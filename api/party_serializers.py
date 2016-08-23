from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from parties.models import Party


class PartySerializer(serializers.HyperlinkedModelSerializer):
    party_url = serializers.SerializerMethodField()
    user = serializers.CharField(source='user.full_name', read_only=True)
    user_url = serializers.SerializerMethodField()
    user_profile_pic = serializers.ImageField(source='user.profile_pic')

    class Meta:
        model = Party
        fields = ('id', 'party_url', 'user', 'user_url',
                  'user_profile_pic', 'party_type', 'name', 'location',
                  'party_size', 'party_month', 'party_day', 'start_time',
                  'end_time', 'description', 'image', 'created', 'modified',
                  'get_attendees_info', 'attendees_count')

    def get_party_url(self, obj):
        return api_reverse('party_detail_api',
                           kwargs={'pk': obj.pk},
                           request=self.context['request'])

    def get_user_url(self, obj):
        return api_reverse('user_account_detail_api',
                           kwargs={'pk': obj.user.pk},
                           request=self.context['request'])


class PartyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ('id', 'party_type', 'name', 'location', 'party_size',
                  'party_month', 'party_day', 'start_time', 'end_time',
                  'description', 'image',)
