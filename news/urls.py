from django.conf.urls import patterns, url
from news import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^article/10(?P<pk>[0-9]+)$', views.article, name='article'),
                       url(r'^articles/features/$', views.features, name='features'),
                       url(r'^articles/relatedto/10(?P<pk>[0-9]+)$$', views.related_articles, name='related'),
                       url(r'^articles/toppicks/$', views.top_picks, name='toppicks'),
                       url(r'^business/(?P<sector>[a-zA-Z]+)$', views.business, name='business'),
                       # url(r'^opinion/$', views.column, name='column'),
                       # url(r'^opinion/10(?P<pk>[0-9]+)$', views.column, name='column'),
                       url(r'^reports/$', views.reports, name='reports'),
                       url(r'^articles/relatedto/10(?P<pk>[0-9]+)$', views.related_articles, name='related'),
                       )
