from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from writers import settings

urlpatterns = patterns('',
                       url(r'^test/$', 'writers.views.test', name='test'),
                       url(r'^weal/',
                           include('stears.urls', namespace='weal')),
                       url(r'^',
                           include('news.urls', namespace='news')),
                       )

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
