from django.contrib import admin
from django.urls import path, include
from stream.views import home 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('', home),  
    path('admin/', admin.site.urls),
    path('stream/', include('stream.urls')),
     path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/', include('stream.urls')), 
]
