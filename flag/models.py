from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from parties.models import Party


class Flag(TimeStampedModel):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    party = models.ForeignKey(Party)
    comment = models.TextField(null=True, blank=True)
    resolved = models.BooleanField(default=False)
    flag_count = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'flag'
