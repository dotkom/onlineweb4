from django import forms
from apps.rutinator.models import Task

class NewTaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = (
            'title', 'description', 'deadline', 'group'
        )
