from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from casting.models import Casting
from dashboard.csv_parser import parse_casting_csv
from dashboard.forms.casting import CastingForm, CSVUploadForm
from dashboard.mixins import RunMixin


class CastingListView(RunMixin, View):
    def get(self, request, slug):
        castings = self.run.castings.select_related(
            "user", "house", "year", "path", "blood_status"
        ).order_by("-created_at")
        return render(request, "dashboard/casting/list.html", {
            "run": self.run,
            "castings": castings,
        })


class CastingCreateView(RunMixin, View):
    def get(self, request, slug):
        form = CastingForm(run=self.run)
        return render(request, "dashboard/casting/form.html", {
            "run": self.run,
            "form": form,
            "is_edit": False,
        })

    def post(self, request, slug):
        form = CastingForm(request.POST, run=self.run)
        if form.is_valid():
            casting = form.save(commit=False)
            casting.run = self.run
            casting.custom_attributes = _extract_custom_attrs(request.POST, self.run)
            casting.save()
            form.save_m2m()
            messages.success(request, f"Casting for {casting.character_name or 'new character'} created.")
            return redirect("dashboard:casting_list", slug=self.run.slug)
        return render(request, "dashboard/casting/form.html", {
            "run": self.run,
            "form": form,
            "is_edit": False,
        })


class CastingEditView(RunMixin, View):
    def get(self, request, slug, casting_id):
        casting = get_object_or_404(Casting, pk=casting_id, run=self.run)
        form = CastingForm(run=self.run, instance=casting)
        return render(request, "dashboard/casting/form.html", {
            "run": self.run,
            "form": form,
            "casting": casting,
            "is_edit": True,
        })

    def post(self, request, slug, casting_id):
        casting = get_object_or_404(Casting, pk=casting_id, run=self.run)
        form = CastingForm(request.POST, run=self.run, instance=casting)
        if form.is_valid():
            casting = form.save(commit=False)
            casting.custom_attributes = _extract_custom_attrs(request.POST, self.run)
            casting.save()
            form.save_m2m()
            messages.success(request, f"Casting for {casting.character_name or 'character'} updated.")
            return redirect("dashboard:casting_list", slug=self.run.slug)
        return render(request, "dashboard/casting/form.html", {
            "run": self.run,
            "form": form,
            "casting": casting,
            "is_edit": True,
        })


class CastingDeleteView(RunMixin, View):
    """HTMX: show confirm dialog, then delete."""

    def get(self, request, slug, casting_id):
        casting = get_object_or_404(Casting, pk=casting_id, run=self.run)
        return render(request, "dashboard/casting/_delete_confirm.html", {
            "run": self.run,
            "casting": casting,
        })

    def post(self, request, slug, casting_id):
        casting = get_object_or_404(Casting, pk=casting_id, run=self.run)
        casting.delete()
        messages.success(request, "Casting deleted.")
        from django.urls import reverse
        response = HttpResponse(status=204)
        response["HX-Redirect"] = reverse("dashboard:casting_list", kwargs={"slug": self.run.slug})
        return response


class CastingRoleFieldsView(RunMixin, View):
    """HTMX: return role-specific form fields when role changes."""

    def get(self, request, slug):
        role = request.GET.get("role", "student")
        casting_id = request.GET.get("casting_id")
        instance = None
        if casting_id:
            instance = Casting.objects.filter(pk=casting_id, run=self.run).first()
        form = CastingForm(run=self.run, role=role, instance=instance)
        return render(request, "dashboard/casting/_role_fields.html", {
            "form": form,
        })


class CSVUploadView(RunMixin, View):
    def get(self, request, slug):
        form = CSVUploadForm()
        return render(request, "dashboard/casting/upload.html", {
            "run": self.run,
            "form": form,
        })


class CSVUploadPreviewView(RunMixin, View):
    """HTMX: parse CSV and return preview table."""

    def post(self, request, slug):
        form = CSVUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, "dashboard/casting/_upload_preview.html", {
                "run": self.run,
                "errors": ["Please provide CSV data."],
            })

        csv_text = form.cleaned_data.get("csv_text", "")
        if not csv_text and form.cleaned_data.get("csv_file"):
            csv_text = form.cleaned_data["csv_file"].read().decode("utf-8-sig")

        if not csv_text.strip():
            return render(request, "dashboard/casting/_upload_preview.html", {
                "run": self.run,
                "errors": ["No CSV data provided."],
            })

        rows = parse_casting_csv(csv_text, self.run)
        request.session["csv_parsed_rows"] = [r.to_dict() for r in rows]

        return render(request, "dashboard/casting/_upload_preview.html", {
            "run": self.run,
            "rows": rows,
            "valid_count": sum(1 for r in rows if r.is_valid),
            "error_count": sum(1 for r in rows if not r.is_valid),
        })


class CSVUploadConfirmView(RunMixin, View):
    """Create castings from session-stored parsed CSV data."""

    def post(self, request, slug):
        parsed_rows = request.session.pop("csv_parsed_rows", [])
        if not parsed_rows:
            messages.error(request, "No CSV data found. Please upload again.")
            return redirect("dashboard:csv_upload", slug=self.run.slug)

        created = 0
        for row_data in parsed_rows:
            if not row_data.get("is_valid"):
                continue
            data = row_data["data"]
            casting = Casting(
                run=self.run,
                role=data.get("role", "student"),
                character_name=data.get("character_name", ""),
                staff_title=data.get("staff_title", ""),
            )
            # Set FK fields by name lookup
            casting.house = _lookup_vocab(self.run.houses, data.get("house"))
            casting.year = _lookup_vocab(self.run.years, data.get("year"))
            casting.path = _lookup_vocab(self.run.paths, data.get("path"))
            casting.blood_status = _lookup_vocab(self.run.blood_statuses, data.get("blood_status"))
            casting.monitor_of_house = _lookup_vocab(self.run.houses, data.get("monitor_of_house"))
            casting.monitor_of_club = _lookup_vocab(self.run.clubs, data.get("monitor_of_club"))
            casting.custom_attributes = data.get("custom_attributes", {})
            casting.save()

            # Set M2M fields
            if data.get("clubs"):
                clubs = self.run.clubs.filter(name__in=data["clubs"])
                casting.clubs.set(clubs)
            if data.get("teaching_subject"):
                casting.teaching_subject = _lookup_vocab(self.run.teaching_subjects, data["teaching_subject"])
                casting.save()

            created += 1

        messages.success(request, f"{created} casting(s) created from CSV.")
        return redirect("dashboard:casting_list", slug=self.run.slug)


def _extract_custom_attrs(post_data, run):
    """Extract custom attribute values from POST data."""
    attrs = {}
    for attr_def in run.custom_attributes.all():
        key = f"custom_{attr_def.pk}"
        if attr_def.attr_type == "boolean":
            attrs[attr_def.name] = key in post_data
        elif attr_def.attr_type == "choice":
            val = post_data.get(key, "")
            if val:
                attrs[attr_def.name] = val
        else:  # text
            val = post_data.get(key, "").strip()
            if val:
                attrs[attr_def.name] = val
    return attrs


def _lookup_vocab(manager, name):
    """Look up a vocabulary item by name, return None if not found."""
    if not name:
        return None
    return manager.filter(name=name).first()
