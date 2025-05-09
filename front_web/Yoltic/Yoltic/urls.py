from django.contrib import admin
from django.urls import path, include
from front import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('front.urls')),
]
