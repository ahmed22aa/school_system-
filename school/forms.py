from django import forms
from .models import Subject, CustomUser, Lesson
from django.contrib.auth.forms import AuthenticationForm
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['teacher'].queryset = CustomUser.objects.filter(role='teacher')


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'name', 'description', 'file_text', 'file_audio',
            'video', 'subject', 'audio_file_transcribe'
        ]