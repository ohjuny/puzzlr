# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-16 13:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solution',
            name='points',
        ),
        migrations.AddField(
            model_name='solution',
            name='down_votes',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='solution',
            name='up_votes',
            field=models.IntegerField(blank=True, default=1),
        ),
    ]
