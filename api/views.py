from datetime import datetime

from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response as RestResponse
from rest_framework.reverse import reverse as api_reverse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F
from django.shortcuts import get_object_or_404

from accounts.models import Follower, MyUser, Photo
from core.mixins import AdminRequiredMixin, CacheMixin
from feed.models import Feed
from feed.signals import feed_item
from flag.models import Flag
from notifications.models import Notification
from notifications.signals import notify
from parties.models import Party
from .account_serializers import (AccountCreateSerializer, FollowerSerializer,
                                  MyUserSerializer, PhotoCreateSerializer)
from .auth_serializers import (PasswordResetSerializer,
                               PasswordResetConfirmSerializer,
                               PasswordChangeSerializer)
from .feed_serializers import FeedSerializer
from .mixins import DefaultsMixin, FiltersMixin
from .notification_serializers import NotificationSerializer
from .pagination import (AccountPagination, NotificationPagination,
                         PartyPagination)
from .party_serializers import PartyCreateSerializer, PartySerializer
from .permissions import IsOwnerOrReadOnly, MyUserIsOwnerOrReadOnly

# Create your views here.


class APIHomeView(AdminRequiredMixin, CacheMixin, DefaultsMixin, APIView):
    cache_timeout = 60 * 60 * 24 * 30

    def get(self, request, format=None):
        user = request.user
        data = {
            'authentication': {
                'login': api_reverse('auth_login_api',
                                     request=request),
                'password_reset': api_reverse('rest_password_reset',
                                              request=request),
                'password_change': api_reverse('rest_password_change',
                                               request=request),
                'sign_up': api_reverse('account_create_api',
                                       request=request),
            },
            'accounts': {
                'count': MyUser.objects.all().count(),
                'url': api_reverse('user_account_list_api',
                                   request=request),
                'profile_url': api_reverse('user_account_detail_api',
                                           request=request,
                                           kwargs={'user_pk': user.pk}),
                'photo_upload': api_reverse('photo_create_api',
                                            request=request)
            },
            'feed': {
                'url': api_reverse('feed_list_api',
                                   request=request),
            },
            'notifications': {
                'count': Notification.objects.unread_for_user(user).count(),
                'url': api_reverse('notification_list_api',
                                   request=request),
                'unread_url': api_reverse('get_unread_notifications_api',
                                          request=request),
            },
            'parties': {
                'count': Party.objects.active().count(),
                'url': api_reverse('party_list_api',
                                   request=request),
                'create_url': api_reverse('party_create_api',
                                          request=request),
                'own_parties': api_reverse('own_party_list_api',
                                           request=request),
            },
        }
        return RestResponse(data)


########################################################################
# ACCOUNTS                                                             #
########################################################################
class AccountCreateAPIView(generics.CreateAPIView):
    serializer_class = AccountCreateSerializer
    permission_classes = (permissions.AllowAny,)


class MyUserListAPIView(CacheMixin, DefaultsMixin, generics.ListAPIView):
    cache_timeout = 60 * 60 * 24
    pagination_class = AccountPagination
    serializer_class = MyUserSerializer
    queryset = MyUser.objects.all()


class MyUserDetailAPIView(CacheMixin,
                          generics.RetrieveAPIView,
                          mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin):
    cache_timeout = 60 * 5
    permission_classes = (
        permissions.IsAuthenticated,
        MyUserIsOwnerOrReadOnly,
    )
    serializer_class = MyUserSerializer
    parser_classes = (MultiPartParser, FormParser,)

    def get_object(self):
        obj = get_object_or_404(MyUser, pk=self.kwargs["user_pk"])

        if self.request.user in obj.blocking.all():
            raise PermissionDenied(
                "You do not have permission to view that profile.")
        return obj

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class PhotoCreateAPIView(ModelViewSet):
    queryset = Photo.objects.select_related('user').all()
    serializer_class = PhotoCreateSerializer
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        photo=self.request.data.get('photo'))


@api_view(['POST'])
def follow_status_api(request, user_pk):
    viewing_user = request.user
    follower, created = Follower.objects.get_or_create(user=viewing_user)
    user = get_object_or_404(MyUser, pk=user_pk)
    followed, created = Follower.objects.get_or_create(user=user)

    try:
        user_followed = (Follower.objects.select_related('user')
                                         .get(user=user, followers=follower))
    except Follower.DoesNotExist:
        user_followed = None

    if user_followed:
        followed.followers.remove(follower)
    else:
        followed.followers.add(follower)
        notify.send(
            viewing_user,
            recipient=user,
            verb='is now following you',
            # target=viewing_user,
        )

        if user in viewing_user.blocking.all():
            viewing_user.blocking.remove(user)

    serializer = FollowerSerializer(followed, context={'request': request})
    return RestResponse(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def block_user_api(request, user_pk):
    viewing_user = request.user
    user_to_block = get_object_or_404(MyUser, pk=user_pk)
    follower, created = Follower.objects.get_or_create(user=viewing_user)
    followed, created = Follower.objects.get_or_create(user=user_to_block)

    # Does the viewing_user follow the user_to_block?
    # If so, remove them
    try:
        user_to_block_followed = (Follower.objects.select_related('user')
                                          .get(user=user_to_block,
                                               followers=follower))
    except Follower.DoesNotExist:
        user_to_block_followed = None

    if user_to_block_followed:
        followed.followers.remove(follower)

    # Does the user_to_block follow the viewing_user?
    # If so, remove them
    try:
        viewer_followed = (Follower.objects.select_related('user')
                                           .get(user=viewing_user,
                                                followers=followed))
    except Follower.DoesNotExist:
        viewer_followed = None

    if viewer_followed:
        follower.followers.remove(followed)

    # Is the user_to_block already in blocked users?
    if user_to_block not in viewing_user.blocking.all():
        viewing_user.blocking.add(user_to_block)

    serializer = FollowerSerializer(followed, context={'request': request})
    return RestResponse(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def privacy_status_api(request, user_pk):
    user = get_object_or_404(MyUser, pk=user_pk)
    user.is_private = False if user.is_private else True
    user.save(update_fields=['is_private'])
    serializer = MyUserSerializer(user, context={'request': request})
    return RestResponse(serializer.data, status=status.HTTP_201_CREATED)


########################################################################
# AUTHENTICATION                                                       #
########################################################################
class PasswordResetView(generics.GenericAPIView):
    """
    Calls PasswordResetForm save method
    Accepts the following POST parameters: email
    Returns the success/fail message
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return RestResponse(
            {"success": "Password reset e-mail has been sent."},
            status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Password reset e-mail link is confirmed, so this resets the user's password
    Accepts the following POST parameters: new_password1, new_password2
    Accepts the following Django URL arguments: token, uid
    Returns the success/fail message
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return RestResponse({"success": "Password has been reset."})


class PasswordChangeView(generics.GenericAPIView):
    """
    Calls SetPasswordForm save method
    Accepts the following POST parameters: new_password1, new_password2
    Returns the success/fail message
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return RestResponse({"success": "New password has been saved."})


########################################################################
# FEED                                                                 #
########################################################################
class FeedAPIView(CacheMixin, DefaultsMixin, generics.ListAPIView):
    # cache_timeout = 60 * 7
    serializer_class = FeedSerializer

    def get_queryset(self):
        return Feed.objects.recent_for_user(user=self.request.user, num=50)


########################################################################
# FLAGS                                                                #
########################################################################
@api_view(['POST'])
def flag_create_api(request, party_pk):
    party = get_object_or_404(Party, pk=party_pk)
    party_creator = party.user

    flagged, created = Flag.objects.get_or_create(party=party,
                                                  creator=request.user)
    flagged.flag_count = F('flag_count') + 1
    flagged.save()

    party_creator.times_flagged = F('times_flagged') + 1
    party_creator.save(update_fields=['times_flagged'])

    send_mail('FLAGGED ITEM',
              'There is a new flagged item with the id: {}'.format(flagged.id),
              settings.DEFAULT_HR_EMAIL, [settings.DEFAULT_HR_EMAIL],
              fail_silently=True)

    serializer = PartySerializer(party, context={'request': request})
    return RestResponse(serializer.data, status=status.HTTP_201_CREATED)


########################################################################
# NOTIFICATIONS                                                        #
########################################################################
class NotificationAPIView(CacheMixin, DefaultsMixin, generics.ListAPIView):
    # cache_timeout = 60 * 7
    pagination_class = NotificationPagination
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """
        Update all of the notifications to read=True.
        Get 50 most recent notifications for the user.
        Delete all of the notifications older than the 50 displayed.
        Return the 50 most recent notifications for the user.
        """
        user = self.request.user
        notifications = Notification.objects.all_for_user(user=user)
        notifications.update(read=True)
        notifications = notifications[:50]
        if notifications.count() > 0:
            delete_after_datetime = list(notifications)[-1].created
            Notification.objects.all_for_user(user).filter(
                created__lt=delete_after_datetime).delete()
        return notifications


class NotificationAjaxAPIView(DefaultsMixin, generics.ListAPIView):
    pagination_class = NotificationPagination
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        user.last_login = datetime.now()
        user.save(update_fields=['last_login'])
        queryset = Notification.objects.unread_for_user(user=user).last()
        if not queryset:
            raise ValidationError({"detail":
                                  "You have no new notifications."})
        return queryset


########################################################################
# PARTIES                                                              #
########################################################################
class PartyCreateAPIView(ModelViewSet):
    queryset = Party.objects.active()
    serializer_class = PartyCreateSerializer
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user,
                        party_type=self.request.data.get('party_type'),
                        invite_type=self.request.data.get('invite_type'),
                        name=self.request.data.get('name'),
                        location=self.request.data.get('location'),
                        latitude=self.request.data.get('latitude'),
                        longitude=self.request.data.get('longitude'),
                        party_size=self.request.data.get('party_size'),
                        party_month=self.request.data.get('party_month'),
                        party_day=self.request.data.get('party_day'),
                        party_year=self.request.data.get('party_year'),
                        start_time=self.request.data.get('start_time'),
                        end_time=self.request.data.get('end_time'),
                        description=self.request.data.get('description'),
                        image=self.request.data.get('image'),)
        party = Party.objects.get(id=serializer.data.get('id'))
        user_ids = self.request.data.get('invited_user_ids')

        if user_ids:
            for user_id in user_ids.split(','):
                invited = MyUser.objects.get(id=user_id)
                party.invited_users.add(invited)
                notify.send(
                    user,
                    recipient=invited,
                    verb='has invited you to their event',
                    target=party,
                )
        party.attendees.add(user)
        feed_item.send(
            user,
            verb='are hosting an event.',
            target=party,
        )


class PartyDetailAPIView(CacheMixin,
                         generics.RetrieveAPIView,
                         mixins.DestroyModelMixin,
                         mixins.UpdateModelMixin):
    cache_timeout = 60 * 7
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly,)
    serializer_class = PartySerializer

    def get_object(self):
        obj = get_object_or_404(Party, pk=self.kwargs["party_pk"])
        expires_on = datetime(
            obj.party_year, obj.party_month, obj.party_day,
            int(obj.end_time.strftime('%H')), int(obj.end_time.strftime('%M')))
        obj.is_active = False if expires_on <= datetime.now() else True
        obj.save(update_fields=['is_active'])
        return obj

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class PartyListAPIView(CacheMixin, DefaultsMixin, FiltersMixin,
                       generics.ListAPIView):
    # cache_timeout = 60 * 60 * 24
    pagination_class = PartyPagination
    serializer_class = PartySerializer
    search_fields = ('user__email', 'user__full_name',
                     'attendees__email', 'attendees__full_name',
                     'requesters__email', 'requesters__full_name',)
    ordering_fields = ('created',)

    def get_queryset(self):
        return Party.objects.active().exclude(party_type=Party.INVITE_ONLY)


class OwnPartyListAPIView(CacheMixin, DefaultsMixin, FiltersMixin,
                          generics.ListAPIView):
    # cache_timeout = 60 * 60 * 24
    pagination_class = PartyPagination
    serializer_class = PartySerializer
    search_fields = ('user__email', 'user__full_name',
                     'attendees__email', 'attendees__full_name',
                     'requesters__email', 'requesters__full_name',)
    ordering_fields = ('created',)

    def get_queryset(self):
        return Party.objects.own_parties_hosting(user=self.request.user)


class UserPartyListAPIView(CacheMixin, DefaultsMixin, FiltersMixin,
                           generics.ListAPIView):
    # cache_timeout = 60 * 60 * 24
    pagination_class = PartyPagination
    serializer_class = PartySerializer
    search_fields = ('user__email', 'user__full_name',
                     'attendees__email', 'attendees__full_name',
                     'requesters__email', 'requesters__full_name',)
    ordering_fields = ('created',)

    def get_queryset(self):
        return Party.objects.own_parties_hosting(
            user=MyUser.objects.get(pk=self.kwargs['user_pk']))


@api_view(['POST'])
def party_attend_api(request, party_pk):
    user = request.user
    party = get_object_or_404(Party, pk=party_pk)
    party_creator = party.user

    if user in party.attendees.all():
        party.attendees.remove(user)
    elif party.invite_type == Party.INVITE_ONLY:

        if user == party_creator:
            party.attendees.add(user)
        else:
            party.requesters.add(user)
            notify.send(
                user,
                recipient=party.user,
                verb='has requested to attend your event',
                target=party,
            )
    else:
        party.attendees.add(user)

        if user != party_creator:
            notify.send(
                user,
                recipient=party_creator,
                verb='will be attending your event',
                target=party,
            )
            feed_item.send(
                user,
                verb='will be attending {0}\'s event'.format(
                    party_creator.get_full_name),
                target=party,
            )
    party.save()
    serializer = PartySerializer(party, context={'request': request})
    return RestResponse(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def requester_approve_api(request, party_pk, user_pk):
    user = get_object_or_404(MyUser, pk=user_pk)
    party = get_object_or_404(Party, pk=party_pk)
    party_creator = party.user
    party.attendees.add(user)
    party.requesters.remove(user)
    notify.send(
        party_creator,
        recipient=user,
        verb='has accepted your request to attend',
        target=party,
    )
    feed_item.send(
        user,
        verb='is attending {0}\'s event'.format(party_creator.get_full_name),
        target=party,
    )
    serializer = PartySerializer(party, context={'request': request})
    return RestResponse(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def requester_deny_api(request, party_pk, user_pk):
    party = get_object_or_404(Party, pk=party_pk)
    party.requesters.remove(get_object_or_404(MyUser, pk=user_pk))
    serializer = PartySerializer(party, context={'request': request})
    return RestResponse(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def party_like_api(request, party_pk):
    user = request.user
    party = get_object_or_404(Party, pk=party_pk)

    if user in party.likers.all():
        party.likers.remove(user)
    else:
        party.likers.add(user)

    serializer = PartySerializer(party, context={'request': request})
    return RestResponse(serializer.data, status=status.HTTP_201_CREATED)
