from django import forms

from casting.models import Casting


class CastingForm(forms.ModelForm):
    class Meta:
        model = Casting
        fields = [
            "role", "character_name", "house", "year", "path",
            "clubs", "blood_status", "teaching_subjects",
            "monitor_of_house", "monitor_of_club", "staff_title",
        ]

    def __init__(self, *args, run=None, **kwargs):
        super().__init__(*args, **kwargs)
        if run:
            self.fields["house"].queryset = run.houses.all()
            self.fields["year"].queryset = run.years.all()
            self.fields["path"].queryset = run.paths.all()
            self.fields["clubs"].queryset = run.clubs.all()
            self.fields["blood_status"].queryset = run.blood_statuses.all()
            self.fields["teaching_subjects"].queryset = run.teaching_subjects.all()
            self.fields["monitor_of_house"].queryset = run.houses.all()
            self.fields["monitor_of_club"].queryset = run.clubs.all()

            # Add custom attribute fields
            for attr_def in run.custom_attributes.all():
                field_key = f"custom_{attr_def.pk}"
                if attr_def.attr_type == "boolean":
                    self.fields[field_key] = forms.BooleanField(
                        label=attr_def.name, required=False,
                    )
                elif attr_def.attr_type == "choice":
                    choices = [("", "---")] + [(c, c) for c in (attr_def.choices or [])]
                    self.fields[field_key] = forms.ChoiceField(
                        label=attr_def.name, choices=choices, required=False,
                    )
                else:
                    self.fields[field_key] = forms.CharField(
                        label=attr_def.name, required=False,
                    )

                # Pre-fill from instance
                if self.instance and self.instance.pk:
                    stored = self.instance.custom_attributes or {}
                    val = stored.get(attr_def.name)
                    if val is not None:
                        self.initial[field_key] = val


class CSVUploadForm(forms.Form):
    csv_text = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "placeholder": "Paste CSV here..."}),
        required=False,
    )
    csv_file = forms.FileField(required=False)

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("csv_text") and not cleaned.get("csv_file"):
            raise forms.ValidationError("Please paste CSV text or upload a file.")
        return cleaned
