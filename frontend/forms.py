from django import forms
from backend.models import Record

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = '__all__'
