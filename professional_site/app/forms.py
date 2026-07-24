from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput, label="")
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "phone", "organization", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 6})}

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Invalid submission.")
        return value
