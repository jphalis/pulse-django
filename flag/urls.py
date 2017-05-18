from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        regex=r'^create/$',
        view=views.flag_create_ajax,
        name='flag_create_ajax'
    ),
]
