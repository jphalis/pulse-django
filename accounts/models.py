from __future__ import unicode_literals

try:
    from urllib.parse import urlencode
except ImportError:  # python 2
    from urllib import urlencode

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _


def profile_pic_upload_loc(instance, filename):
    """
    Stores the profile picture in username/profile_pictures/filename.
    """
    return "{0}/profile_pictures/{1}".format(instance.username, filename)


class MyUserManager(BaseUserManager):
    def _create_user(self, email, password, first_name, last_name,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()

        if not email:
            raise ValueError('Users must have an email.')

        email = self.normalize_email(email)

        user = self.model(email=email,
                          first_name=first_name,
                          last_name=last_name,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, first_name=None,
                    last_name=None, **extra_fields):
        return self._create_user(email, password, first_name, last_name,
                                 is_staff=False, is_superuser=False,
                                 **extra_fields)

    def create_superuser(self, email, password, first_name=None,
                         last_name=None, **extra_fields):
        return self._create_user(email, password, first_name, last_name,
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
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    email = models.EmailField(max_length=120, unique=True)
    profile_pic = models.ImageField(_('profile picture'),
                                    upload_to=profile_pic_upload_loc,
                                    blank=True)

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    modified = models.DateTimeField(_('last modified'), auto_now=True)

    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = MyUserManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    # def get_absolute_url(self):
    #     """
    #     Returns the url for the user.
    #     """
    #     return reverse('profile', kwargs={"username": self.username})

    @cached_property
    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return '{0} {1}'.format(self.first_name, self.last_name)

    @cached_property
    def get_short_name(self):
        """
        Returns the first name for the user.
        """
        return self.first_name

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
