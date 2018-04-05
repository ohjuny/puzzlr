# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-15 05:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0011_auto_20180215_0512'),
    ]

    operations = [
        migrations.AddField(
            model_name='puzzle',
            name='subject',
            field=models.CharField(default='Computer Science', max_length=30),
        ),
        migrations.AlterField(
            model_name='subject',
            name='subject_name',
            field=models.CharField(max_length=30),
        ),
    ]
