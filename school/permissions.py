from rest_framework.permissions import BasePermission
from .models import Subject

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class CanCreateLesson(BasePermission):
    def has_permission(self, request, view):
        subject_id = request.data.get('subject')
        return (
            request.user.is_authenticated and
            request.user.role == 'teacher' and
            Subject.objects.filter(id=subject_id, teacher=request.user).exists()
        )
