from django.shortcuts import render
from stears.forms import LoginForm, DateForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def home(request):
    login_form = LoginForm()
    return render(request, 'stears/login.html', {'login_form': login_form})


def test(request):
    if request.method == "POST":
        form = DateForm(request.POST)
        if form.is_valid():
            dob = form.cleaned_data['dob']
            print dob
        else:
            print form.errors
        return HttpResponseRedirect(reverse('test'))
    date_form = DateForm()
    return render(request, 'stears_test.html', {'date_form': date_form})
