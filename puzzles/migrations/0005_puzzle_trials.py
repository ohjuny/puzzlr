# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-11 06:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0004_auto_20171108_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='puzzle',
            name='trials',
            field=models.IntegerField(default=1),
        ),
    ]
