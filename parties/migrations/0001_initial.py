# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-18 22:45
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import parties.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Party',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('party_type', models.IntegerField(choices=[(0, 'Custom'), (1, 'Social'), (2, 'Holiday'), (3, 'Event'), (4, 'Rager'), (5, 'Themed'), (6, 'Celebration')], default=0)),
                ('name', models.CharField(max_length=80)),
                ('location', models.CharField(max_length=240)),
                ('party_size', models.IntegerField(choices=[(10, 'Small'), (11, 'Medium'), (12, 'Large')], default=10)),
                ('party_month', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(12)])),
                ('party_day', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(31)])),
                ('start_time', models.DateTimeField(verbose_name='Start Time')),
                ('end_time', models.DateTimeField(verbose_name='End Time')),
                ('description', models.TextField(blank=True, max_length=500)),
                ('image', models.ImageField(blank=True, upload_to=parties.models.party_image_upload_loc, verbose_name='party image')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('attendees', models.ManyToManyField(blank=True, related_name='party_attendees', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='party_creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'party',
                'verbose_name_plural': 'parties',
            },
        ),
    ]