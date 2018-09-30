from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from puzzles.models import *

# Create your models here.

# Lookup table for year groups.
class Year(models.Model):
    # Uses CharField instead of IntegerField so that 'N/A' can be stored.
    year = models.CharField(max_length=3)

    def __str__(self):
        return self.year

# Definition of Solution object.
class Solution(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=50)
    content = models.TextField()
    up_votes = models.ManyToManyField(User, related_name='up_votes', blank=True)
    down_votes = models.ManyToManyField(User, related_name='down_votes', blank=True)
    datetime = models.DateTimeField(default=timezone.now, blank=True)
    
    @property
    def points(self):
        return self.up_votes.count() - self.down_votes.count()

    def __str__(self):
        return self.title

# Definition of Comment object.
class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    solution = models.ForeignKey(
        Solution,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=50)
    content = models.TextField()
    datetime = models.DateTimeField(default=timezone.now, blank=True)
    
    def __str__(self):
        return self.title

# Definition of Submission object.
class Submission(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
    )
    userAnswer = models.TextField()
    datetime = models.DateTimeField(default=timezone.now, blank=True)

    @property
    def correct(self):
        return self.userAnswer == self.puzzle.answer

    def __str__(self):
        return "{}, puzzle: {}".format(self.user.username, self.puzzle.id)

# Extending Django's default User model by having a OneToOneField with User table.
class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    teacher = models.BooleanField(default=False, blank=True)
    year = models.ForeignKey(
        Year,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.user.username


    # I implemented the 'points' property using a dictionary, then using a list of lists.
    # At the time, after I had implemented using a dictionary, I ran into errors with Django Template Language in my template.
    # So I reimplemented the feature using a list of lists, which worked fine with Django Template Language.

    #Using List of Lists
    @property
    def points(self):
        subjects = Subject.objects.all()
        submissions = Submission.objects.filter(user=self.user)
        points = []

        # Initialise list of lists in required format:
        # [['subject_name', subject_points], ['subject_name', subject_points]]
        counter = 0
        for subject in subjects:
            points.append([subject.subject_name])
            points[counter].append(0)
            counter += 1

        for submission in submissions:
            # Ensure only puzzles that have ended are counted.
            if submission.puzzle.end_date < timezone.now():
                subject = submission.puzzle.subject.subject_name
                index = 0
                
                # Finds index of puzzle's subject in list of lists.
                # This step would be unnecesarry if using a dictionary.
                for sj in points:
                    if sj[0] == subject:
                        break
                    index += 1

                if submission.userAnswer == submission.puzzle.answer:
                    points[index][1] += submission.puzzle.correct_points
                else:
                    points[index][1] += submission.puzzle.incorrect_points
        
        engagement = 0
        solutions = Solution.objects.filter(user=self.user)
        for solution in solutions:
            # This ensures negative scores don't affect the total score.
            # This is to prevent users from excessive downvoting.
            if solution.points > 0:
                engagement += solution.points
        points.insert(0, ['engagement', engagement])
        
        total = 0
        for category in points:
            total += category[1]
        points.insert(0, ['total', total])
        return points

    # Using Dictionary
    # @property
    # def points(self):
    #     subjects = Subject.objects.all()
    #     submissions = Submission.objects.filter(user=self.user)
    #     points = {}
    #     for subject in subjects:
    #         points[subject.subject_name] = 0
    #     for submission in submissions:
    #         if submission.puzzle.end_date < timezone.now():
    #             subject = submission.puzzle.subject.subject_name
    #             if submission.userAnswer == submission.puzzle.answer:
    #                 points[subject] += submission.puzzle.correct_points
    #             else:
    #                 points[subject] += submission.puzzle.incorrect_points

    #     engagement = 0
    #         solutions = Solution.objects.filter(user=self.user)
    #         for solution in solutions:
    #             if solution.points > 0:
    #                 engagement += solution.points
    #         points['engagement'] = 0]

    #     total = 0
    #     for category in points:
    #         total += points[category]
    #     points['total'] = total
    #     return points