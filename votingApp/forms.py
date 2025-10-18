from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Candidate,  Candidacy


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ["manifesto", "image", "video", "ig_url", "x_url", "snap_url"]  
        widgets = {
            # "student": forms.Select(attrs={"class":"input", "placeholder":"student"}),
            "manifesto": forms.Textarea(attrs={"class":"textarea", "placeholder":"student"}),
            "image": forms.ClearableFileInput(attrs={"class":"input"}),
            "video": forms.ClearableFileInput(attrs={"class":"input"}),
            "ig_url":forms.TextInput(attrs={"class": "input", "placeholder": "Add Snapchat link"}),
            "x_url":forms.TextInput(attrs={"class": "input", "placeholder": "Add Snapchat link"}),
            "snap_url":forms.TextInput(attrs={"class": "input", "placeholder": "Add Snapchat link"}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        ig_url = cleaned_data.get("ig_url")
        x_url = cleaned_data.get("x_url")
        snap_url = cleaned_data.get("snap_url")

        if not ig_url or x_url or snap_url:
            forms.ValidationError("atleast one social media need to be added")

        return cleaned_data


class CandidacyForm(forms.ModelForm):
    class Meta:
        model = Candidacy
        fields = ["candidate", "position"] 
        widgets = {
            "candidate": forms.Select(attrs={"class":"input"}),
            "position": forms.Select(attrs={"class":"input"}),
        }
