from django.shortcuts import render
from stears.forms import LoginForm


def home(request):
    login_form = LoginForm()
    return render(request, 'stears/login.html', {'login_form': login_form})
