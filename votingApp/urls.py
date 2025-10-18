from django.urls import path
from .views import HomeView, ElectionView, CandidateView, CandidateListView, CastVoteView, HometoVote, ResultView, IndividualResultView, RunForElection, BecomeCandidate


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("election/", ElectionView.as_view(), name="election"),
    path("candidates/", CandidateView.as_view(), name="candidates"),
    path("election/candidates_election/<int:pk>", CandidateListView.as_view() , name="candidates-election"),
    path("vote/<int:candidacy_id>/", CastVoteView.as_view(), name="vote"),
    path("home/candidates/<int:pk>", HometoVote.as_view(), name="home-to-vote"),
    path("results/", ResultView.as_view(), name="results"),
    path("candidates_election/results/<int:pk>", IndividualResultView.as_view() , name="election-results"),
    path("run-for-post/", RunForElection.as_view(), name="create-candidacy"),
    path("become_a_candidate/<int:pk>", BecomeCandidate.as_view(), name="become-candidate"),
]
