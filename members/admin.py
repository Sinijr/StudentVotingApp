# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student
from .forms import StudentForm

class StudentAdmin(UserAdmin):
    model = Student
    add_form = StudentForm
    form = StudentForm

    list_display = ["matNo", "name", "email", "department", "faculty", "is_staff"]
    ordering = ["matNo"]

    fieldsets = (
        (None, {"fields": ("matNo", "password")}),
        ("Personal info", {"fields": ("name", "email", "department", "faculty")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("matNo", "name", "email", "department", "faculty", "password1", "password2"),
        }),
    )
    
    # readonly_fields = ("faculty",) 

admin.site.register(Student, StudentAdmin)
