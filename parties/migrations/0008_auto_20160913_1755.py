# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-13 17:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parties', '0007_auto_20160913_0909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='invite_type',
            field=models.IntegerField(choices=[(15, 'Open'), (16, 'Invite only'), (17, 'Request + approval')], default=15),
        ),
    ]