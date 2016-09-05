from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from parties.models import Party


class PartySerializer(serializers.HyperlinkedModelSerializer):
    party_url = serializers.SerializerMethodField()
    user = serializers.CharField(source='user.full_name', read_only=True)
    user_profile_pic = serializers.ImageField(source='user.profile_pic')
    party_type = serializers.SerializerMethodField()
    party_size = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = Party
        fields = ('id', 'party_url', 'user', 'user_profile_pic',
                  'party_type', 'name', 'location', 'party_size',
                  'party_month', 'party_day', 'start_time',
                  'end_time', 'description', 'image',
                  'attendees_count', 'get_attendees_info',)

    def get_party_url(self, obj):
        return api_reverse('party_detail_api',
                           kwargs={'party_pk': obj.pk},
                           request=self.context['request'])

    def get_user_url(self, obj):
        return api_reverse('user_account_detail_api',
                           kwargs={'user_pk': obj.user.pk},
                           request=self.context['request'])

    def get_party_type(self, obj):
        return dict(Party.PARTY_TYPES)[obj.party_type]

    def get_party_size(self, obj):
        return dict(Party.PARTY_SIZES)[obj.party_size]

    def get_start_time(self, obj):
        # %l:%M %p (removes leading 0)
        return obj.start_time.strftime("%I:%M %p")

    def get_end_time(self, obj):
        # %l:%M %p (removes leading 0)
        return obj.end_time.strftime("%I:%M %p")


class PartyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ('id', 'party_type', 'name', 'location', 'party_size',
                  'party_month', 'party_day', 'start_time', 'end_time',
                  'description', 'image',)
