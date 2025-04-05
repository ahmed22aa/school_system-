from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Grade, Subject, Lesson
from .forms import SubjectForm
from django.urls import path
from django.shortcuts import render, redirect
from django.db import transaction
import pandas as pd



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

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    change_list_template = "admin/customuser_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-csv/", self.upload_csv, name="upload_csv"),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                self.message_user(request, "No file uploaded.", level=messages.ERROR)
                return redirect("..")

            try:
                # Read CSV file
                df = pd.read_csv(csv_file)

                required_columns = {"username", "email", "role", "school_id", "grade", "password"}
                if not required_columns.issubset(set(df.columns)):
                    self.message_user(request, f"Missing required columns: {required_columns}", messages.ERROR)
                    return redirect("..")

                # Grade lookup by name (case-insensitive)
                grade_map = {g.name.lower(): g for g in Grade.objects.all()}

                users = []
                for row in df.itertuples(index=False):
                    grade_name = str(getattr(row, "grade")).lower().strip()
                    grade = grade_map.get(grade_name)

                    if not grade:
                        self.message_user(request, f"Grade '{grade_name}' not found. Skipping user {getattr(row, 'email')}", messages.WARNING)
                        continue

                    user = CustomUser(
                        username=getattr(row, "username"),
                        email=getattr(row, "email"),
                        role=getattr(row, "role"),
                        school_id=getattr(row, "school_id"),
                        grade=grade,
                    )
                    user.set_password(getattr(row, "password"))
                    users.append(user)

                with transaction.atomic():
                    CustomUser.objects.bulk_create(users)

                self.message_user(request, f"Successfully uploaded {len(users)} users.", messages.SUCCESS)
                return redirect("..")

            except Exception as e:
                self.message_user(request, f"Upload failed: {str(e)}", messages.ERROR)
                return redirect("..")

        return render(request, "admin/upload_csv.html")

#admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Grade)
admin.site.register(Lesson)  
