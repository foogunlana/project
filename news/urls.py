from django.conf.urls import patterns, url
from news import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^articles/$', views.articles, name='articles'),
                       url(r'^companies/$', views.companies, name='companies'),
                       )
