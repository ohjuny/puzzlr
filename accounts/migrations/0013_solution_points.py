# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-16 07:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20180316_0658'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='points',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
