# -*- coding: utf-8 -*-
# Generated by Django 1.11.dev20161116224037 on 2016-11-17 13:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('push_notifications', '0004_fcm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gcmdevice',
            name='cloud_message_type',
            field=models.CharField(choices=[('GCM', 'Google Cloud Message'), ('FCM', 'Firebase Cloud Message')], default='GCM', help_text='You should choose GCM or FCM', max_length=3, verbose_name='Cloud Message Type'),
        ),
    ]
