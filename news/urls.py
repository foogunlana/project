from django.conf.urls import patterns, url
from news import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^article/10(?P<pk>[0-9]+)$', views.article, name='article'),
                       url(r'^business/(?P<sector>[a-zA-Z]+)$', views.business, name='business'),
                       url(r'^reports/$', views.reports, name='reports'),
                       url(r'^articles/toppicks/$', views.top_picks, name='toppicks'),
                       url(r'^articles/features/$', views.features, name='features'),
                       url(r'^articles/relatedto/(?P<pk>[0-9]+)$$', views.related_articles, name='related'),
                       )
