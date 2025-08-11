from django.urls import path
from .views import camera_feed, home

urlpatterns = [
    path('', home, name='home'),              # Home page
    path('camera/', camera_feed, name='camera_feed'),  # Camera feed
]
