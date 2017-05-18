from django.conf.urls import url

from . import views


app_name = 'accounts'
urlpatterns = [
    url(
        regex=r'^logout/$',
        view=views.auth_logout,
        name='logout'
    ),
    url(
        regex=r'^password/change/$',
        view=views.password_change,
        name="password_change"
    ),
    url(
        regex=r'^password/reset/$',
        view=views.password_reset,
        name="password_reset"
    ),
    url(
        regex=r'^password/reset/confirm/'
              r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
              r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        view=views.password_reset_confirm,
        name="password_reset_confirm"
    ),
]
