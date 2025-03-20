from django import forms
from .models import Subject, CustomUser

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['teacher'].queryset = CustomUser.objects.filter(role='teacher')
