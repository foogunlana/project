from django.shortcuts import render
from stears.permissions import editor
from django.contrib.auth.decorators import user_passes_test

# Create your views here.


@user_passes_test(lambda u: editor(u), login_url='/stears/noaccess/')
def home(request):
    context = {"bla": "hello my name is bode"}
    return render(request, 'news/home.html', context)


@user_passes_test(lambda u: editor(u), login_url='/stears/noaccess/')
def article(request):
    context = {"bla": "hello my name is bode"}
    return render(request, 'news/article.html', context)
