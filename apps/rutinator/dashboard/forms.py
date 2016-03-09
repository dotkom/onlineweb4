from apps.rutinator.models import Task
from django import forms


class NewTaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = (
            'title', 'description', 'deadline', 'group'
        )
