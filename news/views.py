from django.shortcuts import render
from stears.permissions import editor
from django.contrib.auth.decorators import user_passes_test
from utils import HomePage, BusinessPage, EconomyPage, \
Article

# Create your views here.



@user_passes_test(lambda u: editor(u), login_url='/weal/')
def articles(request):
    return render(request, 'news/articles.html')

@user_passes_test(lambda u: editor(u), login_url='/weal/')
def business(request):
	return render(request, 'news/business.html')

@user_passes_test(lambda u: editor(u), login_url='/weal/')
def index(request):
	return render(request, 'news/index.html')

@user_passes_test(lambda u: editor(u), login_url='/weal/')
def economy(request):
	return render(request, 'news/economy.html')