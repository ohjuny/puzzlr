# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-15 05:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0012_auto_20180215_0517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puzzle',
            name='subject',
            field=models.CharField(max_length=30),
        ),
    ]
