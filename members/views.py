from django.views.generic import CreateView, TemplateView, DetailView, UpdateView
from django.urls import reverse_lazy
from .models import Student
from votingApp.models import Candidacy
from .forms import StudentForm, StudentEditForm
from django.shortcuts import get_object_or_404


class StudentRegister(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

class LandingView(TemplateView):
    model = Candidacy
    template_name = "registration/index.html"
    
class ProfileView(DetailView):
    model = Student
    template_name = "registration/profile.html"
    context_object_name = "student"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        student = self.object        
        candidacy = (Candidacy.objects.filter(candidate__student=student))
        context["candidacy"] = candidacy
        return context
        

class EditProfile(UpdateView):
    model = Student
    form_class = StudentEditForm
    context_object_name = "student"
    template_name = "registration/editprofile.html"
    success_url = reverse_lazy("home")
    
        
        
