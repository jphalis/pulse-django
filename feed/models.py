from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from core.models import TimeStampedModel

# Create your models here.


class FeedManager(models.Manager):
    def all_for_sender(self, sender):
        """
        Returns all of the feed items for the sender.
        """
        return super(FeedManager, self).get_queryset() \
            .filter(sender_object=sender)

    def get_recent_for_sender(self, sender, num):
        r"""
        Returns N (num) recent feed items for the sender.
        """
        return super(FeedManager, self).get_queryset() \
            .filter(sender_object=sender)[:num]


@python_2_unicode_compatible
class Feed(TimeStampedModel):
    sender_content_type = models.ForeignKey(ContentType,
                                            related_name='feed_sender')
    sender_object_id = models.PositiveIntegerField()
    sender_object = GenericForeignKey("sender_content_type",
                                      "sender_object_id")
    verb = models.CharField(max_length=255)

    action_content_type = models.ForeignKey(ContentType,
                                            related_name='feed_action',
                                            null=True, blank=True)
    action_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_object = GenericForeignKey("action_content_type",
                                      "action_object_id")

    target_content_type = models.ForeignKey(ContentType,
                                            related_name='feed_target',
                                            null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = GenericForeignKey("target_content_type",
                                      "target_object_id")

    objects = FeedManager()

    class Meta:
        ordering = ['-created']
        app_label = 'feed'

    def __str__(self):
        context = {
            # "action": self.action_object,
            "sender": self.sender_object,
            "target": self.target_object,
            "verb": self.verb,
        }
        return "%(sender)s %(verb)s" % context
