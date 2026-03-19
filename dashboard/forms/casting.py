from django import forms

from casting.models import Casting

SHARED_FIELDS = ["role", "character_name"]

STUDENT_FIELDS = ["house", "year", "path", "clubs", "blood_status"]
PROFESSOR_FIELDS = ["teaching_subjects", "monitor_of_house", "monitor_of_club"]
STAFF_FIELDS = ["staff_title"]

ROLE_FIELDS = {
    "student": STUDENT_FIELDS,
    "professor": PROFESSOR_FIELDS,
    "staff": STAFF_FIELDS,
    "headmaster": STAFF_FIELDS,
}


class CastingForm(forms.ModelForm):
    class Meta:
        model = Casting
        fields = [
            "role", "character_name", "house", "year", "path",
            "clubs", "blood_status", "teaching_subjects",
            "monitor_of_house", "monitor_of_club", "staff_title",
        ]

    def __init__(self, *args, run=None, role=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.run = run

        # Determine active role
        if role:
            active_role = role
        elif self.instance and self.instance.pk:
            active_role = self.instance.role
        else:
            active_role = self.data.get("role", "student") if self.data else "student"

        self.active_role = active_role

        if run:
            self.fields["house"].queryset = run.houses.all()
            self.fields["year"].queryset = run.years.all()
            self.fields["path"].queryset = run.paths.all()
            self.fields["clubs"].queryset = run.clubs.all()
            self.fields["blood_status"].queryset = run.blood_statuses.all()
            self.fields["teaching_subjects"].queryset = run.teaching_subjects.all()
            self.fields["monitor_of_house"].queryset = run.houses.all()
            self.fields["monitor_of_club"].queryset = run.clubs.all()

            # Add custom attribute fields (filtered by role)
            for attr_def in run.custom_attributes.all():
                if attr_def.applies_to != "all" and attr_def.applies_to != active_role:
                    continue
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

        # Remove fields not relevant to the active role
        visible_fields = set(SHARED_FIELDS + ROLE_FIELDS.get(active_role, []))
        for field_name in list(self.fields):
            if field_name.startswith("custom_"):
                continue  # already filtered above
            if field_name not in visible_fields:
                del self.fields[field_name]

    def role_specific_fields(self):
        """Return only the role-specific fields (excludes role and character_name)."""
        for field in self:
            if field.name not in SHARED_FIELDS:
                yield field


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
