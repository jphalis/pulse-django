from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel
from core.utils import readable_number


def profile_pic_upload_loc(instance, filename):
    """
    Stores the profile picture in <user_id>/profile_pictures/<filename>.
    """
    return "{0}/profile_pictures/{1}".format(instance.id, filename)


class MyUserManager(BaseUserManager):
    def _create_user(self, email, password, full_name,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()

        if not email:
            raise ValueError('Users must have an email.')
        elif not full_name:
            raise ValueError('Users must have a name.')

        email = self.normalize_email(email)

        user = self.model(email=email, full_name=full_name,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, full_name, password=None, **extra_fields):
        return self._create_user(email, password, full_name,
                                 is_staff=False, is_superuser=False,
                                 **extra_fields)

    def create_superuser(self, email, full_name, password, **extra_fields):
        return self._create_user(email, password, full_name,
                                 is_staff=True, is_superuser=True,
                                 **extra_fields)


@python_2_unicode_compatible
class MyUser(AbstractBaseUser, PermissionsMixin):
    MALE = 0
    FEMALE = 1
    NO_ANSWER = 2
    GENDER_CHOICES = (
        (MALE, _('Male')),
        (FEMALE, _('Female')),
        (NO_ANSWER, _('Prefer not to answer')),
    )
    gender = models.IntegerField(choices=GENDER_CHOICES, default=NO_ANSWER)
    full_name = models.CharField(_('full name'), max_length=100)
    email = models.EmailField(max_length=120, unique=True)
    profile_pic = models.ImageField(_('profile picture'),
                                    upload_to=profile_pic_upload_loc,
                                    blank=True)

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    modified = models.DateTimeField(_('last modified'), auto_now=True)

    blocking = models.ManyToManyField('self', related_name='blocked_by',
                                      symmetrical=False)
    is_private = models.BooleanField(_('private'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = MyUserManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.full_name

    @cached_property
    def get_full_name(self):
        """
        Returns the full name of the user.
        """
        return self.full_name

    @cached_property
    def get_short_name(self):
        """
        Returns the first name for the user.
        """
        return self.full_name.split()[0]

    @property
    def user_profile_pic(self):
        """
        Returns the profile picture of a user. If there is no profile picture,
        a default one will be rendered.
        """
        if self.profile_pic:
            return "{0}{1}".format(settings.MEDIA_URL, self.profile_pic)
        return settings.STATIC_URL + 'img/default-profile-pic.jpg'

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to the user.
        """
        send_mail(subject, message, from_email, [self.email])

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        return True

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        return True


@python_2_unicode_compatible
class Follower(TimeStampedModel):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    followers = models.ManyToManyField('self', related_name='following',
                                       symmetrical=False)

    class Meta:
        app_label = 'accounts'
        ordering = ['-created']

    def __str__(self):
        return self.user.full_name

    @cached_property
    def get_followers_info(self):
        return self.followers.select_related('user').values(
            'user__id', 'user__full_name', 'user__profile_pic')

    @cached_property
    def get_following_info(self):
        return self.following.select_related('user').values(
            'user__id', 'user__full_name', 'user__profile_pic')

    def short_followers_count(self):
        return readable_number(self.get_followers_info.count(), short=True)

    def short_following_count(self):
        return readable_number(self.get_following_info.count(), short=True)

    def followers_count(self):
        return str(self.get_followers_info.count())

    def following_count(self):
        return str(self.get_following_info.count())

MyUser.profile = property(lambda u: Follower.objects.get_or_create(user=u)[0])
