from django import forms
from django.core.files.images import get_image_dimensions

from .models import ContactMessage, GalleryCategory


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else [data]
        if not files or files == [None]:
            raise forms.ValidationError("Select at least one image.")
        cleaned = []
        for upload in files:
            try:
                image = super().clean(upload, initial)
                get_image_dimensions(image)
            except forms.ValidationError as exc:
                raise forms.ValidationError(
                    f"{getattr(upload, 'name', 'Selected file')}: {exc.messages[0]}"
                ) from exc
            cleaned.append(image)
        return cleaned


class GalleryBulkUploadForm(forms.Form):
    images = MultipleImageField(help_text="Select multiple JPG, PNG, GIF or WebP images.")
    category = forms.ModelChoiceField(queryset=GalleryCategory.objects.all())
    event_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    location = forms.CharField(max_length=160, required=False)
    caption = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    title_prefix = forms.CharField(max_length=100, required=False)
    publish_immediately = forms.BooleanField(required=False)
    mark_featured = forms.BooleanField(required=False)


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
