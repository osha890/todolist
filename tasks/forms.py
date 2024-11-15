from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date']  # Добавьте необходимые поля
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class DayDateForm(forms.Form):
    day_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='',
        required=False
    )
