from django.contrib import admin
from .models import Candidacy, Candidate, Election, Position, Vote
from members.models import Student

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ("id","title", "scope", "is_active", "start_date", "end_date")

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("title", "election")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "election":
            kwargs["queryset"] = Election.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Candidacy)
class CandidacyAdmin(admin.ModelAdmin):
    list_display = ("candidate", "position")

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "election":
    #         kwargs["queryset"] = Election.objects.filter(is_active=True)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("student", "manifesto")

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("voter", "voting_for")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "voting_for":
            qs_school = Candidacy.objects.filter(election__scope="school")
            qs_faculty = Candidacy.objects.none()
            qs_department = Candidacy.objects.none()

            if Student.faculty:
                qs_faculty = Candidacy.objects.filter(
                    election__scope="faculty",
                    election__faculty=Student.faculty
                )

            if Student.faculty and Student.department:
                qs_department = Candidacy.objects.filter(
                    election__scope="department",
                    election__faculty=Student.faculty,
                    election__department=Student.department
                )

        # Combine all
            qs = qs_school | qs_faculty | qs_department
            kwargs["queryset"] = qs
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)





#to hide the election field from admin
# @admin.register(Candidacy)
# class CandidacyAdmin(admin.ModelAdmin):
#     exclude = ("election",)