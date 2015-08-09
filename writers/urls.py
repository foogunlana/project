from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView
from writers import settings

urlpatterns = patterns('',
                       url(r'^weal/',
                           include('stears.urls', namespace='weal')),
                       url(r'^',
                           include('news.urls', namespace='news')),
                       url(r'^robots\.txt$', TemplateView.as_view(
                           template_name='robots.txt')),
                       )
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
