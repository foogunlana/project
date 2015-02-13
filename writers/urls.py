from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from writers import settings

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', 'writers.views.home', name='home'),
                       url(r'^test/$', 'writers.views.test', name='test'),
                       # url(r'^blog/', include('blog.urls')),

                       # url(r'^admin/', include(admin.site.urls)),
                       url(r'^stears/',
                           include('stears.urls', namespace='stears')),
                       url(r'^news/',
                           include('news.urls', namespace='news')),
                       )

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
