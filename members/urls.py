from django.urls import path
from .views import StudentRegister, LandingView, ProfileView, EditProfile

urlpatterns = [
    path("register/", StudentRegister.as_view(), name="signup"),
    path("", LandingView.as_view(), name="landing"),
    path("profile/<int:pk>", ProfileView.as_view(), name="profile"),
    path("profile/<int:pk>/edit/", EditProfile.as_view(), name="edit-profile"),
]
