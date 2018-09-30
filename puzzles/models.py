from django.db import models
from django.core.validators import MinValueValidator
from django import forms
from django.utils import timezone
from datetime import timedelta


# Create your models here.

# Lookup table for subjects.
class Subject(models.Model):
    subject_name = models.CharField(max_length=30)

    def __str__(self):
        return self.subject_name

# Definition of Puzzle object.
class Puzzle(models.Model):
    title = models.CharField(max_length=50)
    question = models.TextField()
    datetime = models.DateTimeField(
        default=timezone.now,
        blank=True)
    answer = models.TextField(default="answer")
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
    )
    correct_points = models.IntegerField(
        default=10,
    )
    incorrect_points = models.IntegerField(
        default=3,
    )
    scheduled_date = models.DateTimeField(
        default=timezone.now,
        null=True,
        blank=True,
    )

    def one_week_future():
        return timezone.now()+timedelta(days=7)

    end_date = models.DateTimeField(
        # Defaults end_date to one week in the future unless specified.
        # However, this default value should never be needed because CreatePuzzleForm and EditPuzzleForm perform validations
        # that ensure that end_date must be given.
        # So this default was mostly useful during development and debugging when I was experimenting with my Puzzle model.
        default=one_week_future,
        null=True,
    )

    def __str__(self):
        return self.title

