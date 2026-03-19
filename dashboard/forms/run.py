from django import forms
from django.utils.text import slugify

from runs.models import Run


class RunCreateForm(forms.ModelForm):
    class Meta:
        model = Run
        fields = ["name", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
        help_texts = {
            "name": "e.g. \"College of Wizardry 27: Wintertide\"",
        }

    def clean_name(self):
        name = self.cleaned_data["name"]
        slug = slugify(name)
        if not slug:
            raise forms.ValidationError("Name must contain at least one letter or number.")
        # Ensure unique slug
        base_slug = slug
        counter = 2
        while Run.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self._generated_slug = slug
        return name

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = self._generated_slug
        if commit:
            instance.save()
        return instance


class RunSettingsForm(forms.ModelForm):
    class Meta:
        model = Run
        fields = ["name", "start_date", "end_date", "is_active"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
