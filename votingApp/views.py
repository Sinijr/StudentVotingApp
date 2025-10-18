from django.views.generic import ListView, TemplateView, DetailView, View, CreateView
from members.models import Student
from .models import Election, Position, Candidacy, Vote, Candidate
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count
from .forms import CandidateForm, CandidacyForm
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import re


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        elections = Election.objects.prefetch_related("candidacy_set", "positions")
        context["candidacy"] = Candidacy.objects.all()
             
        
        for election in elections:
            election.has_candidates = election.candidacy_set.exists()
            election.first_position = election.positions.first()
        context["elections"] = elections
        return context
    

class HometoVote(ListView):
    model = Vote
    template_name = "home.html"
    context_object_name = "vote"
    

class ElectionView(ListView):
    model = Position
    template_name = "election.html"
    
    
class CandidateView(ListView):
    model = Candidacy
    template_name = "candidates.html"
    
    def get_queryset(self):
        user = self.request.user

        qs_school = Candidacy.objects.filter(election__scope="school")
        qs_faculty = Candidacy.objects.none()
        qs_department = Candidacy.objects.none()

        if hasattr(user, "faculty") and user.faculty:
            qs_faculty = Candidacy.objects.filter(
                election__scope="faculty",
                election__faculty=user.faculty
            )

        if hasattr(user, "department") and user.department:
            qs_department = Candidacy.objects.filter(
                election__scope="department",
                election__faculty=user.faculty,
                election__department=user.department
            )

        a = qs_school | qs_faculty | qs_department
        return a.order_by("-election__scope")
    


    
    
    
class CandidateListView(ListView):
    model = Candidacy
    template_name = "candidates.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        position = get_object_or_404(Position, pk=self.kwargs["pk"])
        context["position"] = position               
        context["election"] = position.election    
        
        for candidacy in context["object_list"]:
            student = candidacy.candidate.student
            department = student.department.replace("_", " ").title()
            faculty = student.faculty.replace("_", " ").title()
            student.department_display = " ".join(department.split()[:2])
            student.faculty_display = " ".join(faculty.split()[:2])

        return context   

    def get_queryset(self):
        user = self.request.user
        position_pk = self.kwargs.get("pk", None)

        if position_pk:  
            position = get_object_or_404(Position, pk=position_pk)
            return Candidacy.objects.filter(position=position)


        qs_school = Candidacy.objects.filter(election__scope="school")
        qs_faculty = Candidacy.objects.none()
        qs_department = Candidacy.objects.none()

        if hasattr(user, "faculty") and user.faculty:
            qs_faculty = Candidacy.objects.filter(
                election__scope="faculty",
                election__faculty=user.faculty
            )

        if hasattr(user, "department") and user.department:
            qs_department = Candidacy.objects.filter(
                election__scope="department",
                election__faculty=user.faculty,
                election__department=user.department
            )

        return qs_school | qs_faculty | qs_department


class CastVoteView(View):
    def post(self, request, candidacy_id):
        candidacy = get_object_or_404(Candidacy, pk=candidacy_id)
        voter = request.user  

        try:
            vote = Vote(voter=voter, voting_for=candidacy)
            vote.full_clean()
            vote.save()
            messages.success(request, "Your vote has been cast successfully!")
        except ValidationError as e:
            if 'voter' in e.message_dict or 'voting_for' in e.message_dict:
                messages.error(request, "You have already voted for this position.")
            else:
                messages.error(request, " ".join(e.messages))
        except IntegrityError:
            messages.error(request, "You have already voted for this position.")
        except Exception:
            messages.error(request, "An unexpected error occurred. Please try again.")

        return redirect("candidates-election", pk=candidacy.position.pk)
    
    
class ResultView(ListView):
    model = Vote
    template_name = "result.html"
    context_object_name = "votes"
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        results = (
            Candidacy.objects
            .annotate(total_count=Count("vote"))
            .order_by("-election__scope", "election__title", "position__title", "-total_count")
        )

        context["results"] = results
        context["num_of_vote"] = Vote.objects.count()
        context["num_of_voters"] = Vote.objects.values("voter").distinct().count()
        return context



class IndividualResultView(DetailView):
    model = Position
    template_name = "result.html"
    context_object_name = "position"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        position_pk = self.kwargs.get("pk")
        
        position = get_object_or_404(Position, pk=position_pk)
        candidacies = (
            Candidacy.objects
            .filter(position=position)
            .annotate(total_count=Count("vote"))
            .select_related("position", "candidate__student", "election")
            .order_by("position__title", "-total_count")
        )

        context["results"] = candidacies
        context["labels"] = [c.candidate.student.name for c in candidacies]
        context["data"] = [c.total_count for c in candidacies]
        return context
    
   
class BecomeCandidate(CreateView):
    model = Candidate
    form_class = CandidateForm
    template_name = "contest.html"
    success_url = reverse_lazy("home")
    
    def form_valid(self, form):
        student_pk = self.kwargs.get("pk")
        student = get_object_or_404(Student, pk=student_pk)
        form.instance.student = student
        try:
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, "You are already a candidate.")
            return self.form_invalid(form)


class RunForElection(CreateView):
    model = Candidacy
    form_class = CandidacyForm
    template_name = "runforelection.html"
    success_url = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'candidate_profile'):
            return redirect('become-candidate', pk=request.user.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['candidate'].queryset = Candidate.objects.filter(student=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.candidate = self.request.user.candidate_profile
        return super().form_valid(form)
    
