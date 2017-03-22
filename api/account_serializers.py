from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from accounts.models import Follower, MyUser, Photo
from parties.models import Party


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


class PhotoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('photo',)


class PhotoSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.CharField(source='user.full_name', read_only=True)
    user_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ('id', 'user', 'user_url', 'photo', 'created', 'modified',)

    def get_user_url(self, obj):
        return api_reverse('user_account_detail_api',
                           kwargs={'user_pk': obj.user.pk},
                           request=self.context['request'])


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
    follower = FollowerSerializer(read_only=True)
    event_count = serializers.SerializerMethodField()
    event_images = serializers.SerializerMethodField()
    viewer_can_see = serializers.SerializerMethodField(read_only=True)
    photos = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ('id', 'account_url', 'gender', 'full_name', 'email',
                  'profile_pic', 'photos', 'bio', 'birthday', 'phone_number',
                  'location', 'viewer_can_see', 'follower', 'event_count',
                  'event_images',)

    def get_account_url(self, obj):
        request = self.context['request']
        return api_reverse('user_account_detail_api',
                           kwargs={'user_pk': obj.pk}, request=request)

    def get_gender(self, obj):
        return dict(MyUser.GENDER_CHOICES)[obj.gender]

    def get_event_count(self, obj):
        count = Party.objects.own_parties_hosting(user=obj).count()
        if count == 0:
            return '0'
        return str(count)

    def get_event_images(self, obj):
        return Party.objects.own_parties_hosting(user=obj).values(
            'id', 'image')

    def get_photos(self, obj):
        queryset = Photo.objects.filter(user=obj)
        serializer = PhotoSerializer(queryset, context=self.context, many=True,
                                     read_only=True)
        return serializer.data

    def get_viewer_can_see(self, obj):
        viewing_user = self.context['request'].user
        if obj.is_private and viewing_user not in obj.follower.followers.all():
            return False
        return True
