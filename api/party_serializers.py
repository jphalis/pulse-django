from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from parties.models import Party


class PartySerializer(serializers.HyperlinkedModelSerializer):
    party_url = serializers.SerializerMethodField()
    user_url = serializers.SerializerMethodField()
    user = serializers.CharField(source='user.full_name', read_only=True)
    user_profile_pic = serializers.ImageField(source='user.profile_pic')
    party_type = serializers.SerializerMethodField()
    invite_type = serializers.SerializerMethodField()
    recurrence = serializers.SerializerMethodField()
    party_size = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = Party
        fields = ('id', 'is_active', 'party_url', 'user_url', 'user',
                  'user_profile_pic', 'party_type', 'invite_type', 'name',
                  'location', 'latitude', 'longitude', 'party_size',
                  'party_month', 'party_day', 'party_year', 'recurrence',
                  'start_time', 'end_time', 'description', 'image',
                  'attendees_count', 'requesters_count', 'get_attendees_info',
                  'get_requesters_info', 'get_invited_users_info',
                  'get_likers_info',)

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

    def get_invite_type(self, obj):
        return dict(Party.INVITE_TYPES)[obj.invite_type]

    def get_recurrence(self, obj):
        return dict(Party.RECURRENCE_TYPES)[obj.recurrence]

    def get_party_size(self, obj):
        return dict(Party.PARTY_SIZES)[obj.party_size]

    def get_start_time(self, obj):
        # %l:%M %p (removes leading 0)
        return obj.start_time.strftime("%I:%M %p")

    def get_end_time(self, obj):
        # %l:%M %p (removes leading 0)
        return obj.end_time.strftime("%I:%M %p") if obj.end_time else None


class PartyCreateSerializer(serializers.ModelSerializer):
    party_url = serializers.SerializerMethodField()

    class Meta:
        model = Party
        fields = ('id', 'party_type', 'name', 'location', 'latitude',
                  'longitude', 'party_size', 'party_month', 'party_day',
                  'party_year', 'start_time', 'recurrence', 'end_time',
                  'description', 'image', 'invite_type', 'party_url',)

    def get_party_url(self, obj):
        return api_reverse('party_detail_api',
                           kwargs={'party_pk': obj.pk},
                           request=self.context['request'])
