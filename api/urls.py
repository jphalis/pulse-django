from django.conf.urls import url

from push_notifications.api.rest_framework import APNSDeviceAuthorizedViewSet
from . import views
from .views import APIHomeView
from .views import (AccountCreateAPIView, MyUserDetailAPIView,
                    MyUserListAPIView, PhotoCreateAPIView)
from .views import FeedAPIView
from .views import NotificationAPIView, NotificationAjaxAPIView
from .views import (PasswordChangeView, PasswordResetView,
                    PasswordResetConfirmView)
from .views import (OwnPartyListAPIView, PartyCreateAPIView,
                    PartyDetailAPIView, PartyListAPIView, UserPartyListAPIView)
from .views import SearchListAPIView


urlpatterns = [
    # G E N E R A L
    url(
        regex=r'^$',
        view=APIHomeView.as_view(),
        name='api_home'
    ),
    url(
        regex=r'^search/$',
        view=SearchListAPIView.as_view(),
        name='search_api'
    ),
    url(
        regex=r'^device/apns/$',
        view=APNSDeviceAuthorizedViewSet.as_view({'post': 'create'}),
        name='create_apns_device'
    ),

    # A C C O U N T S
    url(
        regex=r'^accounts/$',
        view=MyUserListAPIView.as_view(),
        name='user_account_list_api'
    ),
    url(
        regex=r'^accounts/create/$',
        view=AccountCreateAPIView.as_view(),
        name='account_create_api'
    ),
    url(
        regex=r'^accounts/(?P<user_pk>\d+)/$',
        view=MyUserDetailAPIView.as_view(),
        name='user_account_detail_api'
    ),
    url(
        regex=r'^accounts/photos/create/$',
        view=PhotoCreateAPIView.as_view({'post': 'create'}),
        name='photo_create_api'
    ),
    url(
        regex=r'^accounts/photos/delete/(?P<photo_pk>\d+)/$',
        view=views.photo_delete_api,
        name='photo_delete_api'
    ),
    url(
        regex=r'^follow/(?P<user_pk>\d+)/$',
        view=views.follow_status_api,
        name='follow_status_api'
    ),
    url(
        regex=r'^privacy_status/(?P<user_pk>\d+)/$',
        view=views.privacy_status_api,
        name='privacy_status_api'
    ),
    url(
        regex=r'^block/(?P<user_pk>\d+)/$',
        view=views.block_user_api,
        name='block_user_api'
    ),

    # A U T H E N T I C A T I O N
    url(
        regex=r'^password/reset/$',
        view=PasswordResetView.as_view(),
        name='rest_password_reset'
    ),
    url(
        regex=r'^password/reset/confirm/'
              r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
              r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        view=PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm'
    ),

    url(
        regex=r'^password/change/$',
        view=PasswordChangeView.as_view(),
        name='rest_password_change'
    ),

    # F E E D
    url(
        regex=r'^feed/(?P<user_id>\d+)/$',
        view=FeedAPIView.as_view(),
        name='feed_list_api'
    ),

    # F L A G S
    url(
        regex=r'^flag/create/(?P<party_pk>\d+)/$',
        view=views.flag_create_api,
        name='flag_create_api'
    ),

    # N O T I F I C A T I O N S
    url(
        regex=r'^notifications/$',
        view=NotificationAPIView.as_view(),
        name='notification_list_api'
    ),
    url(
        regex=r'^notifications/unread/$',
        view=NotificationAjaxAPIView.as_view(),
        name='get_unread_notifications_api'
    ),

    # P A R T I E S
    url(
        regex=r'^parties/$',
        view=PartyListAPIView.as_view(),
        name='party_list_api'
    ),
    url(
        regex=r'^parties/own/$',
        view=OwnPartyListAPIView.as_view(),
        name='own_party_list_api'
    ),
    url(
        regex=r'^parties/(?P<user_pk>\d+)/$',
        view=UserPartyListAPIView.as_view(),
        name='user_party_list_api'
    ),
    url(
        regex=r'^party/(?P<party_pk>\d+)/$',
        view=PartyDetailAPIView.as_view(),
        name='party_detail_api'
    ),
    url(
        regex=r'^party/create/$',
        view=PartyCreateAPIView.as_view({'post': 'create'}),
        name='party_create_api'
    ),
    url(
        regex=r'^party/attend/(?P<party_pk>\d+)/$',
        view=views.party_attend_api,
        name='party_attend_api'
    ),
    url(
        regex=r'^party/approve/(?P<party_pk>\d+)/(?P<user_pk>\d+)/$',
        view=views.requester_approve_api,
        name='requester_approve_api'
    ),
    url(
        regex=r'^party/deny/(?P<party_pk>\d+)/(?P<user_pk>\d+)/$',
        view=views.requester_deny_api,
        name='requester_deny_api'
    ),
    url(
        regex=r'^party/like/(?P<party_pk>\d+)/$',
        view=views.party_like_api,
        name='party_like_api'
    ),
]
