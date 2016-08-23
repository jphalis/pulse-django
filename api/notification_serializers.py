from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from notifications.models import Notification


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    sender = serializers.CharField(source='sender_object', read_only=True)
    sender_url = serializers.SerializerMethodField()
    sender_profile_picture = serializers.ReadOnlyField(
        source="sender_object.user_profile_pic")
    target_url = serializers.SerializerMethodField()
    recipient_url = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'sender', 'sender_url', 'sender_profile_picture',
                  '__str__', 'target_url', 'recipient_url', 'read',
                  'created', 'modified',)

    def get_recipient_url(self, obj):
        request = self.context['request']
        kwargs = {'pk': obj.recipient.pk}
        return api_reverse('user_account_detail_api', kwargs=kwargs,
                           request=request)

    def get_sender_url(self, obj):
        request = self.context['request']
        kwargs = {'pk': obj.sender_object.pk}
        return api_reverse('user_account_detail_api', kwargs=kwargs,
                           request=request)

    def get_target_url(self, obj):
        request = self.context['request']
        if obj.target_object:
            view_name = "party_detail_api"
            kwargs = {'pk': obj.target_object.pk}
            return api_reverse(view_name, kwargs=kwargs, request=request)
        return None
