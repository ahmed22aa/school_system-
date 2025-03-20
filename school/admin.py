from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Grade, Subject, Lesson
from .forms import SubjectForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'role', 'school_id', 'grade', 'profile_picture')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'role', 'school_id', 'grade', 'profile_picture')


class SubjectAdmin(admin.ModelAdmin):
    form = SubjectForm


admin.site.register(Subject, SubjectAdmin)  # ✅ Only once, using SubjectForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('email', 'username', 'role', 'school_id', 'grade', 'is_staff')
    list_filter = ('role', 'grade')
    ordering = ('email',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'role', 'school_id', 'grade', 'profile_picture', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('role', 'school_id', 'grade', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Grade)
admin.site.register(Lesson)  
