from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["contact_email", "discord_username", "facebook_url", "instagram_url"]


class JoinSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    class Meta:
        model = User
        fields = ["email"]

    def clean_password_confirm(self):
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("password_confirm")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        if p1:
            validate_password(p1)
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.PLAYER
        if commit:
            user.save()
        return user
