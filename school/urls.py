from django.urls import path
from .views import *

urlpatterns = [
    path('student/detail/', StudentDetailView.as_view(), name='student_detail'),
    path('subject-details/<int:pk>/', SubjectDetailView.as_view(), name='subject_detail'),
    path('lesson-details/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('teacher-subjects/', TeacherSubjectsView.as_view(), name='teacher-subjects'),
    path('lessons/create/', CreateLessonView.as_view(), name='create-lesson'),
    path('lessons/<int:lesson_id>/process/', ProcessLessonView.as_view(), name='process-lesson'),
    path("test-process/", testLessonView.as_view(), name="mock-process"),
    path('result/<str:task_id>/', get_result),
    path('add/', trigger_add),
    path('trigger_speech/<int:pk>',trigger_speech_rec.as_view())
]
