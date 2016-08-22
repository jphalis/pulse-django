from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from accounts.models import Follower, MyUser


class FollowerCreateSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Follower
        fields = ('user', 'followers',)


class FollowerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Follower
        fields = ('get_followers_count', 'get_following_count',
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
    follower = FollowerSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = MyUser
        fields = ('id', 'account_url', 'gender', 'full_name', 'email',
                  'profile_pic', 'date_joined', 'modified',
                  'is_private', 'is_active', 'follower',)

    def get_account_url(self, obj):
        request = self.context['request']
        kwargs = {'pk': obj.pk}
        return api_reverse('user_account_detail_api', kwargs=kwargs,
                           request=request)
