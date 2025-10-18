from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import Student  


class StudentForm(UserCreationForm):
    class Meta:
        model = Student
        fields = ["name", "email", "department", "faculty", "matNo", "password1", "password2"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input", "placeholder": "Name"}),
            "email": forms.EmailInput(attrs={"class": "input", "placeholder": "Email"}),
            "department": forms.Select(attrs={"class": "input", "placeholder":"Department"}),
            "faculty": forms.Select(attrs={"class": "input", "placeholder":"Faculty"}),
            "matNo": forms.TextInput(attrs={"class": "input", "placeholder": "Matric No"}),
            "password1": forms.PasswordInput(attrs={"class": "input", "placeholder": "Password"}),
            "password2": forms.PasswordInput(attrs={"class": "input", "placeholder": "Confirm Password"}),
        }


class StudentLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Matric No",
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Matric No"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Password"})
    )
    
class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "email", "department", "faculty", "matNo",]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input", "placeholder": "Name"}),
            "email": forms.EmailInput(attrs={"class": "input", "placeholder": "Email"}),
            "department": forms.Select(attrs={"class": "input", "placeholder":"Department"}),
            "faculty": forms.Select(attrs={"class": "input", "placeholder":"Faculty"}),
            "matNo": forms.TextInput(attrs={"class": "input", "placeholder": "Matric No"}),
        }
