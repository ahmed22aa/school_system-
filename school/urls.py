from django.urls import path
from .views import *

urlpatterns = [
    path('student-data/', StudentDetailView.as_view(), name='student-data'),
    path('subjects-details/<int:id>/', Lessons.as_view(), name='lesson'),
    path('lessons-details/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('subjects/', TeacherSubjectsView.as_view(), name='teacher-subjects'),
    path('lessons/create/', CreateLessonView.as_view(), name='create-lesson'),
]
