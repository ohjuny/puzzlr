# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-08 16:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0002_puzzle_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='puzzle',
            name='subject',
            field=models.CharField(choices=[('CS', 'Computer Science')], default='CS', max_length=2),
        ),
    ]
