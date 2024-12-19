from django.urls import path
from .views import get_gpt_recommendation,fetch_game_details

urlpatterns = [
    path("gpt-recommendation/", get_gpt_recommendation, name="gpt_recommendation"),
    path("fetch_game_details/", fetch_game_details, name="fetch_game_details"),
]
