from django import forms

from runs.models import CustomAttributeDefinition


class CustomAttributeForm(forms.ModelForm):
    class Meta:
        model = CustomAttributeDefinition
        fields = ["name", "attr_type", "choices", "applies_to", "is_filterable", "sort_order"]
        widgets = {
            "choices": forms.TextInput(attrs={"placeholder": "e.g. [\"Option A\", \"Option B\"]"}),
        }
