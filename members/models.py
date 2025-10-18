from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models


class StudentManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, matNo, email, name, department, password=None, **extra_fields):
        if not matNo:
            raise ValueError("The Matriculation Number must be set")
        if not email:
            raise ValueError("The Email must be set")

        email = self.normalize_email(email)
        user = self.model(
            matNo=matNo,
            email=email,
            name=name,
            department=department,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matNo, email, name, department, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(matNo, email, name, department, password, **extra_fields)


class Student(AbstractUser):
    faculty_list = [
    ("education", "College of Education"),
    ("theology", "Ecclesiastical Faculty of Theology"),
    ("engineering", "Faculty of Engineering"),
    ("health_sciences", "Faculty of Health Sciences"),
    ("humanities", "Faculty of Humanities"),
    ("law", "Faculty of Law"),
    ("management_sciences", "Faculty of Management Sciences"),
    ("medical_sciences", "Faculty of Medical Sciences"),
    ("natural_applied_sciences", "Faculty of Natural & Applied Sciences"),
    ("pharmaceutical_sciences", "Faculty of Pharmaceutical Sciences"),
    ("social_sciences", "Faculty of Social Sciences"),
]

    department_list = [
        # Education
        ("biology_education", "Biology Education"),
        ("business_education", "Business Education"),
        ("chemistry_education", "Chemistry Education"),
        ("computer_science_education", "Computer Science Education"),
        ("economics_education", "Economics Education"),
        ("educational_management", "Educational Management"),
        ("english_education", "English Education"),
        ("guidance_and_counseling", "Guidance And Counseling"),
        ("library_and_information_science", "Library And Information Science"),
        ("physics_education", "Physics Education"),
        ("religious_education", "Religious Education"),
        ("social_studies_education", "Social Studies Education"),

        # Theology
        ("sacred_theology", "Sacred Theology"),
        ("theology", "Theology"),

        # Engineering
        ("beng_computer_engineering", "B.Eng Computer Engineering"),
        ("beng_electrical_electronic_engineering", "B.Eng Electrical & Electronic Engineering"),

        # Health Sciences
        ("medical_laboratory_sciences", "Medical Laboratory Sciences"),
        ("nursing", "Nursing"),

        # Humanities
        ("english_literary_studies", "English & Literary Studies"),
        ("history_international_relations", "History & International Relations"),
        ("philosophy", "Philosophy"),
        ("religious_studies", "Religious Studies"),
        ("sacred_philosophy", "Sacred Philosophy"),

        # Law
        ("law", "Law"),
        ("public_international_law", "Public & International Law"),

        # Management Sciences
        ("accounting", "Accounting"),
        ("banking_finance", "Banking & Finance"),
        ("business_administration", "Business Administration"),
        ("entrepreneurial_studies", "Entrepreneurial Studies"),
        ("marketing_advertising", "Marketing & Advertising"),
        ("public_administration", "Public Administration"),

        # Medical Sciences
        ("anatomy", "Anatomy"),
        ("medicine_and_surgery", "Medicine and Surgery"),
        ("physiology", "Physiology"),

        # Natural & Applied Sciences
        ("applied_mathematics", "Applied Mathematics"),
        ("applied_microbiology", "Applied Microbiology"),
        ("biochemistry", "Biochemistry"),
        ("botany", "Botany"),
        ("computer_science", "Computer Science"),
        ("industrial_chemistry", "Industrial Chemistry"),
        ("physics_electronics", "Physics with Electronics"),
        ("software_engineering", "Software Engineering"),
        ("zoology", "Zoology"),

        # Pharmaceutical Sciences
        ("pharmacy", "Pharmacy"),

        # Social Sciences
        ("economics", "Economics"),
        ("mass_communication", "Mass Communication"),
        ("peace_conflict_studies", "Peace and Conflict Studies"),
        ("political_science_diplomacy", "Political Science & Diplomacy"),
    ]

    department_map = {
    "education": [
        "biology_education", "business_education", "chemistry_education",
        "computer_science_education", "economics_education",
        "educational_management", "english_education",
        "guidance_and_counseling", "library_and_information_science",
        "physics_education", "religious_education", "social_studies_education",
    ],

    # Ecclesiastical Faculty of Theology
    "theology": [
        "sacred_theology", "theology"
    ],

    # Engineering
    "engineering": [
        "beng_computer_engineering", "beng_electrical_electronic_engineering",
    ],

    # Health Sciences
    "health_sciences": [
        "medical_laboratory_sciences", "nursing",
    ],

    # Humanities
    "humanities": [
        "english_literary_studies", "history_international_relations",
        "philosophy", "religious_studies", "sacred_philosophy",
    ],

    # Law
    "law": ["law", "public_international_law"],

    # Management Sciences
    "management_sciences": [
        "accounting", "banking_finance", "business_administration",
        "entrepreneurial_studies", "marketing_advertising",
        "public_administration",
    ],

    # Medical Sciences
    "medical_sciences": ["anatomy", "medicine_and_surgery", "physiology"],

    # Natural and Applied Sciences
    "natural_applied_sciences": [
        "applied_mathematics", "applied_microbiology", "biochemistry",
        "botany", "computer_science", "industrial_chemistry",
        "physics_electronics", "software_engineering", "zoology",
    ],

    # Pharmaceutical Sciences
    "pharmaceutical_sciences": ["pharmacy"],

    # Social Sciences
    "social_sciences": [
        "economics", "mass_communication", "peace_conflict_studies",
        "political_science_diplomacy",
    ],
}

    username = None
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=200, choices=department_list)
    faculty = models.CharField(max_length=200, choices=faculty_list)
    matNo = models.CharField(max_length=100, unique=True)

    USERNAME_FIELD = "matNo"
    REQUIRED_FIELDS = ["name", "email", "department", "faculty"]
    
    objects=StudentManager()
    
    def department_display(self, words=2):
        return " ".join(self.department.replace("_", " ").title().split()[:words])

    def faculty_display(self, words=2):
        return " ".join(self.faculty.replace("_", " ").title().split()[:words])

    def clean(self):
        super().clean()
        allowed_departments = self.department_map.get(self.faculty, [])
        if self.department not in allowed_departments:
            raise ValidationError({
                "department": f"{self.department} does not belong in the faculty of {self.faculty}."
            })

    def __str__(self):
        return f"{self.name} ({self.matNo})"

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
