"""pulse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework_jwt import views as rest_framework_jwt_views

from . import views


admin.site.site_header = "Pulse Administration"


urlpatterns = [
    # Admin
    url(
        r'^hidden/secure/pulse/admin/',
        admin.site.urls
    ),

    # API
    url(
        r'^hidden/secure/pulse/api/',
        include('api.urls')
    ),
    url(
        r'^hidden/secure/pulse/auth/',
        include('rest_framework.urls')
    ),
    url(
        regex=r'^hidden/secure/pulse/api/auth/token/$',
        view=rest_framework_jwt_views.obtain_jwt_token,
        name='auth_login_api'
    ),

    # General
    url(
        regex=r'^$',
        view=views.home,
        name='home'
    ),
    url(
        r'^accounts/',
        include('accounts.urls', namespace='accounts')
    ),
    url(
        regex=r'^privacy/$',
        view=views.privacy_policy,
        name='privacy_policy'
    ),
    url(
        regex=r'^terms/$',
        view=views.terms_of_use,
        name='terms_of_use'
    ),

    # Share
    url(
        regex=r'^party/share/(?P<party_pk>\d+)/$',
        view=views.share_party,
        name='share_party'
    ),
]

if settings.DEBUG:
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
    urlpatterns += [] + static(settings.STATIC_URL,
                               document_root=settings.STATIC_ROOT)
    urlpatterns += [] + static(settings.MEDIA_URL,
                               document_root=settings.MEDIA_ROOT)
