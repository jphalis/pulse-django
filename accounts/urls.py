from django.conf.urls import url

from . import views


app_name = 'accounts'
urlpatterns = [
    url(r'^signout/$', views.auth_logout, name='logout'),
    url(r'^password/change/$', views.password_change, name="password_change"),
    url(r'^password/reset/$', views.password_reset, name="password_reset"),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, name="password_reset_confirm"),
]
