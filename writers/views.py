from django.shortcuts import render
from stears.forms import LoginForm, DateForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def home(request):
    login_form = LoginForm()
    return render(request, 'stears/login.html', {'login_form': login_form})


def test(request):
    import urllib2
    import re

    site = urllib2.urlopen('http://www.cenbank.org/').read()

    pat = r'dtb">\s*\b(.*)\s*</div>\s*<div\s*class="dtbR">\s*[&#8358;]*(.*\W?\d+)</div>'

    m = re.findall(pat, site)

    site = {}
    for group in m:
        site[group[0]] = group[1]

    if request.method == "POST":
        form = DateForm(request.POST)
        if form.is_valid():
            dob = form.cleaned_data['dob']
            print dob
        else:
            print form.errors
        return HttpResponseRedirect(reverse('test'))
    date_form = DateForm()
    return render(request, 'stears_test.html', {'date_form': date_form, 'site': site})
