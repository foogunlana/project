from django.shortcuts import render
from BeautifulSoup import BeautifulSoup
from stears.permissions import editor, approved_writer
from stears.utils import mongo_calls
from stears.models import ReportModel
from django.contrib.auth.decorators import user_passes_test
from utils import HomePage, BusinessPage, EconomyPage, \
Article, htmltag_text, remove_special_characters

import datetime
# Create your views here.


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/')
def article(request, pk):
    pk = int(pk)
    context = {}
    if request.method == 'GET':
        articles = mongo_calls('migrations')
        article = articles.find_one({'article_id': pk})
        if not article:
            articles = mongo_calls('articles')
            article = articles.find_one({'article_id': pk})
        tree = BeautifulSoup(article['content'])
        article['content'] = tree.prettify()
        context = {'article': article}
    return render(request, 'news/article.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/')
def business(request, sector):
    if request.method == 'GET':
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
    return render(request, 'news/business.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/')
def reports(request):
    context = {}
    if request.method == 'GET':
        reports = ReportModel.objects.all().order_by('week_ending')
        for report in reports:
            d = datetime.datetime.strptime(str(report.week_ending), "%Y-%m-%d")
            report.time_title = "Week ending {}".format(d.strftime('%B %-d'))
        context['reports'] = reports
    return render(request, 'news/stearsreport.html', context)


@user_passes_test(lambda u: approved_writer(u), login_url='/weal/')
def index(request):
    context = {}
    if request.method == 'GET':
        onsite = mongo_calls('onsite')
        articles = mongo_calls('articles')
        context = onsite.find_one({'page': 'home'})
        day = str(datetime.datetime.now().weekday())
        col_writer = context['daily_column'].get(day)
        todays_column = articles.find_one({'$query': {
                                  'writer':col_writer, 'category': 'stearsColumn', 'state':'submitted'},
                                  '$orderby':{'time':-1}})
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
    return render(request, 'news/index.html', context)

def test(request):
    return render(request, 'news/test.html')
