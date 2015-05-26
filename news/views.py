from django.shortcuts import render
from stears.permissions import editor
from stears.utils import mongo_calls
from django.contrib.auth.decorators import user_passes_test
from utils import HomePage, BusinessPage, EconomyPage, \
Article



# Create your views here.


@user_passes_test(lambda u: editor(u), login_url='/weal/')
def article(request, pk):
    pk = int(pk)
    articles = mongo_calls('migrations')

    article = articles.find_one({'article_id': pk})
    if not article:
        articles = mongo_calls('articles')
        article = articles.find_one({'article_id': pk})
    context = {'article': article}
    return render(request, 'news/article.html', context)


@user_passes_test(lambda u: editor(u), login_url='/weal/')
def business(request):
    onsite = mongo_calls('onsite')
    context = onsite.find_one({'page': 'business'})
    return render(request, 'news/business.html', context)


@user_passes_test(lambda u: editor(u), login_url='/weal/')
def economy(request):
    onsite = mongo_calls('onsite')
    context = onsite.find_one({'page': 'economy'})
    return render(request, 'news/economy.html', context)


@user_passes_test(lambda u: editor(u), login_url='/weal/')
def index(request):
    onsite = mongo_calls('onsite')
    context = onsite.find_one({'page': 'home'})
    return render(request, 'news/index.html', context)
