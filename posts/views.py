from collections import defaultdict

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from casting.mixins import PlayerRunMixin
from posts.forms import CharacterPostForm, CommentForm, OtherPostForm
from posts.models import Comment, LookingForEntry, Photo, Post, PostKeyword, Rumor
from runs.models import CustomAttributeDefinition, GlobalKeyword, GlobalLookingForLabel


class MessageBoardView(PlayerRunMixin, View):
    def get(self, request, slug):
        posts = (
            Post.objects.filter(run=self.run, is_published=True)
            .select_related("casting__house", "casting__year", "casting__path", "author")
            .prefetch_related("keywords", "photos", "casting__clubs")
            .order_by("-created_at")
        )
        paginator = Paginator(posts, 20)
        page = paginator.get_page(request.GET.get("page"))
        character_post = Post.objects.filter(
            run=self.run, author=request.user, post_type=Post.PostType.CHARACTER
        ).first()
        can_create_character = character_post is None or self.casting.allow_multiple_posts
        return render(request, "player/message_board.html", {
            "run": self.run,
            "casting": self.casting,
            "page_obj": page,
            "character_post": character_post,
            "can_create_character": can_create_character,
        })


class PostExpandView(PlayerRunMixin, View):
    def get(self, request, slug, pk):
        post = get_object_or_404(
            Post.objects.select_related(
                "casting__house", "casting__year", "casting__path",
                "casting__blood_status", "casting__teaching_subject",
                "casting__monitor_of_house", "casting__monitor_of_club",
                "author",
            ).prefetch_related("keywords", "looking_for_entries", "rumors", "photos", "casting__clubs"),
            pk=pk, run=self.run, is_published=True,
        )
        comments = _build_comment_tree(
            Comment.objects.filter(post=post).select_related("author").order_by("created_at")
        )
        return render(request, "player/partials/_post_expanded.html", {
            "post": post,
            "run": self.run,
            "comments": comments,
            "comment_form": CommentForm(),
        })


class PostDetailView(PlayerRunMixin, View):
    def get(self, request, slug, pk):
        post = get_object_or_404(
            Post.objects.select_related(
                "casting__house", "casting__year", "casting__path",
                "casting__blood_status", "casting__teaching_subject",
                "casting__monitor_of_house", "casting__monitor_of_club",
                "author",
            ).prefetch_related("keywords", "looking_for_entries", "rumors", "photos", "casting__clubs"),
            pk=pk, run=self.run, is_published=True,
        )
        comments = _build_comment_tree(
            Comment.objects.filter(post=post).select_related("author").order_by("created_at")
        )
        return render(request, "player/post_detail.html", {
            "post": post,
            "run": self.run,
            "casting": self.casting,
            "comments": comments,
            "comment_form": CommentForm(),
        })


class PostCreateView(PlayerRunMixin, View):
    def _has_character_post(self):
        return Post.objects.filter(
            run=self.run, author=self.request.user, post_type=Post.PostType.CHARACTER
        ).exists()

    def _can_create_character(self):
        return not self._has_character_post() or self.casting.allow_multiple_posts

    def get(self, request, slug):
        post_type = request.GET.get("type", "character")
        if post_type == "character" and not self._can_create_character():
            messages.info(request, "You already have a character introduction. You can edit it instead.")
            existing = Post.objects.get(run=self.run, author=request.user, post_type=Post.PostType.CHARACTER)
            return redirect("posts:post_edit", slug=self.run.slug, pk=existing.pk)
        if post_type == "other":
            form = OtherPostForm(run=self.run)
        else:
            form = CharacterPostForm(casting=self.casting)
        return render(request, "player/post_form.html", {
            "form": form,
            "run": self.run,
            "casting": self.casting,
            "post_type": post_type,
            "editing": False,
        })

    def post(self, request, slug):
        post_type = request.POST.get("post_type", "character")
        if post_type == "other":
            form = OtherPostForm(run=self.run, data=request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.run = self.run
                post.author = request.user
                post.casting = self.casting
                post.post_type = Post.PostType.OTHER
                if post.category != Post.OtherCategory.CLUB_RECRUITMENT:
                    post.club = None
                post.save()
                _save_photos(request, post)
                messages.success(request, "Post created!")
                return redirect("posts:message_board", slug=self.run.slug)
        else:
            if not self._can_create_character():
                messages.error(request, "You already have a character introduction.")
                return redirect("posts:message_board", slug=self.run.slug)
            form = CharacterPostForm(request.POST, casting=self.casting)
            if form.is_valid():
                post = form.save(commit=False)
                post.run = self.run
                post.author = request.user
                post.casting = self.casting
                post.post_type = Post.PostType.CHARACTER
                post.save()
                _save_casting_fields(form, self.casting)
                _save_keywords(request, post)
                _save_looking_for(request, post)
                _save_rumors(request, post)
                _save_photos(request, post)
                messages.success(request, "Character introduction posted!")
                return redirect("posts:message_board", slug=self.run.slug)

        return render(request, "player/post_form.html", {
            "form": form,
            "run": self.run,
            "casting": self.casting,
            "post_type": post_type,
            "editing": False,
        })


class PostEditView(PlayerRunMixin, View):
    def get(self, request, slug, pk):
        post = get_object_or_404(Post, pk=pk, run=self.run, author=request.user)
        post_type = post.post_type
        if post_type == Post.PostType.OTHER:
            form = OtherPostForm(run=self.run, instance=post)
        else:
            form = CharacterPostForm(instance=post, casting=self.casting)
        return render(request, "player/post_form.html", {
            "form": form,
            "run": self.run,
            "casting": self.casting,
            "post_type": post_type,
            "editing": True,
            "post": post,
            "existing_keywords": list(post.keywords.values_list("label", flat=True)),
            "existing_looking_for": list(post.looking_for_entries.values("label", "description")),
            "existing_rumors": list(post.rumors.values_list("text", flat=True)),
        })

    def post(self, request, slug, pk):
        post = get_object_or_404(Post, pk=pk, run=self.run, author=request.user)
        post_type = post.post_type
        if post_type == Post.PostType.OTHER:
            form = OtherPostForm(run=self.run, data=request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                if post.category != Post.OtherCategory.CLUB_RECRUITMENT:
                    post.club = None
                post.save()
                _delete_photos(request, post)
                _save_photos(request, post)
                messages.success(request, "Post updated!")
                return redirect("posts:post_detail", slug=self.run.slug, pk=post.pk)
        else:
            form = CharacterPostForm(request.POST, instance=post, casting=self.casting)
            if form.is_valid():
                post = form.save()
                _save_casting_fields(form, self.casting)
                post.keywords.all().delete()
                post.looking_for_entries.all().delete()
                post.rumors.all().delete()
                _save_keywords(request, post)
                _save_looking_for(request, post)
                _save_rumors(request, post)
                _delete_photos(request, post)
                _save_photos(request, post)
                messages.success(request, "Post updated!")
                return redirect("posts:post_detail", slug=self.run.slug, pk=post.pk)

        return render(request, "player/post_form.html", {
            "form": form,
            "run": self.run,
            "casting": self.casting,
            "post_type": post_type,
            "editing": True,
            "post": post,
        })


class PostDeleteView(PlayerRunMixin, View):
    def post(self, request, slug, pk):
        post = get_object_or_404(Post, pk=pk, run=self.run, author=request.user)
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("posts:message_board", slug=self.run.slug)


class CommentCreateView(PlayerRunMixin, View):
    def post(self, request, slug, pk):
        post = get_object_or_404(Post, pk=pk, run=self.run, is_published=True)
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                post=post,
                author=request.user,
                body=form.cleaned_data["body"],
            )
        comments = _build_comment_tree(
            Comment.objects.filter(post=post).select_related("author").order_by("created_at")
        )
        return render(request, "player/partials/_comment_thread.html", {
            "comments": comments,
            "post": post,
            "run": self.run,
            "comment_form": CommentForm(),
        })


class CommentReplyView(PlayerRunMixin, View):
    def get(self, request, slug, pk, comment_id):
        post = get_object_or_404(Post, pk=pk, run=self.run, is_published=True)
        parent = get_object_or_404(Comment, pk=comment_id, post=post)
        return render(request, "player/partials/_comment_form.html", {
            "post": post,
            "run": self.run,
            "parent": parent,
            "comment_form": CommentForm(),
        })

    def post(self, request, slug, pk, comment_id):
        post = get_object_or_404(Post, pk=pk, run=self.run, is_published=True)
        parent = get_object_or_404(Comment, pk=comment_id, post=post)
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                post=post,
                parent=parent,
                author=request.user,
                body=form.cleaned_data["body"],
            )
        comments = _build_comment_tree(
            Comment.objects.filter(post=post).select_related("author").order_by("created_at")
        )
        return render(request, "player/partials/_comment_thread.html", {
            "comments": comments,
            "post": post,
            "run": self.run,
            "comment_form": CommentForm(),
        })


class DiscoverFacultyView(PlayerRunMixin, View):
    def get(self, request, slug):
        posts = (
            Post.objects.filter(
                run=self.run,
                is_published=True,
                post_type=Post.PostType.CHARACTER,
                casting__role__in=["professor", "staff", "headmaster"],
            )
            .select_related(
                "casting__house", "casting__teaching_subject",
                "casting__monitor_of_house", "casting__monitor_of_club",
                "author",
            )
            .prefetch_related("photos")
        )
        return render(request, "player/discover/faculty.html", {
            "run": self.run,
            "casting": self.casting,
            "posts": posts,
        })


class DiscoverStudentsView(PlayerRunMixin, View):
    def get(self, request, slug):
        custom_attrs = CustomAttributeDefinition.objects.filter(
            run=self.run, is_filterable=True,
        ).filter(Q(applies_to="student") | Q(applies_to="all"))
        # Pass through any initial filter params (used by links from post detail)
        initial_filters = {
            k: v for k, v in request.GET.items() if v
        }
        return render(request, "player/discover/students.html", {
            "run": self.run,
            "casting": self.casting,
            "houses": self.run.houses.all(),
            "years": self.run.years.all(),
            "paths": self.run.paths.all(),
            "clubs": self.run.clubs.all(),
            "blood_statuses": self.run.blood_statuses.all(),
            "custom_attrs": custom_attrs,
            "initial_filters": initial_filters,
        })


class StudentFilterView(PlayerRunMixin, View):
    def get(self, request, slug):
        posts = Post.objects.filter(
            run=self.run,
            is_published=True,
            post_type=Post.PostType.CHARACTER,
            casting__role="student",
        ).select_related(
            "casting__house", "casting__year", "casting__path",
            "casting__blood_status", "author",
        ).prefetch_related("keywords", "photos")

        # Apply filters
        house = request.GET.get("house")
        year = request.GET.get("year")
        path = request.GET.get("path")
        club = request.GET.get("club")
        blood = request.GET.get("blood_status")
        keyword = request.GET.get("keyword")
        q = request.GET.get("q", "").strip()

        if house:
            posts = posts.filter(casting__house_id=house)
        if year:
            posts = posts.filter(casting__year_id=year)
        if path:
            posts = posts.filter(casting__path_id=path)
        if club:
            posts = posts.filter(casting__clubs__id=club)
        if blood:
            posts = posts.filter(casting__blood_status_id=blood)
        if keyword:
            posts = posts.filter(keywords__label__iexact=keyword)

        # Custom attribute filters
        for key, val in request.GET.items():
            if key.startswith("custom_") and val:
                attr_id = key.replace("custom_", "")
                try:
                    attr = CustomAttributeDefinition.objects.get(pk=attr_id, run=self.run, is_filterable=True)
                    if attr.attr_type == "boolean":
                        posts = posts.filter(casting__custom_attributes__contains={attr.name: True})
                    else:
                        posts = posts.filter(casting__custom_attributes__contains={attr.name: val})
                except (CustomAttributeDefinition.DoesNotExist, ValueError):
                    pass

        if q:
            posts = posts.filter(
                Q(casting__character_name__icontains=q)
                | Q(content__icontains=q)
                | Q(looking_for_entries__label__icontains=q)
                | Q(looking_for_entries__description__icontains=q)
            ).distinct()

        posts = posts.order_by("-created_at")

        return render(request, "player/partials/_student_results.html", {
            "posts": posts,
            "run": self.run,
        })


class StudentRandomView(PlayerRunMixin, View):
    def get(self, request, slug):
        from posts.hallway import get_biased_hallway_posts

        posts = get_biased_hallway_posts(self.run, self.casting, count=3)

        return render(request, "player/partials/_hallway_widget.html", {
            "posts": posts,
            "run": self.run,
        })


class DiscoverOtherView(PlayerRunMixin, View):
    def get(self, request, slug):
        posts = Post.objects.filter(
            run=self.run,
            is_published=True,
            post_type=Post.PostType.OTHER,
        ).select_related("author", "club").order_by("-created_at")

        category = request.GET.get("category")
        if category:
            posts = posts.filter(category=category)

        if request.htmx:
            return render(request, "player/partials/_other_results.html", {
                "posts": posts,
                "run": self.run,
            })

        return render(request, "player/discover/other.html", {
            "run": self.run,
            "casting": self.casting,
            "posts": posts,
            "categories": Post.OtherCategory.choices,
            "initial_category": request.GET.get("category", ""),
        })


# --- Helpers ---

def _save_casting_fields(form, casting):
    casting.character_name = form.cleaned_data["character_name"]
    casting.blood_status = form.cleaned_data["blood_status"]
    casting.save(update_fields=["character_name", "blood_status"])
    casting.clubs.set(form.cleaned_data.get("clubs", []))

def _build_comment_tree(comments):
    tree = []
    children_map = defaultdict(list)
    for c in comments:
        c.children = []
        if c.parent_id:
            children_map[c.parent_id].append(c)
        else:
            tree.append(c)
    # Assign children recursively
    def _assign(nodes):
        for node in nodes:
            node.children = children_map.get(node.pk, [])
            _assign(node.children)
    _assign(tree)
    return tree


def _save_keywords(request, post):
    raw = request.POST.get("keywords", "")
    labels = [l.strip() for l in raw.split(",") if l.strip()]
    for label in labels:
        PostKeyword.objects.create(post=post, label=label)
        GlobalKeyword.objects.get_or_create(label=label)


def _save_looking_for(request, post):
    labels = request.POST.getlist("lf_label")
    descriptions = request.POST.getlist("lf_description")
    for i, (label, desc) in enumerate(zip(labels, descriptions)):
        label = label.strip()
        if label:
            LookingForEntry.objects.create(post=post, label=label, description=desc.strip(), sort_order=i)
            GlobalLookingForLabel.objects.get_or_create(label=label)


def _save_rumors(request, post):
    texts = request.POST.getlist("rumor_text")
    for i, text in enumerate(texts):
        text = text.strip()
        if text:
            Rumor.objects.create(post=post, text=text, sort_order=i)


def _delete_photos(request, post):
    ids = request.POST.getlist("delete_photos")
    if ids:
        post.photos.filter(pk__in=ids).delete()


ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_PHOTOS_PER_POST = 20


def _save_photos(request, post):
    files = request.FILES.getlist("photos")
    existing_count = post.photos.count()
    remaining_slots = MAX_PHOTOS_PER_POST - existing_count
    for i, f in enumerate(files[:remaining_slots]):
        ext = "." + f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
        if ext not in ALLOWED_PHOTO_EXTENSIONS:
            messages.warning(request, f"Skipped {f.name}: only JPEG, PNG, GIF, and WebP are allowed.")
            continue
        if f.size > MAX_PHOTO_SIZE:
            messages.warning(request, f"Skipped {f.name}: file exceeds 10 MB limit.")
            continue
        Photo.objects.create(post=post, image=f, sort_order=existing_count + i)
