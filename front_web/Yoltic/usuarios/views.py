from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from .decorators import group_required
from django.shortcuts import redirect
from django.contrib.auth import login
from django.utils.http import url_has_allowed_host_and_scheme
# Create your views here.


class Login(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)  
        if user.groups.filter(name='Operadores').exists():
            return redirect('operacion')
        elif user.groups.filter(name='Visualizadores').exists():
            return redirect('visualizacion')
        else:
            return redirect('login')
