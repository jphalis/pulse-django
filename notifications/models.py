from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from core.models import TimeStampedModel

# Create your models here.


class NotificationManager(models.Manager):
    def all_for_user(self, user):
        """
        Returns all of the notifications for the user.
        """
        return super(NotificationManager, self).get_queryset().filter(
            recipient=user)

    def read_for_user(self, user):
        """
        Returns all of the read notifications for the user.
        """
        return super(NotificationManager, self).get_queryset().filter(
            recipient=user, read=True)

    def unread_for_user(self, user):
        """
        Returns all of the unread notifications for the user.
        """
        return super(NotificationManager, self).get_queryset().filter(
            recipient=user, read=False)

    def get_recent_for_user(self, user, num):
        """
        Returns N (num) recent notifications for the user.
        """
        return super(NotificationManager, self).get_queryset().filter(
            recipient=user)[:num]

    def mark_all_read(self, user):
        return super(NotificationManager, self).get_queryset() \
            .filter(recipient=user).update(read=True)


@python_2_unicode_compatible
class Notification(TimeStampedModel):
    sender_content_type = models.ForeignKey(ContentType,
                                            related_name='nofity_sender')
    sender_object_id = models.PositiveIntegerField()
    sender_object = GenericForeignKey("sender_content_type",
                                      "sender_object_id")
    verb = models.CharField(max_length=255)

    action_content_type = models.ForeignKey(ContentType,
                                            related_name='notify_action',
                                            null=True, blank=True)
    action_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_object = GenericForeignKey("action_content_type",
                                      "action_object_id")

    target_content_type = models.ForeignKey(ContentType,
                                            related_name='notify_target',
                                            null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = GenericForeignKey("target_content_type",
                                      "target_object_id")

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='notifications')
    read = models.BooleanField(default=False)

    objects = NotificationManager()

    class Meta:
        ordering = ['-created']
        app_label = 'notifications'

    def __str__(self):
        context = {
            "action": self.action_object,
            "sender": self.sender_object,
            "target": self.target_object,
            "verb": self.verb,
        }

        if self.target_object:
            if self.action_object:
                if self.verb == "commented":
                    return "%(verb)s: '%(action)s'" % context
                return "%(verb)s %(action)s" % context
            return "%(verb)s" % context
        return "%(verb)s" % context
