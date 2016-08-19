# from django.conf import settings
# from django.utils.encoding import force_text
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.contrib.auth.tokens import default_token_generator

# from rest_framework import serializers
# from rest_framework.authtoken.models import Token
# from rest_framework.exceptions import ValidationError

# from accounts.forms import PasswordResetForm, SetPasswordForm
# from accounts.models import MyUser


# class TokenSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Token
#         fields = ('key',)


# class PasswordResetSerializer(serializers.Serializer):
#     """
#     Serializer for requesting a password reset e-mail.
#     """
#     email = serializers.EmailField()
#     password_reset_form_class = PasswordResetForm

#     def validate_email(self, value):
#         self.reset_form = self.password_reset_form_class(
#             data=self.initial_data)
#         if not self.reset_form.is_valid():
#             raise serializers.ValidationError(_('Error'))
#         return value

#     def save(self):
#         request = self.context.get('request')
#         opts = {
#             'use_https': request.is_secure(),
#             'from_email': getattr(settings, 'EMAIL_HOST_USER'),
#             'request': request,
#         }
#         self.reset_form.save(**opts)


# class PasswordResetConfirmSerializer(serializers.Serializer):
#     """
#     Serializer for confirming a password reset change from e-mail.
#     """
#     new_password1 = serializers.CharField(max_length=128)
#     new_password2 = serializers.CharField(max_length=128)
#     uid = serializers.CharField(required=True)
#     token = serializers.CharField(required=True)
#     set_password_form_class = SetPasswordForm

#     def validate(self, attrs):
#         self._errors = {}
#         try:
#             uid = force_text(uid_decoder(attrs['uid']))
#             self.user = MyUser._default_manager.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
#             raise ValidationError({'uid': ['Invalid value']})
#         self.custom_validation(attrs)
#         self.set_password_form = self.set_password_form_class(
#             user=self.user, data=attrs)
#         if not self.set_password_form.is_valid():
#             raise serializers.ValidationError(self.set_password_form.errors)
#         if not default_token_generator.check_token(self.user, attrs['token']):
#             raise ValidationError({'token': ['Invalid value']})
#         return attrs

#     def save(self):
#         self.set_password_form.save()


# class PasswordChangeSerializer(serializers.Serializer):
#     old_password = serializers.CharField(max_length=128)
#     new_password1 = serializers.CharField(max_length=128)
#     new_password2 = serializers.CharField(max_length=128)
#     set_password_form_class = SetPasswordForm

#     def __init__(self, *args, **kwargs):
#         self.old_password_field_enabled = True
#         self.logout_on_password_change = False
#         super(PasswordChangeSerializer, self).__init__(*args, **kwargs)
#         if not self.old_password_field_enabled:
#             self.fields.pop('old_password')
#         self.request = self.context.get('request')
#         self.user = getattr(self.request, 'user', None)

#     def validate_old_password(self, value):
#         invalid_password_conditions = (
#             self.old_password_field_enabled,
#             self.user,
#             not self.user.check_password(value)
#         )
#         if all(invalid_password_conditions):
#             raise serializers.ValidationError('Incorrect old password')
#         return value

#     def validate(self, attrs):
#         self.set_password_form = self.set_password_form_class(
#             user=self.user, data=attrs)
#         if not self.set_password_form.is_valid():
#             raise serializers.ValidationError(self.set_password_form.errors)
#         return attrs

#     def save(self):
#         self.set_password_form.save()
#         if not self.logout_on_password_change:
#             from django.contrib.auth import update_session_auth_hash
#             update_session_auth_hash(self.request, self.user)
