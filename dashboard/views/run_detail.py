from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView

from dashboard.forms.run import RunSettingsForm
from dashboard.forms.vocabulary import CustomAttributeForm
from dashboard.mixins import OrganizerRequiredMixin, RunMixin
from runs.models import (
    BloodStatus,
    Club,
    CustomAttributeDefinition,
    House,
    Path,
    TeachingSubject,
    Year,
)

VOCABULARY_MODELS = {
    "houses": House,
    "paths": Path,
    "years": Year,
    "clubs": Club,
    "teaching_subjects": TeachingSubject,
    "blood_statuses": BloodStatus,
}

VOCABULARY_LABELS = {
    "houses": "Houses",
    "paths": "Paths",
    "years": "Years",
    "clubs": "Clubs",
    "teaching_subjects": "Teaching Subjects",
    "blood_statuses": "Blood Statuses",
}


class RunDetailView(RunMixin, DetailView):
    template_name = "dashboard/run_detail.html"
    context_object_name = "run"

    def get_object(self):
        return self.run

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        run = self.run
        ctx["casting_count"] = run.castings.count()
        ctx["claimed_count"] = run.castings.filter(user__isnull=False).count()
        ctx["invite_count"] = run.castings.filter(invite__isnull=False).count()
        ctx["vocabulary_sections"] = [
            {
                "type": vtype,
                "label": VOCABULARY_LABELS[vtype],
                "items": getattr(run, vtype).all(),
            }
            for vtype in VOCABULARY_MODELS
        ]
        ctx["custom_attributes"] = run.custom_attributes.all()
        return ctx


class RunSettingsView(RunMixin, View):
    def get(self, request, slug):
        form = RunSettingsForm(instance=self.run)
        return render(request, "dashboard/run_settings.html", {"form": form, "run": self.run})

    def post(self, request, slug):
        form = RunSettingsForm(request.POST, instance=self.run)
        if form.is_valid():
            form.save()
            return redirect("dashboard:run_detail", slug=self.run.slug)
        return render(request, "dashboard/run_settings.html", {"form": form, "run": self.run})


class VocabularyEditView(RunMixin, View):
    """HTMX view: render checkbox list for a vocabulary type, handle save."""

    def get(self, request, slug, vocab_type):
        model = VOCABULARY_MODELS.get(vocab_type)
        if not model:
            return HttpResponse("Invalid vocabulary type", status=400)
        all_items = model.objects.all()
        selected_ids = set(getattr(self.run, vocab_type).values_list("id", flat=True))
        return render(request, "dashboard/vocabulary/_edit.html", {
            "run": self.run,
            "vocab_type": vocab_type,
            "label": VOCABULARY_LABELS[vocab_type],
            "items": all_items,
            "selected_ids": selected_ids,
        })

    def post(self, request, slug, vocab_type):
        model = VOCABULARY_MODELS.get(vocab_type)
        if not model:
            return HttpResponse("Invalid vocabulary type", status=400)
        selected_ids = request.POST.getlist("items")
        getattr(self.run, vocab_type).set(selected_ids)
        items = getattr(self.run, vocab_type).all()
        return render(request, "dashboard/vocabulary/_chips.html", {
            "run": self.run,
            "vocab_type": vocab_type,
            "label": VOCABULARY_LABELS[vocab_type],
            "items": items,
        })


class VocabularyAddView(RunMixin, View):
    """HTMX view: add a new vocabulary item and check it for this run."""

    def post(self, request, slug, vocab_type):
        model = VOCABULARY_MODELS.get(vocab_type)
        if not model:
            return HttpResponse("Invalid vocabulary type", status=400)
        name = request.POST.get("name", "").strip()
        if name:
            item, _ = model.objects.get_or_create(name=name)
            getattr(self.run, vocab_type).add(item)
        # Re-render the edit form
        all_items = model.objects.all()
        selected_ids = set(getattr(self.run, vocab_type).values_list("id", flat=True))
        return render(request, "dashboard/vocabulary/_edit.html", {
            "run": self.run,
            "vocab_type": vocab_type,
            "label": VOCABULARY_LABELS[vocab_type],
            "items": all_items,
            "selected_ids": selected_ids,
        })


class CustomAttributeListView(RunMixin, View):
    """HTMX view: list custom attributes."""

    def get(self, request, slug):
        attrs = self.run.custom_attributes.all()
        form = CustomAttributeForm()
        return render(request, "dashboard/custom_attrs/_list.html", {
            "run": self.run,
            "custom_attributes": attrs,
            "form": form,
        })

    def post(self, request, slug):
        form = CustomAttributeForm(request.POST)
        if form.is_valid():
            attr = form.save(commit=False)
            attr.run = self.run
            attr.save()
            form = CustomAttributeForm()
        attrs = self.run.custom_attributes.all()
        return render(request, "dashboard/custom_attrs/_list.html", {
            "run": self.run,
            "custom_attributes": attrs,
            "form": form,
        })


class CustomAttributeDeleteView(RunMixin, View):
    """HTMX: delete a custom attribute."""

    def post(self, request, slug, attr_id):
        attr = get_object_or_404(CustomAttributeDefinition, pk=attr_id, run=self.run)
        attr.delete()
        attrs = self.run.custom_attributes.all()
        form = CustomAttributeForm()
        return render(request, "dashboard/custom_attrs/_list.html", {
            "run": self.run,
            "custom_attributes": attrs,
            "form": form,
        })
