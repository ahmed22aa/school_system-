# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Grade(models.Model):
    name = models.CharField(max_length=85)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE, default='student')
    profile_picture = models.ImageField(upload_to="user_photos", blank=True, null=True)
    school_id = models.CharField(max_length=12, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, blank=True, null=True , related_name="users")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} - {self.role}"

class Subject(models.Model):
    name = models.CharField(max_length=85)
    description = models.TextField()
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT , related_name="subjects_grades")
    teacher = models.ForeignKey(CustomUser , on_delete=models.PROTECT , related_name="subjects")
    def __str__(self):
        return self.name
    
    
class Lesson(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    file_text = models.FileField(upload_to='lessons/texts/', blank=True, null=True)
    file_audio = models.FileField(upload_to='lessons/audios/', blank=True, null=True)
    video = models.FileField(upload_to='lessons/videos/', blank=True, null=True)
    subject = models.ForeignKey(Subject , on_delete=models.PROTECT , related_name="lessons")
    audio_file_transcribe = models.FileField(upload_to='lessons/transcribe/', blank=True, null=True)
    processed = models.BooleanField(default=False)
    def __str__(self):
        return self.name





