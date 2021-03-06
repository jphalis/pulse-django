from datetime import datetime, date, timedelta

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
from django.views.decorators.cache import never_cache

from accounts.models import Follower, MyUser, Photo
from core.mixins import AdminRequiredMixin, CacheMixin
from feed.models import Feed
from feed.signals import feed_item
from flag.models import Flag
from notifications.models import Notification
from notifications.signals import notify
from parties.models import Party
from push_notifications.models import APNSDevice
from .account_serializers import (AccountCreateSerializer, FollowerSerializer,
                                  MyUserSerializer, PhotoCreateSerializer,
                                  PhotoSerializer)
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
from .search_serializers import SearchMyUserSerializer

# Create your views here.


class APIHomeView(AdminRequiredMixin, DefaultsMixin, APIView):
    def get(self, request, format=None):
        user = request.user
        data = {
            'authentication': {
                'apns': api_reverse('create_apns_device', request=request),
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
                                   request=request,
                                   kwargs={'user_id': user.id}),
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
            'search': {
                'url': api_reverse('search_api', request=request),
                'help_text': "add '?q=searched_parameter' to the "
                             "end of the url to display results"
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


class MyUserDetailAPIView(generics.RetrieveAPIView,
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


@api_view(['DELETE'])
def photo_delete_api(request, photo_pk):
    photo = get_object_or_404(Photo, pk=photo_pk)
    photo.delete()
    serializer = PhotoSerializer(photo, context={'request': request})
    return RestResponse(serializer.data, status=status.HTTP_200_OK)


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
            verb='is now following you.',
        )

        # Push notifications
        try:
            device = APNSDevice.objects.get(user=user)
        except APNSDevice.DoesNotExist:
            device = None

        if device:
            device.send_message(
                "{} is now following you.".format(viewing_user),
                sound='default'
            )

        if user in viewing_user.blocking.all():
            viewing_user.blocking.remove(user)

    serializer = FollowerSerializer(followed, context={'request': request})
    return RestResponse(serializer.data, status=status.HTTP_200_OK)


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
            status=status.HTTP_200_OK
        )


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
class FeedAPIView(DefaultsMixin, generics.ListAPIView):
    serializer_class = FeedSerializer

    def get_queryset(self):
        user = MyUser.objects.get(id=self.kwargs['user_id'])
        return Feed.objects.all_for_user(user=user)[:50]


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

    send_mail(
        'FLAGGED ITEM',
        'There is a new flagged item with the id: {}'.format(flagged.id),
        settings.DEFAULT_HR_EMAIL,
        [settings.DEFAULT_HR_EMAIL],
        fail_silently=True
    )

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
        data = self.request.data
        party_type = data.get('party_type')
        invite_type = data.get('invite_type')
        name = data.get('name')
        location = data.get('location')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        party_size = data.get('party_size')
        party_month = data.get('party_month')
        party_day = data.get('party_day')
        party_year = data.get('party_year')
        start_time = data.get('start_time')
        recurrence = data.get('recurrence')
        end_time = data.get('end_time')
        description = data.get('description')
        image = data.get('image')
        serializer.save(
            user=user, party_type=party_type, invite_type=invite_type,
            name=name, location=location, latitude=latitude,
            longitude=longitude, party_size=party_size,
            party_month=party_month, party_day=party_day,
            party_year=party_year, start_time=start_time,
            recurrence=recurrence, end_time=end_time, description=description,
            image=image
        )
        party = Party.objects.get(id=serializer.data.get('id'))
        party.attendees.add(user)
        user_ids = data.get('invited_user_ids')

        if user_ids:
            for user_id in user_ids.split(','):
                invited = MyUser.objects.get(id=user_id)
                party.invited_users.add(invited)
                notify.send(
                    user,
                    recipient=invited,
                    verb='has invited you to an event.',
                    target=party,
                )

                # Push notifications
                try:
                    device = APNSDevice.objects.get(user=invited)
                except APNSDevice.DoesNotExist:
                    device = None

                if device:
                    device.send_message(
                        "{} has invited you to an event.".format(user),
                        sound='default'
                    )

        if party.invite_type != Party.INVITE_ONLY:
            feed_item.send(
                user,
                verb='hosting an event.',
                target=party,
            )

        if party.recurrence != Party.NONE:
            start_date = date(
                int(party_year),
                int(party_month),
                int(party_day)
            )

            if party.recurrence == Party.DAILY:
                for i in range(6):
                    start_date += timedelta(days=1)
                    day = start_date.strftime('%d')
                    month = start_date.strftime('%m')
                    year = start_date.strftime('%Y')
                    Party.objects.create(
                        user=user, party_type=party_type,
                        invite_type=invite_type, name=name, location=location,
                        latitude=latitude, longitude=longitude,
                        party_size=party_size, party_month=month,
                        party_day=day, party_year=year, start_time=start_time,
                        recurrence=recurrence, end_time=end_time,
                        description=description, image=image
                    )
            elif party.recurrence == Party.WEEKLY:
                for i in range(3):
                    start_date += timedelta(weeks=1)
                    day = start_date.strftime('%d')
                    month = start_date.strftime('%m')
                    year = start_date.strftime('%Y')
                    Party.objects.create(
                        user=user, party_type=party_type,
                        invite_type=invite_type, name=name, location=location,
                        latitude=latitude, longitude=longitude,
                        party_size=party_size, party_month=month,
                        party_day=day, party_year=year, start_time=start_time,
                        recurrence=recurrence, end_time=end_time,
                        description=description, image=image
                    )
            elif party.recurrence == Party.MONTHLY:
                for i in range(2):
                    start_date += timedelta(weeks=4)
                    day = start_date.strftime('%d')
                    month = start_date.strftime('%m')
                    year = start_date.strftime('%Y')
                    Party.objects.create(
                        user=user, party_type=party_type,
                        invite_type=invite_type, name=name, location=location,
                        latitude=latitude, longitude=longitude,
                        party_size=party_size, party_month=month,
                        party_day=day, party_year=year, start_time=start_time,
                        recurrence=recurrence, end_time=end_time,
                        description=description, image=image
                    )
        return serializer


class PartyDetailAPIView(generics.RetrieveAPIView,
                         mixins.DestroyModelMixin,
                         mixins.UpdateModelMixin):
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly,)
    serializer_class = PartySerializer

    def get_object(self):
        obj = get_object_or_404(Party, pk=self.kwargs["party_pk"])
        now = datetime.now()
        if obj.end_time:
            if obj.end_time < obj.start_time:
                expires_on = datetime(
                    obj.party_year,
                    obj.party_month,
                    obj.party_day,
                    int(obj.end_time.strftime('%H')),
                    int(obj.end_time.strftime('%M'))
                )
                expires_on += timedelta(days=1)
            else:
                expires_on = datetime(
                    obj.party_year, obj.party_month, obj.party_day,
                    int(obj.end_time.strftime('%H')),
                    int(obj.end_time.strftime('%M')))
            obj.is_active = False if expires_on <= now else True
        else:
            expires_on = date(
                obj.party_year, obj.party_month, obj.party_day
            )
            obj.is_active = False if now.date() > expires_on else True
        obj.save(update_fields=['is_active'])
        return obj

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class PartyListAPIView(DefaultsMixin, FiltersMixin, generics.ListAPIView):
    pagination_class = PartyPagination
    serializer_class = PartySerializer
    search_fields = ('user__email', 'user__full_name',
                     'attendees__email', 'attendees__full_name',
                     'requesters__email', 'requesters__full_name',)
    # queryset = Party.objects.active().exclude(
    #     invite_type=Party.INVITE_ONLY).order_by(
    #         'party_year', 'party_month', 'party_day', 'start_time')

    @never_cache
    def dispatch(self, *args, **kwargs):
        return super(PartyListAPIView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Party.objects.active().exclude(invite_type=Party.INVITE_ONLY)
        to_remove_ids = []

        for party in qs:
            start_date = date(party.party_year,
                              party.party_month,
                              party.party_day)
            if party.recurrence != Party.NONE and start_date > date.today():
                to_remove_ids.append(party.id)
        return qs.exclude(id__in=to_remove_ids).order_by(
            'party_year', 'party_month', 'party_day', 'start_time'
        )


class OwnPartyListAPIView(DefaultsMixin, FiltersMixin, generics.ListAPIView):
    pagination_class = PartyPagination
    serializer_class = PartySerializer
    search_fields = ('user__email', 'user__full_name',
                     'attendees__email', 'attendees__full_name',
                     'requesters__email', 'requesters__full_name',)
    ordering_fields = ('created',)

    def get_queryset(self):
        return Party.objects.own_parties_hosting(
            user=self.request.user, viewing_user=self.request.user
        )


class UserPartyListAPIView(DefaultsMixin, FiltersMixin, generics.ListAPIView):
    pagination_class = PartyPagination
    serializer_class = PartySerializer
    search_fields = ('user__email', 'user__full_name',
                     'attendees__email', 'attendees__full_name',
                     'requesters__email', 'requesters__full_name',)
    ordering_fields = ('created',)

    def get_queryset(self):
        return Party.objects.own_parties_hosting(
            user=MyUser.objects.get(pk=self.kwargs['user_pk']),
            viewing_user=self.request.user)


@api_view(['POST'])
def party_attend_api(request, party_pk):
    user = request.user
    party = get_object_or_404(Party, pk=party_pk)
    party_creator = party.user

    if user in party.attendees.all():
        pass
    elif party.invite_type == Party.REQUEST_APPROVAL:
        if user == party_creator:
            party.attendees.add(user)
        else:
            party.requesters.add(user)
            notify.send(
                user,
                recipient=party_creator,
                verb='has requested to attend your event.',
                target=party,
            )

            # Push notifications
            try:
                device = APNSDevice.objects.get(user=party_creator)
            except APNSDevice.DoesNotExist:
                device = None

            if device:
                device.send_message(
                    "{} has requested to attend your event.".format(user),
                    sound='default'
                )
    elif party.invite_type == Party.OPEN:
        party.attendees.add(user)
        if user != party_creator:
            notify.send(
                user,
                recipient=party_creator,
                verb='will be attending your event.',
                target=party,
            )

            # Push notifications
            try:
                device = APNSDevice.objects.get(user=party_creator)
            except APNSDevice.DoesNotExist:
                device = None

            if device:
                device.send_message(
                    "{} will be attending your event.".format(user),
                    sound='default'
                )

            feed_item.send(
                user,
                verb='attending {}\'s event.'.format(
                    party_creator.get_full_name),
                target=party,
            )
    elif party.invite_type == Party.INVITE_ONLY and user in party.invited_users.all():
        party.attendees.add(user)
        if user != party_creator:
            notify.send(
                user,
                recipient=party_creator,
                verb='will be attending your event.',
                target=party,
            )

            # Push notifications
            try:
                device = APNSDevice.objects.get(user=party_creator)
            except APNSDevice.DoesNotExist:
                device = None

            if device:
                device.send_message(
                    "{} will be attending your event.".format(user),
                    sound='default'
                )

            feed_item.send(
                user,
                verb='attending {}\'s event.'.format(
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
        verb='has accepted your request to attend.',
        target=party,
    )

    # Push notifications
    try:
        device = APNSDevice.objects.get(user=user)
    except APNSDevice.DoesNotExist:
        device = None

    if device:
        device.send_message(
            "{} has accepted your request to attend.".format(party_creator),
            sound='default'
        )

    feed_item.send(
        user,
        verb='attending {}\'s event.'.format(party_creator.get_full_name),
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


########################################################################
# SEARCH                                                               #
########################################################################
class SearchListAPIView(CacheMixin, DefaultsMixin, FiltersMixin,
                        generics.ListAPIView):
    serializer_class = SearchMyUserSerializer
    # '^' Starts-with search
    # '=' Exact matches
    # '$' Regex search
    search_fields = ('^full_name',)

    def get_queryset(self):
        return MyUser.objects.exclude(pk=self.request.user.pk).filter(
            is_active=True).only('id', 'full_name', 'profile_pic')
