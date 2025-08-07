from django.contrib import admin
from django.urls import path, include
from stream.views import home  

urlpatterns = [
    path('', home),  
    path('admin/', admin.site.urls),
    path('stream/', include('stream.urls')),
]
