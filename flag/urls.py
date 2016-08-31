from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^create/$',
        views.flag_create_ajax,
        name="flag_create_ajax"),
]
