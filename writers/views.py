from django.shortcuts import render
from stears.forms import LoginForm, DateForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def home(request):
    login_form = LoginForm()
    return render(request, 'stears/login.html', {'login_form': login_form})
