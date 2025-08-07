from django.urls import path
from .views import camera_stream

urlpatterns = [
    path('camera/', camera_stream, name='camera-stream'),
]
