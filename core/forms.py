# /core/forms.py
from django import forms
from .models import Professor

class DisponibilidadeForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['disponibilidade']

