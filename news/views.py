from django.shortcuts import render
from stears.utils import mongo_calls
from stears.models import ReportModel
from django.http import HttpRequest, HttpResponse
from utils import summarize
from django.core.cache import cache

import datetime
import json


def article(request, pk):
    pk = int(pk)
    context = {}
    if request.method == 'GET':
        try:
            articles = mongo_calls('migrations')
            article = articles.find_one(
                {'article_id': pk},
                {'headline': 1, 'category': 1, 'writer': 1,
                 'keywords': 1, 'content': 1, 'photo': 1})
            aUri = HttpRequest.build_absolute_uri(request)
            article['par1'] = summarize(article)
            context = {'article': article, 'aUri': aUri}
        except Exception:
            pass

    context['sUri'] = 'http://{}'.format(HttpRequest.get_host(request))
    return render(request, 'news/article.html', context)


def business(request, sector):
    cache_name = 'newscache:{}{}'.format('business', sector)
    cached_index = cache.get(cache_name, None)
    if cached_index:
        return render(request, 'news/business.html', cached_index)
    context = {}
    absolute_url = 'http://{}'.format(HttpRequest.get_host(request))
    if request.method == 'GET':
        try:
            onsite = mongo_calls('onsite')
            context = onsite.find_one({'page': 'b_e', 'sector': sector})
            if context and context.get('main_feature'):
                context['bmf_summary'] = summarize(context['main_feature'])
            else:
                context = {}
            context['sUri'] = absolute_url
            cache.set(cache_name, context, 60*60*24)
        except Exception:
            context['sUri'] = absolute_url

    return render(request, 'news/business.html', context)


def reports(request):
    context = {}
    if request.method == 'GET':
        try:
            reports = ReportModel.objects.all().order_by('week_ending')
            for report in reports:
                d = datetime.datetime.strptime(
                    str(report.week_ending), "%Y-%m-%d")
                report.time_title = "Week ending {}".format(
                                    d.strftime('%B %-d, %Y'))
            context['reports'] = reports
            context['page'] = 'reports'
        except Exception as e:
            print str(e)
    context['sUri'] = 'http://{}'.format(HttpRequest.get_host(request))
    return render(request, 'news/stearsreport.html', context)


def index(request):
    cache_name = 'newscache:index'
    cached_index = cache.get(cache_name, None)
    absolute_url = 'http://{}'.format(HttpRequest.get_host(request))

    if cached_index:
        return render(request, 'news/index.html', cached_index)
    context = {}
    if request.method == 'GET':
        onsite = mongo_calls('onsite')
        articles = mongo_calls('migrations')

        try:
            context = onsite.find_one({'page': 'home'})
            day = str(datetime.datetime.now().weekday())
            col_writer = context['daily_column'].get(day)
            todays_column = articles.find_one({'$query': {
                                               'writer': col_writer,
                                               'category': 'stearsColumn',
                                               'state': 'site_ready'},
                                               '$orderby': {'time': -1}})
            if todays_column:
                writers = mongo_calls('user')
                writer = writers.find_one({'username': col_writer})
                if writer:
                    todays_column['column_title'] = writer.get('column', '')
                dc_summary = summarize(todays_column)
                context['daily_column_summary'] = dc_summary
                context['column'] = todays_column

            context['sUri'] = absolute_url
            cache.set(cache_name, context, 60*60*1)
        except Exception as e:
            context['sUri'] = absolute_url
            print str(e)
    return render(request, 'news/index.html', context)


def top_picks(request):
    responseData = {}
    if request.method == 'GET':
        onsite = mongo_calls('onsite')
        try:
            top_picks = onsite.find_one({'page': 'home'},
                                        {'main_feature': 1, 'secondary': 1,
                                         'tertiaries': {'$slice': 1}, '_id': 0})
            top_picks['tertiaries'] = top_picks['tertiaries'][0]
            top_picks = [{'headline': a['headline'],
                          'article_id': a['article_id'],
                          'par1': a['par1']} for a in top_picks.values()]
            responseData['articles'] = top_picks
            responseData['success'] = True
        except Exception as e:
            responseData['success'] = False
            responseData['message'] = str(e)
    return HttpResponse(json.dumps(responseData))


def features(request):
    responseData = {}
    if request.method == 'GET':
        o = mongo_calls('onsite')
        try:
            for a in o.find_one({'page': 'home'}, {'features': 1})['features']:
                responseData['articles'] = responseData.get(
                    'articles', []) + [{
                        'headline': a['headline'], 'writer': a['writer'],
                        'photo': a['photo'], 'article_id': a['article_id']}]
            responseData['success'] = True
        except Exception as e:
            responseData['success'] = False
            responseData['message'] = str(e)
    return HttpResponse(json.dumps(responseData))


def related_articles(request, pk):
    pk = int(pk)
    responseData = {}
    if request.method == 'GET':
        m = mongo_calls('migrations')
        try:
            tags = m.find_one({'article_id': pk},
                              {'keywords': 1, '_id': 0})['keywords']
            picks = [s for s in m.find(
                {'posted': {'$exists': 1},
                 'keywords': {'$elemMatch': {'$in': tags}}},
                {'keywords': 1, 'article_id': 1, '_id': 0,
                 'headline': 1})]

            f = lambda a: 1. - 1./(len(set(a['keywords']) & set(tags))+1)
            for article in picks:
                article['f'] = f(article)
            responseData['articles'] = sorted(picks, key=f, reverse=True)
            responseData['success'] = True
        except Exception as e:
            responseData['success'] = False
            responseData['message'] = str(e)
    return HttpResponse(json.dumps(responseData))
