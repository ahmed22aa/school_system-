from rest_framework.permissions import BasePermission
from .models import Subject , Lesson

class CanViewLesson(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'teacher':
            return obj.subject.teacher == user
        if user.role == 'student':
            return obj.subject.grade == user.grade
        return False

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
        

class CanProcessLesson(BasePermission):
    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.role == 'teacher'):
            return False

        lesson_id = view.kwargs.get('lesson_id')

        return Lesson.objects.filter(id=lesson_id, subject__teacher=request.user).exists()