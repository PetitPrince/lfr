import random

from posts.models import Post


def get_biased_hallway_posts(run, viewer_casting, count=3):
    """Return up to `count` random student posts, biased toward the viewer's
    path > house > year > shared keywords (in that priority order).

    Each post gets a base weight of 1.0, with additive bonuses for affinity.
    Posts are then selected via weighted random sampling without replacement.
    """
    posts = list(
        Post.objects.filter(
            run=run,
            is_published=True,
            post_type=Post.PostType.CHARACTER,
            casting__role="student",
        )
        .exclude(casting=viewer_casting)
        .select_related("casting__house", "casting__year", "casting__path")
        .prefetch_related("keywords")
    )

    if not posts:
        return []

    # Collect viewer's keywords for comparison
    viewer_post = Post.objects.filter(
        run=run, casting=viewer_casting, post_type=Post.PostType.CHARACTER,
    ).prefetch_related("keywords").first()

    viewer_keywords = set()
    if viewer_post:
        viewer_keywords = {kw.label.lower() for kw in viewer_post.keywords.all()}

    # Assign weights
    weights = []
    for post in posts:
        w = 1.0
        c = post.casting
        if viewer_casting.path_id and c.path_id == viewer_casting.path_id:
            w += 4.0
        if viewer_casting.house_id and c.house_id == viewer_casting.house_id:
            w += 3.0
        if viewer_casting.year_id and c.year_id == viewer_casting.year_id:
            w += 2.0
        if viewer_keywords:
            post_keywords = {kw.label.lower() for kw in post.keywords.all()}
            if viewer_keywords & post_keywords:
                w += 1.0
        weights.append(w)

    # Weighted sampling without replacement
    selected = []
    remaining = list(range(len(posts)))
    remaining_weights = list(weights)

    for _ in range(min(count, len(posts))):
        chosen_idx = random.choices(range(len(remaining)), weights=remaining_weights, k=1)[0]
        selected.append(posts[remaining[chosen_idx]])
        remaining.pop(chosen_idx)
        remaining_weights.pop(chosen_idx)

    return selected
