from django.conf.urls import patterns, url
from news import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^article/10(?P<pk>[0-9]+)$', views.article, name='article'),
                       url(r'^business/(?P<sector>[a-zA-Z]+)$', views.business, name='business'),
                       url(r'^reports/$', views.reports, name='reports'),
                       url(r'^articles/mfeatures/$', views.main_features, name='main_features'),
                       url(r'^articles/homefeatures/$', views.features, name='features'),
                       )
