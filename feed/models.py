from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from accounts.models import Follower
from core.models import TimeStampedModel

# Create your models here.


class FeedManager(models.Manager):
    def all_for_user(self, user):
        """
        Returns all of the feed items for the user.
        """
        try:
            follow = Follower.objects.select_related('user').get(user=user)
        except Follower.DoesNotExist:
            follow = None

        # own_feed = self.own_for_user(user=user)
        own_feed = self.filter(sender_object_id=user.id)

        if follow and follow.following.count() > 0:
            # following_feed = self.following_for_user(user=user)
            following_feed = self.filter(
                sender_object_id__in=user.follower.following.values('user_id'))
            return (own_feed | following_feed).distinct()
        return own_feed


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
        return "%(verb)s" % context

    @property
    def time_since(self):
        return naturaltime(self.created)
