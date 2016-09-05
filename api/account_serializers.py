from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from accounts.models import Follower, MyUser
from parties.models import Party
from .party_serializers import PartySerializer


class FollowerCreateSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Follower
        fields = ('user', 'followers',)


class FollowerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Follower
        fields = ('followers_count', 'following_count',
                  'get_followers_info', 'get_following_info',)


class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'email', 'full_name', 'password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = MyUser.objects.create_user(
            email=validated_data['email'].lower(),
            full_name=validated_data['full_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class MyUserSerializer(serializers.HyperlinkedModelSerializer):
    account_url = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    is_private = serializers.BooleanField(read_only=True)
    follower = FollowerSerializer(read_only=True)
    event_count = serializers.SerializerMethodField()
    event_images = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ('id', 'account_url', 'gender', 'full_name', 'email',
                  'profile_pic', 'is_private', 'follower', 'event_count',
                  'event_images',)

    def get_account_url(self, obj):
        request = self.context['request']
        kwargs = {'user_pk': obj.pk}
        return api_reverse('user_account_detail_api', kwargs=kwargs,
                           request=request)

    def get_gender(self, obj):
        return dict(MyUser.GENDER_CHOICES)[obj.gender]

    def get_event_count(self, obj):
        return str(Party.objects.own_parties_hosting(user=obj).count())

    def get_event_images(self, request):
        return Party.objects.own_parties_hosting(user=request).values('image')
