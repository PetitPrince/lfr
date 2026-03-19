from django import forms

from posts.models import Post


class CharacterPostForm(forms.ModelForm):
    character_name = forms.CharField(max_length=300)
    blood_status = forms.ModelChoiceField(queryset=None, required=False)
    keywords = forms.CharField(required=False, help_text="Comma-separated keywords")
    looking_for_labels = forms.CharField(required=False, widget=forms.HiddenInput)
    looking_for_descriptions = forms.CharField(required=False, widget=forms.HiddenInput)
    rumors = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Post
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10, "placeholder": "Write about your character..."}),
        }

    def __init__(self, *args, casting=None, **kwargs):
        super().__init__(*args, **kwargs)
        if casting:
            self.fields["character_name"].initial = casting.character_name
            self.fields["blood_status"].initial = casting.blood_status_id
            self.fields["blood_status"].queryset = casting.run.blood_statuses.all()
        else:
            from runs.models import BloodStatus
            self.fields["blood_status"].queryset = BloodStatus.objects.none()


class OtherPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "category", "content", "club"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
            "category": forms.Select(attrs={"hx-get": "", "hx-target": "#club-field", "hx-swap": "outerHTML"}),
        }

    def __init__(self, run=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["category"].required = True
        if run:
            self.fields["club"].queryset = run.clubs.all()
        self.fields["club"].required = False


class CommentForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Write a comment..."}))
