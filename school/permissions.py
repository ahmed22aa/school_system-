from rest_framework.permissions import BasePermission
from .models import Subject , Lesson
from django.http import HttpResponseForbidden



def check_user_permission(user, subject_id):
    
    subject = Subject.objects.filter(id=subject_id).first()

    if not subject:
        return HttpResponseForbidden("Subject not found.")

   
    if subject.teacher == user:
        return None  

    
    if user.role == 'student' and subject.grade == user.grade:
        return None  

    return HttpResponseForbidden("You do not have permission to view this subject.")


def check_student_permission(user):
    if user.role != 'student':
        return HttpResponseForbidden("You do not have permission to view this page.")
    return None


def check_teacher_permission(user):
    if user.role != 'teacher':
        return HttpResponseForbidden("You do not have permission to view this page.")
    return None


# APIS

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

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
    
    
    
class CanViewLesson(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'teacher':
            return obj.subject.teacher == user
        if user.role == 'student':
            return obj.subject.grade == user.grade
        return False    



from rest_framework.permissions import BasePermission
from django.http import HttpResponseForbidden
from .models import Subject

class UserCheckPermission(BasePermission):
    """
    Custom permission to allow access based on user role (teacher or student)
    and their relationship with the subject (teacher of the subject or student in the grade).
    """

    def has_permission(self, request, view):
        
        subject_id = view.kwargs.get("pk")  
        if not subject_id:
            return False  
        
        
        subject = Subject.objects.filter(id=subject_id).first()
        if not subject:
            return False  
        
        
        if subject.teacher == request.user:
            return True  
        
        
        if request.user.role == 'student' and subject.grade == request.user.grade:
            return True  
        
        
        return False
