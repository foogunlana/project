from django.shortcuts import render
from stears.utils import mongo_calls
from stears.models import ReportModel
from django.http import HttpRequest
from utils import summarize

import datetime


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
            context = {'article': article, 'aUri': aUri}
        except Exception:
            pass
    context['sUri'] = 'http://{}'.format(HttpRequest.get_host(request))
    return render(request, 'news/article.html', context)


def business(request, sector):
    context = {}
    if request.method == 'GET':
        try:
            onsite = mongo_calls('onsite')
            context = onsite.find_one({'page': 'b_e', 'sector': sector})
            if context and context.get('main_feature'):
                context['bmf_summary'] = summarize(context['main_feature'])
            else:
                context = {}
        except Exception:
            pass
    context['sUri'] = 'http://{}'.format(HttpRequest.get_host(request))
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
        except Exception:
            pass
    context['sUri'] = 'http://{}'.format(HttpRequest.get_host(request))
    return render(request, 'news/stearsreport.html', context)


def index(request):
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
                # optimize by adding titles to articles
                writers = mongo_calls('user')
                writer = writers.find_one({'username': col_writer})
                todays_column['column_title'] = writer.get('column', '')
                dc_summary = summarize(todays_column)
                context['daily_column_summary'] = dc_summary
                context['column'] = todays_column
        except Exception:
            pass
    context['sUri'] = 'http://{}'.format(HttpRequest.get_host(request))
    return render(request, 'news/index.html', context)
