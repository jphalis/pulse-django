# from django.conf import settings
# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import EmailMultiAlternatives
# from django.template import loader
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode

# from rest_framework import serializers
# from rest_framework.reverse import reverse as api_reverse

# from accounts.models import MyUser


# class AccountCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MyUser
#         fields = ('id', 'email', 'password',)
#         extra_kwargs = {'password': {'write_only': True}}

#     def send_mail(self, subject_template_name, email_template_name,
#                   context, from_email, to_email, html_email_template_name):
#         """
#         Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
#         """
#         subject = subject_template_name
#         # Email subject *must not* contain newlines
#         subject = ''.join(subject.splitlines())
#         body = loader.render_to_string(email_template_name, context)
#         email_message = EmailMultiAlternatives(subject, body,
#                                                from_email, [to_email])
#         if html_email_template_name is not None:
#             html_email = loader.render_to_string(html_email_template_name,
#                                                  context)
#             email_message.attach_alternative(html_email, 'text/html')
#         email_message.send()

#     def create(self, validated_data,
#                subject_template_name='Wipp Email Confirmation',
#                email_template_name='accounts/email_confirm_message.html',
#                use_https=False, token_generator=default_token_generator,
#                from_email=settings.FROM_EMAIL, extra_email_context=None,
#                html_email_template_name='accounts/email_confirm_message.html'):
#         user = MyUser.objects.create(
#             email=validated_data['email'].lower()
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         request = self.context['request']

#         context = {
#             'email': user.email,
#             'domain': request.get_host(),
#             'site_name': request.META['SERVER_NAME'],
#             'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#             'user': user,
#             'token': token_generator.make_token(user),
#             'protocol': 'https' if use_https else 'http',
#         }
#         if extra_email_context is not None:
#             context.update(extra_email_context)
#         self.send_mail(subject_template_name, email_template_name,
#                        context, from_email, user.email,
#                        html_email_template_name=html_email_template_name)
#         return user


# class MyUserSerializer(serializers.HyperlinkedModelSerializer):
#     account_url = serializers.SerializerMethodField()
#     is_active = serializers.BooleanField(read_only=True)
#     is_admin = serializers.BooleanField(read_only=True)
#     is_driver = serializers.SerializerMethodField()

#     class Meta:
#         model = MyUser
#         fields = ('id', 'account_url', 'email', 'full_name', 'profile_picture',
#                   'phone_number', 'university', 'is_active', 'is_admin',
#                   'is_driver', 'date_joined', 'modified',)

#     def get_account_url(self, obj):
#         request = self.context['request']
#         kwargs = {'id': obj.id}
#         return api_reverse('user_account_detail_api', kwargs=kwargs,
#                            request=request)
