# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-18 06:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20171112_0807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
