from django.shortcuts import get_object_or_404

from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response as RestResponse
from rest_framework.reverse import reverse as api_reverse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from accounts.models import Follower, MyUser
from core.mixins import AdminRequiredMixin, CacheMixin
# from notifications.signals import notify
from parties.models import Party
from .account_serializers import (AccountCreateSerializer, FollowerSerializer,
                                  MyUserSerializer)
from .auth_serializers import (PasswordResetSerializer,
                               PasswordResetConfirmSerializer,
                               PasswordChangeSerializer)
from .mixins import DefaultsMixin, FiltersMixin
from .pagination import AccountPagination, PartyPagination
from .party_serializers import PartyCreateSerializer, PartySerializer
from .permissions import IsOwnerOrReadOnly, MyUserIsOwnerOrReadOnly

# Create your views here.


class APIHomeView(AdminRequiredMixin, CacheMixin, DefaultsMixin, APIView):
    cache_timeout = 60 * 60 * 24 * 30

    def get(self, request, format=None):
        data = {
            'authentication': {
                'login': api_reverse('auth_login_api', request=request),
                'password_reset': api_reverse('rest_password_reset',
                                              request=request),
                'password_change': api_reverse('rest_password_change',
                                               request=request)
            },
            'accounts': {
                'count': MyUser.objects.all().count(),
                'url': api_reverse('user_account_list_api', request=request),
                'create_url': api_reverse('account_create_api',
                                          request=request),
                'profile_url': api_reverse(
                    'user_account_detail_api', request=request,
                    kwargs={'pk': request.user.pk}),
            },
            'parties': {
                'count': Party.objects.active().count(),
                'url': api_reverse('party_list_api', request=request),
                'create_url': api_reverse('party_create_api',
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
        user_pk = self.kwargs["pk"]
        return get_object_or_404(MyUser, pk=user_pk)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


@api_view(['POST'])
def follow_create_api(request, user_pk):
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
        # notify.send(
        #     request.user,
        #     recipient=user,
        #     verb='is now supporting you'
        # )

    serializer = FollowerSerializer(followed, context={'request': request})
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
# PARTIES                                                              #
########################################################################
class PartyCreateAPIView(ModelViewSet):
    queryset = Party.objects.active()
    serializer_class = PartyCreateSerializer
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        party_type=self.request.data.get('party_type'),
                        name=self.request.data.get('name'),
                        location=self.request.data.get('location'),
                        party_size=self.request.data.get('party_size'),
                        party_month=self.request.data.get('party_month'),
                        party_day=self.request.data.get('party_day'),
                        start_time=self.request.data.get('start_time'),
                        end_time=self.request.data.get('end_time'),
                        description=self.request.data.get('description'),
                        image=self.request.data.get('image'),)


class PartyDetailAPIView(CacheMixin,
                         generics.RetrieveAPIView,
                         mixins.DestroyModelMixin,
                         mixins.UpdateModelMixin):
    cache_timeout = 60 * 7
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly,)
    serializer_class = PartySerializer

    def get_object(self):
        party_pk = self.kwargs["party_pk"]
        obj = get_object_or_404(Party, pk=party_pk)
        if obj.party_expired:
            obj.is_active = False
            obj.save()
        return obj

    def delete(self, request, *args, **kwargs):
        party_pk = self.kwargs["party_pk"]
        obj = get_object_or_404(Party, pk=party_pk)
        if request.user == obj.user:
            return self.destroy(request, *args, **kwargs)
        raise PermissionDenied(
            {"message": "You don't have permission to access this"})

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class PartyListAPIView(CacheMixin, DefaultsMixin, FiltersMixin,
                       generics.ListAPIView):
    cache_timeout = 60 * 60 * 24
    pagination_class = PartyPagination
    serializer_class = PartySerializer
    search_fields = ('user__email', 'user__get_full_name',
                     'attendees__email', 'attendees__get_full_name',)
    ordering_fields = ('created', 'modified',)

    def get_queryset(self):
        return Party.objects.active()
