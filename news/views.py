from django.shortcuts import render
from stears.permissions import approved_writer
from stears.utils import mongo_calls
from stears.models import ReportModel
from django.http import HttpRequest
from django.contrib.auth.decorators import user_passes_test
from utils import htmltag_text, remove_special_characters

import datetime


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/')
def article(request, pk):
    pk = int(pk)
    context = {}
    if request.method == 'GET':
        try:
            articles = mongo_calls('migrations')
            article = articles.find_one(
                {'article_id': pk},
                {'headline': 1, 'category': 1, 'writer': 1,
                 'keywords': 1, 'content': 1})

            aUri = HttpRequest.build_absolute_uri(request)
            context = {'article': article, 'aUri': aUri}
        except Exception:
            pass
    return render(request, 'news/article.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/')
def business(request, sector):
    context = {}
    if request.method == 'GET':
        try:
            onsite = mongo_calls('onsite')
            context = onsite.find_one({'page': 'b_e', 'sector': sector})
            if context:
                if context.get('main_feature'):
                    main_feature = context['main_feature']
                    bmf_summary = htmltag_text(main_feature['content'], 'p')
                    bmf_summary = remove_special_characters(bmf_summary.pop())
                    context['bmf_summary'] = bmf_summary
            else:
                context = {}
        except Exception:
            pass
    return render(request, 'news/business.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/')
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
    return render(request, 'news/stearsreport.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/')
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
                                               'state': 'submitted'},
                                               '$orderby': {'time': -1}})
            if todays_column:
                # optimize by adding titles to articles
                writers = mongo_calls('user')
                writer = writers.find_one({'username': col_writer})
                todays_column['column_title'] = writer.get('column', '')
                #
                dc_summary = htmltag_text(todays_column['content'], 'p')
                dc_summary = remove_special_characters(dc_summary.pop())
                context['daily_column_summary'] = dc_summary
                context['column'] = todays_column
        except Exception:
            pass
    return render(request, 'news/index.html', context)
