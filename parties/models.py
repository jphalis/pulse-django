from __future__ import unicode_literals

from datetime import date

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel

# Create your models here.


def party_image_upload_loc(instance, filename):
    """Stores the party images in party_images/<filename>."""
    return "party_images/{}".format(filename)


class PartyManager(models.Manager):
    def active(self):
        """Returns all active parties."""
        return super(PartyManager, self).get_queryset() \
            .filter(is_active=True)

    def own_parties_hosting(self, user, viewing_user):
        """Returns all of the parties the user is/has hosted."""
        qs = super(PartyManager, self).get_queryset().filter(user=user)

        to_remove_ids = []

        for party in qs:
            # viewing user cannot be the party creator
            # party must be invite only
            # viewing user cannot be attending the party
            # viewing user cannot be already invited
            # if any fail, show the party
            # if they all pass, hide the party
            if (viewing_user != party.user and
                party.invite_type == Party.INVITE_ONLY and
                not party.attendees.filter(id=viewing_user.id).exists() and
                not party.invited_users.filter(id=viewing_user.id).exists()):

                to_remove_ids.append(party.id)
        return qs.exclude(id__in=to_remove_ids).order_by(
            '-is_active', 'party_year', 'party_month', 'party_day',
            '-start_time'
        )

    def own_parties_attending(self, user):
        """Returns all of the parties the user is attending."""
        return super(PartyManager, self).get_queryset().filter(attendees=user)

    def party_create(self, user, party_type, invite_type, name, location,
                     party_size, party_month, party_day, start_time,
                     recurrence, end_time=None, description=None, image=None,
                     **extra_fields):
        """Creates a party."""
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

        party = self.model(
            user=user,
            party_type=party_type,
            name=name,
            location=location,
            party_size=party_size,
            party_month=party_month,
            party_day=party_day,
            start_time=start_time,
            recurrence=recurrence,
            end_time=end_time,
            description=description,
            image=image,
            **extra_fields
        )
        party.save(using=self._db)
        party.attendees.add(user)
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
    REQUEST_APPROVAL = 17

    NONE = 20
    DAILY = 21
    WEEKLY = 22
    MONTHLY = 23

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
        (REQUEST_APPROVAL, _('Request + approval')),
    )
    RECURRENCE_TYPES = (
        (NONE, _('None')),
        (DAILY, _('Daily')),
        (WEEKLY, _('Weekly')),
        (MONTHLY, _('Monthly')),
    )

    party_type = models.IntegerField(choices=PARTY_TYPES, default=CUSTOM)
    invite_type = models.IntegerField(choices=INVITE_TYPES, default=OPEN)
    recurrence = models.IntegerField(choices=RECURRENCE_TYPES, default=NONE)
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
    end_time = models.TimeField(verbose_name='End Time', blank=True, null=True)
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
    invited_users = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           related_name='invited_users',
                                           blank=True)
    likers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                    related_name='likers',
                                    blank=True)

    is_active = models.BooleanField(_('active'), default=True)

    objects = PartyManager()

    class Meta:
        app_label = 'parties'
        verbose_name = _('party')
        verbose_name_plural = _('parties')
        ordering = ['-created']

    def __str__(self):
        return str(self.user.get_full_name)

    @cached_property
    def get_attendees_info(self):
        """Returns the information for each attendee of the party."""
        return self.attendees.values('id', 'full_name', 'profile_pic',)

    @cached_property
    def get_requesters_info(self):
        """Returns the information for each requester of the party."""
        return self.requesters.values('id', 'full_name', 'profile_pic',)

    @cached_property
    def get_likers_info(self):
        """Returns the information for each liker of the party."""
        return self.likers.values('id', 'full_name',)

    @cached_property
    def get_invited_users_info(self):
        """Returns the information for each invited user of the party."""
        return self.invited_users.values('id', 'full_name', 'profile_pic',)

    @property
    def attendees_count(self):
        """Returns the number of attendees of the party."""
        return str(self.get_attendees_info.count())

    @property
    def requesters_count(self):
        """Returns the number of requesters of the party."""
        return str(self.get_requesters_info.count())
