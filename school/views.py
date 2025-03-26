from rest_framework import generics, permissions, serializers
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, Subject, Lesson
from .serializers import StudentSerializer, SubjectSerializer, LessonSerializer, SubjectDetailSerializer
from .permissions import IsStudent, IsTeacher, CanCreateLesson , CanViewLesson


class StudentDetailView(generics.RetrieveAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_object(self):
        return self.request.user


class Lessons(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"  


class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated , CanViewLesson] # add permission to make sure that this student can c this lesson 
    

class TeacherSubjectsView(generics.ListAPIView): # test this API
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get_queryset(self):
        queryset = Subject.objects.filter(teacher=self.request.user)
        if not queryset.exists():
            raise NotFound(detail="No subjects found for this teacher.")
        return queryset



class CreateLessonView(generics.CreateAPIView): 
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreateLesson]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to allow authentication using either email or school_id.
    """

    username_field = "email"  # Keep compatibility with Django authentication

    def validate(self, attrs):
        username = attrs.get("email")  # The default key in Simple JWT is "email"
        password = attrs.get("password")

        # Try authenticating with email or school_id
        user = CustomUser.objects.filter(email=username).first() or \
               CustomUser.objects.filter(school_id=username).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError({"error": "Invalid credentials."})

        # Generate tokens
        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "school_id": user.school_id
            }
        }

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view to authenticate using email or school_id.
    """
    serializer_class = CustomTokenObtainPairSerializer

