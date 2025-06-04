from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
     # Vista de login (generalmente en views.py como Login(View))
    path('', views.Login.as_view(), name='login'),

    # Logout con redirección automática al login
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
