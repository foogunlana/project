from django.shortcuts import render
from stears.permissions import editor
from stears.utils import mongo_calls
from django.contrib.auth.decorators import user_passes_test
from utils import HomePage, BusinessPage, EconomyPage, \
Article, htmltag_text, remove_special_characters



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
    main_feature = context['main_feature']
    bmf_summary = htmltag_text(main_feature['content'], 'p')
    bmf_summary = remove_special_characters(bmf_summary.pop())
    context['bmf_summary'] = bmf_summary
    return render(request, 'news/business.html', context)


@user_passes_test(lambda u: editor(u), login_url='/weal/')
def economy(request):
    onsite = mongo_calls('onsite')
    context = onsite.find_one({'page': 'economy'})
    main_feature = context['main_feature']
    emf_summary = htmltag_text(main_feature['content'], 'p')
    emf_summary = remove_special_characters(emf_summary.pop())
    context['emf_summary'] = emf_summary
    return render(request, 'news/economy.html', context)


@user_passes_test(lambda u: editor(u), login_url='/weal/')
def index(request):
    onsite = mongo_calls('onsite')
    context = onsite.find_one({'page': 'home'})
    daily_column = context['daily_column']
    dc_summary = htmltag_text(daily_column['content'], 'p')
    dc_summary = remove_special_characters(dc_summary.pop())
    context['daily_column_summary'] = dc_summary
    return render(request, 'news/index.html', context)
