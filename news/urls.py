from django.conf.urls import patterns, url
from news import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^articles/$', views.articles, name='articles'),
                       url(r'^business/$', views.business, name='business'),
                       url(r'^economy/$', views.economy, name='economy'),
                       )
