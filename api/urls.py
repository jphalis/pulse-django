from django.conf.urls import url


from . import views
from .views import APIHomeView
from .views import (AccountCreateAPIView,
                    MyUserDetailAPIView, MyUserListAPIView)
from .views import FeedAPIView
from .views import NotificationAPIView, NotificationAjaxAPIView
from .views import (PasswordChangeView, PasswordResetView,
                    PasswordResetConfirmView)
from .views import (OwnPartyListAPIView, PartyCreateAPIView,
                    PartyDetailAPIView, PartyListAPIView,
                    UserPartyListAPIView)


urlpatterns = [
    # G E N E R A L
    url(r'^$', APIHomeView.as_view(),
        name='api_home'),

    # A C C O U N T S
    url(r'^accounts/$',
        MyUserListAPIView.as_view(),
        name='user_account_list_api'),
    url(r'^accounts/create/$',
        AccountCreateAPIView.as_view(),
        name='account_create_api'),
    url(r'^accounts/(?P<user_pk>\d+)/$',
        MyUserDetailAPIView.as_view(),
        name='user_account_detail_api'),
    url(r'^follow/(?P<user_pk>\d+)/$',
        views.follow_status_api,
        name='follow_status_api'),
    url(r'^privacy_status/(?P<user_pk>\d+)/$',
        views.privacy_status_api,
        name='privacy_status_api'),
    url(r'^block/(?P<user_pk>\d+)/$',
        views.block_user_api,
        name='block_user_api'),

    # A U T H E N T I C A T I O N
    url(r'^password/reset/$',
        PasswordResetView.as_view(),
        name='rest_password_reset'),
    url(r'^password/reset/confirm/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm'),
    url(r'^password/change/$',
        PasswordChangeView.as_view(),
        name='rest_password_change'),

    # F E E D
    url(r'^feed/$',
        FeedAPIView.as_view(),
        name='feed_list_api'),

    # F L A G S
    url(r'^flag/create/(?P<party_pk>\d+)/$',
        views.flag_create_api,
        name='flag_create_api'),

    # N O T I F I C A T I O N S
    url(r'^notifications/$',
        NotificationAPIView.as_view(),
        name='notification_list_api'),
    url(r'^notifications/unread/$',
        NotificationAjaxAPIView.as_view(),
        name='get_unread_notifications_api'),

    # P A R T I E S
    url(r'^parties/$',
        PartyListAPIView.as_view(),
        name='party_list_api'),
    url(r'^parties/own/$',
        OwnPartyListAPIView.as_view(),
        name='own_party_list_api'),
    url(r'^parties/(?P<user_pk>\d+)/$',
        UserPartyListAPIView.as_view(),
        name='user_party_list_api'),
    url(r'^party/(?P<party_pk>\d+)/$',
        PartyDetailAPIView.as_view(),
        name='party_detail_api'),
    url(r'^party/create/$',
        PartyCreateAPIView.as_view({'post': 'create'}),
        name='party_create_api'),
    url(r'^party/attend/(?P<party_pk>\d+)/$',
        views.party_attend_api,
        name='party_attend_api'),
]
