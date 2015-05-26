from django.conf.urls import patterns, url
from news import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^article/(?P<pk>[0-9]+)$', views.article, name='article'),
                       url(r'^business/$', views.business, name='business'),
                       url(r'^economy/$', views.economy, name='economy'),
                       )
