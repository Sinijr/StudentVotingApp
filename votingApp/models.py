from django.db import models
from members.models import Student
from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_video(file):
    if not file.name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        raise ValidationError("Only video files are allowed.")
    
scope_list = [
    ("department", "Departmental"),
    ("faculty", "Faculty"),
    ("school", "SRA"),
]

class Election(models.Model):
    title = models.CharField(max_length=200, verbose_name="Election Title")
    scope = models.CharField(max_length=500, choices=scope_list, default="school")
    department = models.CharField(max_length=100, null=True, blank=True, choices=Student.department_list)
    faculty = models.CharField(max_length=100, null=True, blank=True, choices=Student.faculty_list)
    description = models.TextField(blank=True, verbose_name="Description")
    start_date = models.DateTimeField(verbose_name="Start Date")
    end_date = models.DateTimeField(verbose_name="End Date")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Election"
        verbose_name_plural = "Elections"
        ordering = ["-start_date"]
        
    def save(self, *args, **kwargs):
        now = timezone.now()
        if self.start_date <= now <= self.end_date:
            self.is_active = True    
        super().save(*args, **kwargs)
    
    def clean(self):
        super().clean()
        if self.scope == "school":
            if self.department or self.faculty:
                raise ValidationError("SRA elections cannot have faculty or department.")             
        elif self.scope == "faculty":
            if not self.faculty:
                raise ValidationError({"faculty": "Faculty election must have a faculty."})
            if self.department:
                raise ValidationError({"department": "Faculty election cannot have a department."})
            if Election.objects.filter(faculty=self.faculty, is_active=True).exclude(pk=self.pk).exists():
                raise ValidationError('a faculty cant have two elections active at the sametime')

        elif self.scope == "department":
            if not self.department:
                raise ValidationError({"department": "Departmental election must have a department."})

            if not self.faculty: 
                raise ValidationError({"faculty":"Departmental election must have a faculty."})
            allowed_departments = Student.department_map.get(self.faculty, [])
            if self.department not in allowed_departments:
                raise ValidationError({"department": f"{self.department} does not belong in the faculty of {self.faculty}."})        

    def __str__(self):
        return f"{self.title} | {self.scope} | {self.start_date.strftime('%Y-%m-%d')}"

class Position(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="positions")
    title = models.CharField(max_length=200)
    
    def clean(self):
        if not self.election.is_active:
            raise ValidationError(f"{self.election} is not active at the moment")
        if Position.objects.filter(election=self.election, title=self.title).exclude(pk=self.pk).exists():
            raise ValidationError("this position has already been created")


    def __str__(self):
        return f"{self.title} | {self.election.title}"

class Candidate(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="candidate_profile")
    manifesto = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    video = models.FileField(null=True, blank=True, upload_to="videos/", validators=[validate_video])
    positions = models.ManyToManyField(Position, through="Candidacy")
    ig_url = models.CharField(max_length=500, blank=True, null=True)
    x_url = models.CharField(max_length=500, blank=True, null=True)
    snap_url = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return str(self.student)

class Candidacy(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, editable=False, null=True, blank=True)
    date_registered = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate} | {self.position}"
    
    
    def save(self):
        if self.position:
            self.election = self.position.election
        return super().save()
    
    def clean(self):
        # if not self.position.election.is_active:
        #     raise ValidationError(f"{self.position.election} is not active at the moment")
        if Candidacy.objects.filter(candidate=self.candidate, position__title=self.position.title).exclude(pk=self.pk).exists():
            raise ValidationError(f"you cannot run for {self.position.title} in two different election")
        
        if self.position and not self.election:
            self.election = self.position.election
        
        if Candidacy.objects.filter(candidate=self.candidate, election=self.position.election).exclude(pk=self.pk).exists():
            raise ValidationError(f"{self.candidate.student.name} is already contesting in this election.")
        
        if self.election.scope == "department":
            if self.candidate.student.department != self.election.department:
                 raise ValidationError(f"only candidates from the department of {self.election.department.upper()} can run for this post or election")

        elif self.election.scope == "faculty":
            if self.candidate.student.faculty != self.election.faculty:
                raise ValidationError(f"Only students from faculty of {self.election.faculty.upper()} can contest in this election.")

        elif self.election.scope == "school":
            pass
    @property
    def vote_count(self):
        return self.vote_set.Count()

    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "position"],
                name="candidacy_constraints"
            ),
            models.UniqueConstraint(
                fields=["candidate", "election"],
                name="election_constraints"
            )
        ]
        verbose_name="Candidacy"
        

class Vote(models.Model):
    voter = models.ForeignKey(Student, on_delete=models.CASCADE)
    voting_for = models.ForeignKey(Candidacy, on_delete=models.CASCADE)

    def clean(self):
        super().clean()
        if not self.voting_for_id:
            return  
        position = self.voting_for.position
        election = self.voting_for.election
        
        # if Vote.objects.filter(
        #     voter=self.voter,
        #     voting_for__position=self.voting_for.position,
        #     voting_for__election=self.voting_for.election
        # ).exclude(pk=self.pk).exists():
        #     raise ValidationError(
        #         f"You have already voted for {self.voting_for.candidate.student.name} as {self.voting_for.position}."

        #     )

        existing_vote = Vote.objects.filter(
            voter=self.voter,
            voting_for__position=position,
            voting_for__election=election
        ).exclude(pk=self.pk).first() 

        if existing_vote:
            raise ValidationError(
                f"You have already voted for {existing_vote.voting_for.candidate.student.name} as {position}."
            )
        if election.scope == "faculty" and self.voter.faculty != election.faculty:
            raise ValidationError(f"Only students from {election.faculty} can vote in this election.")
        if election.scope == "department" and self.voter.department != election.department:
            raise ValidationError(f"Only students from {election.department} can vote in this election.")

    @property
    def vote_stats(self):
        num_of_vote = self.vote_set.count()
        num_of_voters = self.election.vote_set.values('voter').distinct().count()    
        return num_of_vote, num_of_voters    
    
    

    def __str__(self):
        if self.voting_for_id:
            return f"{self.voter} voted for {self.voting_for.candidate} ({self.voting_for.position}) in {self.voting_for.election}"
        return f"{self.voter} has not voted yet"