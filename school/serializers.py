from rest_framework import serializers
from .models import CustomUser, Grade, Subject, Lesson


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name']

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'school_id','email', 'profile_picture']
        
        
class SubjectSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer()

    class Meta:
        model = Subject
        fields = [ 'teacher' , 'id', 'name', 'description', 'grade' ]


class StudentSerializer(serializers.ModelSerializer):
    grade = GradeSerializer()
    subjects = SubjectSerializer(many=True, source='grade.subject_set')


    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'profile_picture' , 'school_id', 'role', 'grade', 'subjects']


class LessonSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), write_only=True
    )
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'name', 'description', 'file_text', 'file_audio', 'video', 'subject', 'subject_name']
        
class SubjectDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'grade', 'lessons']




