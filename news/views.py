from django.shortcuts import render
from stears.utils import mongo_calls
from stears.models import ReportModel, ProfileImageModel
from stears import params
from django.http import HttpRequest, HttpResponse, Http404
from utils import summarize
from django.core.cache import cache
from datetime import datetime

from django.contrib.auth.decorators import user_passes_test
from stears.permissions import is_columnist, approved_writer

import json


def column(request, column_id, pk=None):

    cache_name = 'newscache:{}{}-{}'.format(
        'opinion', column_id, pk if pk else '')

    icache = 'infinitecache:{}{}-{}'.format(
        'opinion', column_id, pk if pk else '')

    response = cache.get(cache_name, None)
    if response:
        return response

    context = {}
    column_id = int(column_id)
    articles = mongo_calls('migrations')
    onsite = mongo_calls('onsite')

    if request.method == 'GET':

        column_page = onsite.find_one({'page': 'opinion', 'column_id': column_id})
        if not column_page:
            raise Http404("Sorry, we can't find that page")

        try:
            photo = ProfileImageModel.objects.get(pk=column_page.get('photo'))
            if photo:
                column_page['photo'] = photo.docfile.url

            articles = list(articles.find({
                                'query': {
                                    'writer': column_page.get('writer'),
                                    'category': 'stearsColumn'},
                                'orderby': {'time': -1}}))

            if len(articles) < 2:
                context = {
                    'column': column_page,
                    'first_visit': True,
                    'aUri': HttpRequest.build_absolute_uri(request),
                }
            else:
                if pk:
                    pk = int(pk)
                    func = lambda a: a.get('article_id') == pk
                    article = filter(func, articles)[0]
                    articles.remove(article)
                    first_visit = False
                else:
                    article, articles = articles[0], articles[1:]
                    first_visit = True

                context = {
                    'article': article,
                    'first_visit': first_visit,
                    'preview': '</p>'.join(article.get('content').split('</p>')[:3]),
                    'others': articles,
                    'column': column_page,
                    'aUri': HttpRequest.build_absolute_uri(request),
                }


            response = render(request, 'news/column.html', context)
            cache.set(cache_name, response, 60*60*12)
            cache.set(icache, response, 60*60*24*14)
            return response

        except Exception:

            response = cache.get(icache, None)
            return response
        


def article(request, pk):
    cache_name = 'newscache:{}{}'.format('article', str(pk))
    icache = 'infinitecache:{}{}'.format('article', str(pk))

    response = cache.get(cache_name, None)
    if response:
        return response

    pk = int(pk)
    context = {}
    if request.method == 'GET':
        try:
            articles = mongo_calls('migrations')
            article = articles.find_one(
                {'article_id': pk},
                {'headline': 1, 'category': 1, 'writer': 1, 'summary': 1,
                 'keywords': 1, 'content': 1, 'photo': 1, 'posted': 1})
            aUri = HttpRequest.build_absolute_uri(request)
            try:
                article['posted'] = datetime.fromtimestamp(
                    article['posted'])
            except Exception:
                pass
            if article.get('summary'):
                article['par1'] = article['summary']
            else:
                article['par1'] = summarize(article)

            context = {'article': article, 'aUri': aUri}
            context['sUri'] = 'http://{}'.format(HttpRequest.get_host(request))

            response = render(request, 'news/article.html', context)
            cache.set(cache_name, response, 60*60*24)
            cache.set(icache, response, 60*60*24*14)
            return response
        except Exception:
            # Log exception
            response = cache.get(icache, None)
            return response

    context['sUri'] = 'http://{}'.format(HttpRequest.get_host(request))
    response = render(request, 'news/article.html', context)
    return response


def business(request, sector):
    cache_name = 'newscache:{}{}'.format('business', sector)
    icache = 'infinitecache:{}{}'.format('business', sector)

    response = cache.get(cache_name, None)
    # if response:
    #     return response

    context = {}
    absolute_url = 'http://{}'.format(HttpRequest.get_host(request))
    if request.method == 'GET':
        try:
            onsite = mongo_calls('onsite')
            context = onsite.find_one({'page': 'b_e', 'sector': sector})
            context['sUri'] = absolute_url
            context['meta_description'] = params.meta_descriptions['b_e'][sector]

            response = render(request, 'news/business.html', context)
            cache.set(cache_name, response, 60*60*24)
            cache.set(icache, response, 60*60*24*14)
            return response
        except Exception:
            # Log exception
            response = cache.get(icache, None)
            return response

    context['sUri'] = absolute_url
    response = render(request, 'news/business.html', context)
    return response


def reports(request):
    context = {}
    if request.method == 'GET':
        try:
            reports = ReportModel.objects.all().order_by('week_ending')
            for report in reports:
                d = datetime.strptime(
                    str(report.week_ending), "%Y-%m-%d")
                report.time_title = "Week ending {}".format(
                                    d.strftime('%B %-d, %Y'))
            context['reports'] = reports
            context['meta_description'] = params.meta_descriptions['reports']
            context['page'] = 'reports'
            context['sUri'] = 'http://{}'.format(HttpRequest.get_host(request))

            response = render(request, 'news/stearsreport.html', context)
            icache = 'infinitecache:{}'.format('reports')
            cache.set(icache, response, 60*60*24*14)
            return response
        except Exception:
            response = cache.get(icache, None)
            return response

    context['sUri'] = 'http://{}'.format(HttpRequest.get_host(request))
    response = render(request, 'news/stearsreport.html', context)
    return response


def index(request):
    cache_name = 'newscache:index'
    icache = 'infinitecache:{}'.format('index')

    response = cache.get(cache_name, None)
    if response:
        return response

    context = {}
    absolute_url = 'http://{}'.format(HttpRequest.get_host(request))

    if request.method == 'GET':
        onsite = mongo_calls('onsite')
        articles = mongo_calls('migrations')
        columns = mongo_calls('columns')

        try:
            context = onsite.find_one({'page': 'home'})
            day = str(datetime.now().weekday())
            col_writer = context['daily_column'].get(day)

            feature = articles.find_one({'$query': {
                                           'writer': col_writer,
                                           'category': 'stearsColumn',
                                           'state': 'site_ready'},
                                           '$orderby': {'time': -1}})
            column = columns.find_one({
                                'writer': col_writer,
                                'state': 'active'})
            column['feature'] = feature
            context['column'] = column

            context['sUri'] = absolute_url
            context['meta_description'] = params.meta_descriptions['home']

            response = render(request, 'news/index.html', context)
            cache.set(cache_name, response, 60*60*24)
            cache.set(icache, response, 60*60*24*14)
            return response
        except Exception as e:
            print e
            response = cache.get(icache, None)
            return response

    context['sUri'] = absolute_url
    response = render(request, 'news/index.html', context)
    return response


def top_picks(request):
    cache_name = 'newscache:{}{}'.format('index', 'top_picks')
    icache = 'infinitecache:{}{}'.format('index', 'top_picks')
    response = cache.get(cache_name, None)

    if response:
        return response

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

            response = HttpResponse(json.dumps(responseData))
            cache.set(cache_name, response, 60*60*24)
            cache.set(icache, response, 60*60*24*14)
            return response
        except Exception as e:
            response = cache.get(icache, None)
            return response

    responseData['success'] = False
    responseData['message'] = str(e)
    response = HttpResponse(json.dumps(responseData))
    return response


def features(request):
    cache_name = 'newscache:{}{}'.format('index', 'features')
    icache = 'infinitecache:{}{}'.format('index', 'features')
    response = cache.get(cache_name, None)

    if response:
        return response

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

            response = HttpResponse(json.dumps(responseData))
            cache.set(cache_name, response, 60*60*24)
            cache.set(icache, response, 60*60*24*14)
            return response
        except Exception as e:
            response = cache.get(icache, None)
            return response

    responseData['success'] = False
    responseData['message'] = str(e)
    response = HttpResponse(json.dumps(responseData))
    return response


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

            f = lambda a: float(len(set(a['keywords']) & set(tags)))/len(set(tags))
            for article in picks:
                article['f'] = f(article)
            responseData['articles'] = sorted(picks, key=f, reverse=True)
            responseData['success'] = True
        except Exception as e:
            responseData['success'] = False
            responseData['message'] = str(e)

    response = HttpResponse(json.dumps(responseData))
    return response
