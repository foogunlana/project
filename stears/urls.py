from django.conf.urls import patterns, url
from stears import views

urlpatterns = patterns('',

                       # Basic URLs for main page and others:
                       url(r'^$', views.writers_home_test,
                           {'group': None}, name='home'),
                       url(r'^articles/$', views.writers_home_test,
                           {'group': None}, name='writers_home'),
                       url(r'^articlelist/(?P<group>[a-zA-Z0-9]+)/$',
                           views.writers_home_test, name='articles_group'),
                       url(r'^articles/allocate/(?P<pk>[0-9]+)$',
                           views.allocate_articles, name='allocate'),
                       url(r'^articles/bin/$',
                           views.bin, name='bin'),
                       url(r'^articles/pipeline/$',
                           views.pipeline, name='pipeline'),
                       url(r'^articles/revive/$',
                           views.revive_article, name='revive'),
                       url(r'^articles/submissions/$',
                           views.submissions, name='submissions'),
                       url(r'^articles/write/$', views.writers_write,
                           name='writers_write'),

                       url(r'^article/addtag/(?P<pk>[0-9]+)/$',
                           views.add_tag, name='tag'),
                       url(r'^article/addwriter/$', views.add_writer_to_article,
                           name='add_writer'),
                       url(r'^article/approve/$',
                           views.approve_article, name='approve_article'),
                       url(r'^article/comment/(?P<pk>[0-9]+)/$',
                           views.comment, name='comment'),
                       url(r'^article/delete/$', views.delete_article,
                           name='delete_article'),
                       url(r'^article/detail/(?P<pk>[0-9]+)/$',
                           views.article_detail, name='article_detail'),
                       url(r'^article/preview/(?P<pk>[0-9]+)/$',
                           views.preview_article, name='preview'),
                       url(r'^article/removetag/$',
                           views.remove_tag, name='remove_tag'),
                       url(r'^article/removewriter/$', views.remove_writer_from_article,
                           name='remove_writer'),
                       url(r'^article/review/(?P<pk>[0-9]+)/$', views.review_article,
                           name='review'),
                       url(r'^article/submit/$', views.submit_article,
                           name='submit'),
                       url(r'^article/suggest/$', views.suggest,
                           name='suggest_nse_article'),


                       url(r'^changepassword/$', views.change_password,
                           name='change_password'),
                       url(r'^forgotpassword/$', views.forgot_password,
                           name='forgot_password'),
                       url(r'^login/$', views.login_view, name='login'),
                       url(r'^logout/$', views.logout_view, name='logout'),
                       url(r'^noaccess/$', views.noaccess, name='noaccess'),
                       url(r'^register/$', views.register, name='register'),


                       url(r'^gts/$', views.gts, name='gts'),
                       url(r'^photos/$', views.upload_photo,
                           name='photos'),
                       url(r'^research/$', views.research, name='research'),


                       url(r'^writers/$', views.writers_list,
                           name='writers_list'),

                       url(r'^writer/accept/$',
                           views.accept_article_category, name='accept_article'),
                       url(r'^writer/approve/$', views.approve_writer,
                           name='approve_writer'),
                       url(r'^writer/details/(?P<name>[a-zA-Z0-9_]+)/$',
                           views.writer_detail, name='writer_detail'),
                       url(r'^writer/detail/edit/$',
                           views.edit_writer_detail, name='edit_writer_detail'),


                       # url(r'^writers/rich_text/$', views.edit_rich_text,
                       #     name='rich_text'),


                       # url(r'^articles/(?P<year>[0-9]{4})/$', views.year_archive),
                       # url(r'^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.month_archive),
                       # url(r'^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$', views.day_archive),
                       # url(r'^articles/article/?P<pk>\d+/$',views.article_detail),

                       # url(r'^details/$', views.details, name='details'),
                       )
