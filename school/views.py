from rest_framework import generics, permissions
from .models import CustomUser, Subject, Lesson
from .serializers import StudentSerializer, SubjectSerializer, LessonSerializer, SubjectDetailSerializer
from .permissions import IsStudent, IsTeacher, CanCreateLesson


class StudentDetailView(generics.RetrieveAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_object(self):
        return self.request.user


class Lessons(generics.ListAPIView):
    serializer_class = SubjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        subject_id = self.kwargs.get('subject_id')
        return Subject.objects.filter(id=subject_id)


class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]


class TeacherSubjectsView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return Subject.objects.filter(teacher=self.request.user)


class CreateLessonView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreateLesson]
