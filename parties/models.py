from __future__ import unicode_literals

from datetime import date

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel

# Create your models here.


def party_image_upload_loc(instance, filename):
    """
    Stores the party images in <user_id>/party_images/<filename>.
    """
    return "{0}/party_images/{1}".format(instance.id, filename)


class PartyManager(models.Manager):
    def active(self):
        """
        Returns all active parties.
        """
        return super(PartyManager, self).get_queryset() \
            .filter(is_active=True) \
            .select_related('user') \
            .prefetch_related('attendees')

    def own_parties_hosting(self, user):
        """
        Returns all of the parties the user is/has hosted.
        """
        return super(PartyManager, self).get_queryset() \
            .filter(user=user) \
            .select_related('user') \
            .prefetch_related('attendees')

    def own_parties_attending(self, user):
        """
        Returns all of the parties the user is attending.
        """
        return super(PartyManager, self).get_queryset() \
            .filter(attendees=user) \
            .select_related('user') \
            .prefetch_related('attendees')

    def party_create(self, user, party_type, name, location, party_size,
                     party_month, party_day, start_time, end_time,
                     description=None, image=None, **extra_fields):
        """
        Creates a party.
        """
        if not user:
            raise ValueError('There must be a user assigned to this party.')
        elif not party_type:
            raise ValueError('There must be a party type.')
        elif not name:
            raise ValueError('There must be a party name.')
        elif not location:
            raise ValueError('There must be a location for the party.')
        elif not party_size:
            raise ValueError('There must be a size for the party.')
        elif not party_month:
            raise ValueError('There must be a month for the party.')
        elif not party_day:
            raise ValueError('There must be a day for the party.')
        elif not start_time:
            raise ValueError('There must be a start time for the party.')
        elif not end_time:
            raise ValueError('There must be an end time for the party.')

        party = self.model(user=user,
                           party_type=party_type,
                           name=name,
                           location=location,
                           party_size=party_size,
                           party_month=party_month,
                           party_day=party_day,
                           start_time=start_time,
                           end_time=end_time,
                           description=description,
                           image=image,
                           **extra_fields)
        party.save(using=self._db)
        party.attendees.add(user)
        party.save()
        return party


@python_2_unicode_compatible
class Party(TimeStampedModel):
    CUSTOM = 0
    SOCIAL = 1
    HOLIDAY = 2
    EVENT = 3
    RAGER = 4
    THEMED = 5
    CELEBRATION = 6

    SMALL = 10
    MEDIUM = 11
    LARGE = 12

    OPEN = 15
    INVITE_ONLY = 16

    PARTY_TYPES = (
        (CUSTOM, _('Custom')),
        (SOCIAL, _('Social')),
        (HOLIDAY, _('Holiday')),
        (EVENT, _('Event')),
        (RAGER, _('Rager')),
        (THEMED, _('Themed')),
        (CELEBRATION, _('Celebration')),
    )
    PARTY_SIZES = (
        (SMALL, _('Small')),
        (MEDIUM, _('Medium')),
        (LARGE, _('Large')),
    )
    INVITE_TYPES = (
        (OPEN, _('Open')),
        (INVITE_ONLY, _('Invite only')),
    )

    party_type = models.IntegerField(choices=PARTY_TYPES, default=CUSTOM)
    invite_type = models.IntegerField(choices=INVITE_TYPES, default=OPEN)
    name = models.CharField(max_length=80)
    location = models.CharField(max_length=240)
    latitude = models.DecimalField(max_digits=12, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=8, null=True)
    party_size = models.IntegerField(choices=PARTY_SIZES, default=SMALL)
    party_month = models.PositiveIntegerField(
        validators=[MaxValueValidator(12)])
    party_day = models.PositiveIntegerField(
        validators=[MaxValueValidator(31)])
    party_year = models.PositiveIntegerField(default=date.today().year)
    start_time = models.TimeField(verbose_name='Start Time')
    end_time = models.TimeField(verbose_name='End Time')
    description = models.TextField(max_length=500, blank=True)
    image = models.ImageField(_('party image'), blank=True,
                              upload_to=party_image_upload_loc)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='party_creator',
                             on_delete=models.CASCADE)
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name='party_attendees',
                                       blank=True)
    requesters = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='party_requesters',
                                        blank=True)

    is_active = models.BooleanField(_('active'), default=True)

    objects = PartyManager()

    class Meta:
        app_label = 'parties'
        verbose_name = _('party')
        verbose_name_plural = _('parties')
        ordering = ['-created']

    def __str__(self):
        return u'{0}'.format(self.user.get_full_name)

    @cached_property
    def get_attendees_info(self):
        """
        Returns the information for each attendee at the party.
        """
        return self.attendees.values('id', 'full_name', 'profile_pic',)

    @cached_property
    def get_requesters_info(self):
        """
        Returns the information for each requester at the party.
        """
        return self.requesters.values('id', 'full_name', 'profile_pic',)

    @property
    def attendees_count(self):
        """
        Returns the number of attendees of the party.
        """
        return str(self.get_attendees_info.count())

    @property
    def requesters_count(self):
        """
        Returns the number of requesters of the party.
        """
        return str(self.get_requesters_info.count())

    def party_expired(self):
        expires_on = date(
            date.today().year, self.party_month, self.party_day)
        return expires_on <= timezone.now()
    party_expired.boolean = True
