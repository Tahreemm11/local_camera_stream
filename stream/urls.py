# stream/urls.py
from django.urls import path
from .views import home, camera_feed
from .api_views import persons_list
from . import api_views as v

urlpatterns = [
    path('', home, name='home'),                 
    path('camera/', camera_feed, name='camera_feed'), 
    path('api/persons/', persons_list, name='persons_list'), 
    path('webrtc/offer/', v.webrtc_offer),
    path('webrtc/stop/', v.webrtc_stop),
    path('emotions/search/', v.emotion_search_view),
    path("persons/", persons_list, name="persons_list"),
]
