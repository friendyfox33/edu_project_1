from django import forms
from .models import *

# class GradeSelectionForm(forms.Form):
#     grade = forms.ModelChoiceField(queryset=Grade.objects.filter(is_active=True))