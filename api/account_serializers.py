from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from accounts.models import MyUser


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
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = MyUser
        fields = ('id', 'account_url', 'gender', 'full_name', 'email',
                  'profile_pic', 'date_joined', 'modified',
                  'is_private', 'is_active',)

    def get_account_url(self, obj):
        request = self.context['request']
        kwargs = {'id': obj.id}
        return api_reverse('user_account_detail_api', kwargs=kwargs,
                           request=request)
