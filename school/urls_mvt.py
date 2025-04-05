from django.urls import path
from .views import *

urlpatterns = [
    
    path('login/', LoginView.as_view(), name='login'),
        path('student/detail/', StudentDetail.as_view(), name='student_detail'),
    path('subject-details/<int:pk>/', SubjectDetail.as_view(), name='subject_detail'),
    path('lesson-details/<int:pk>/', LessonDetail.as_view(), name='lesson_detail'),
    path('teacher-subjects/', TeacherSubjects.as_view(), name='teacher-subjects'),
]