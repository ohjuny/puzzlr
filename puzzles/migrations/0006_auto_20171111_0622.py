# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-11 06:22
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0005_puzzle_trials'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puzzle',
            name='trials',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
