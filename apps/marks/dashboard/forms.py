from django import forms

from apps.marks.models import Mark


class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ["title", "weight", "description", "category"]
