# stream/urls.py
from django.urls import path
from .views import home, camera_feed
from .api_views import persons_list

urlpatterns = [
    path('', home, name='home'),                 
    path('camera/', camera_feed, name='camera_feed'), 
    path('api/persons/', persons_list, name='persons_list'), 
]
