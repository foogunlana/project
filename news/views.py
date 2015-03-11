from django.shortcuts import render
from stears.permissions import editor
from django.contrib.auth.decorators import user_passes_test

# Create your views here.



@user_passes_test(lambda u: editor(u), login_url='/weal/')
def articles(request):
    return render(request, 'news/articles.html')

@user_passes_test(lambda u: editor(u), login_url='/weal/')
def companies(request):
	return render(request, 'news/companies.html')

@user_passes_test(lambda u: editor(u), login_url='/weal/')
def index(request):
	return render(request, 'news/index.html')