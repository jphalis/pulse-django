from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from accounts.models import MyUser


class SearchMyUserSerializer(serializers.HyperlinkedModelSerializer):
    account_url = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ('id', 'account_url', 'full_name', 'profile_pic',)

    def get_account_url(self, obj):
        request = self.context['request']
        return api_reverse('user_account_detail_api',
                           kwargs={'user_pk': obj.pk}, request=request)
