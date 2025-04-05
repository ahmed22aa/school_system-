from django.conf import settings
import requests
from rest_framework import generics, permissions, serializers , status
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import add_numbers, speech_rec
from django_celery_results.models import TaskResult
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import CustomUser, Subject, Lesson
from .serializers import StudentSerializer, SubjectSerializer, LessonSerializer, SubjectDetailSerializer
from .permissions import check_student_permission,  CanCreateLesson , CanViewLesson , CanProcessLesson , check_teacher_permission , check_user_permission , \
    IsTeacher , IsStudent , UserCheckPermission
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.views.generic import DetailView , TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Lesson, Subject
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm
from django.http import HttpResponseForbidden






class StudentDetail(LoginRequiredMixin, TemplateView):
    template_name = 'school/student_detail.html'

    def dispatch(self, request, *args, **kwargs):
        
        permission_response = check_student_permission(self.request.user)
        if permission_response:
            return permission_response  
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        student = self.request.user
        grade = student.grade
        subjects = Subject.objects.filter(grade=grade)

        context.update({
            'student': student,
            'grade': grade,
            'subjects': subjects
        })
        
        return context

class SubjectDetail(DetailView, LoginRequiredMixin):
    model = Subject
    template_name = 'school/subject_detail.html'
    context_object_name = 'subject'

    def dispatch(self, request, *args, **kwargs):
        
        subject = self.get_object()

        
        permission_error = check_user_permission(request.user, subject.id)
        if permission_error:
            return HttpResponseForbidden("You are not authorized to be here.")  

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = context['subject']

        
        context['grade'] = subject.grade
        context['lessons'] = subject.lessons.all()

        return context
    
    
class LessonDetail(DetailView, LoginRequiredMixin):
    model = Lesson
    template_name = 'school/lesson_detail.html'
    context_object_name = 'lesson'

    def dispatch(self, request, *args, **kwargs):
        
        lesson = self.get_object()

        
        permission_error = check_user_permission(request.user, lesson.subject.id)
        if permission_error:
            return HttpResponseForbidden("You are not authorized to be here.")  

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()

        subject = lesson.subject

        
        context['subject'] = subject
        context['subject_name'] = subject.name

        return context


class TeacherSubjects(LoginRequiredMixin, TemplateView):
    template_name = 'school/teacher_subjects.html'

    def dispatch(self, request, *args, **kwargs):
        
        permission_response = check_teacher_permission(self.request.user)
        if permission_response:
            return permission_response
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user
        
        subjects = Subject.objects.filter(teacher=teacher)
        
        context.update({
            'teacher': teacher,
            'subjects': subjects,
        })
        
        return context



class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'school/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            
            user = authenticate(username=email, password=password)

            if user is not None:
                login(request, user)

                
                if user.role == 'teacher':
                    return redirect('teacher-subjects')  
                elif user.role == 'student':
                    return redirect('student_detail')  
                else:
                    messages.error(request, 'Invalid role assigned to user.')
                    return redirect('login')  
            else:
                messages.error(request, 'Invalid email or password.')
                return redirect('login')  

        
        return render(request, 'school/login.html', {'form': form})
    
# APIS

class LessonDetailView(APIView):
    permission_classes = [IsAuthenticated, CanViewLesson]  

    def get(self, request, pk):  
        lesson = get_object_or_404(Lesson, pk=pk)  

        
        self.check_object_permissions(request, lesson)

        
        serializer = LessonSerializer(lesson)
        return Response(serializer.data)
    


class StudentDetailView(generics.RetrieveAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_object(self):
        return self.request.user
    
    
class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated , UserCheckPermission]
    lookup_field = "pk"  



class TeacherSubjectsView(generics.ListAPIView): 
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
    
    
    
class ProcessLessonView(APIView):
    permission_classes = [IsAuthenticated, CanProcessLesson]

    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)

            if lesson.processed:
                return Response({"message": "Lesson already processed"}, status=status.HTTP_400_BAD_REQUEST)

            if not lesson.file_text:
                return Response({"error": "No file associated with this lesson"}, status=status.HTTP_400_BAD_REQUEST)

            rag_system_url = "http://127.0.0.1:8000/api/test-process/"

            
            payload = {"lesson_id": lesson.id}
            files = {"file": lesson.file_text}  

            response = requests.post(rag_system_url, dat=payload, files=files)
            print(response.status_code,"####################################")
            if response.status_code == 200:
                lesson.processed = True
                lesson.save()
                return Response({"message": "Lesson processed successfully"}, status=status.HTTP_200_OK)

            return Response({"error": "Failed to process lesson"}, status=response.status_code)

        except Exception as e:
            print(e)
            return Response({"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)
        
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


def trigger_add(request):
    task = add_numbers.delay(10, 5)
    return JsonResponse({'task_id': task.id})

class trigger_speech_rec(APIView):

    # authentication_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk, format=None):
        """
        Return a list of all users.
        """
        lesson = get_object_or_404(Lesson, pk=pk)
        task = speech_rec.delay(lesson.id)
        return JsonResponse({'task_id': task.id})



def get_result(request, task_id):
    try:
        task = TaskResult.objects.get(task_id=task_id)
        return JsonResponse({
            "status": task.status,
            "result": task.result
        })
    except TaskResult.DoesNotExist:
        return JsonResponse({"error": "Task ID not found"}, status=404)
    
    
class testLessonView(APIView):
    def post(self, request):
        print("STAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAART")
        lesson_id = request.data.get("lesson_id")


        if not lesson_id :
            return Response({"error": "Missing lesson_id or file"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "File received successfully", "lesson_id": lesson_id}, status=status.HTTP_200_OK)


    def get(self,request):
        return Response({"message":"hi"})