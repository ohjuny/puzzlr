from django.shortcuts import render, redirect
from .models import Puzzle
from accounts.models import *
from .forms import *
from django.utils import timezone
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
import json

import logging
logger = logging.getLogger(__name__)

# Create your views here.

# View for live puzzles.
def puzzles(request):
    puzzles = Puzzle.objects.filter(end_date__range=(timezone.now(), "2999-01-01"), scheduled_date__range=("2011-01-01", timezone.now())).order_by('-end_date').reverse()
    return render(request, "puzzles.html", {
        'puzzles': puzzles,
    })

# View for an individual puzzle.
def puzzle(request, puzzleID=None):
    if request.method == "POST":
        form = SubmitForm(request.POST)
        # Ensures only logged in users can attempt a puzzle.
        # Non-logged in users are redirected to sign up page.
        if request.user.is_authenticated:
            if form.is_valid():
                puzzle = Puzzle.objects.get(id=puzzleID)
                userAnswer = form.cleaned_data['answer']
                submission = Submission(
                    user = request.user,
                    puzzle = puzzle,
                    userAnswer = userAnswer,
                    # correct = (userAnswer == puzzle.answer),
                )
                submission.save()
                return redirect('submissions', username=request.user)
        else:
            return redirect("signup")
    else:
        # Exception handling to ensure program does not crash when given puzzle that does not exist.
        try:
            puzzle = Puzzle.objects.get(id=puzzleID)
        except:
            return render(request, "no_puzzle.html")
        # Ensures that only teachers have access to scheduled puzzles.
        scheduled = False
        if puzzle.scheduled_date > timezone.now():
            if not request.user.is_authenticated() or not request.user.profile.teacher:
                return render(request, "no_puzzle.html")
            scheduled = True
        # I could do this check in the template, but intentionally chose to do it in view
        # because I wanted to do all my processing server-side to reduce client-side load.
        closed = False
        if puzzle.end_date < timezone.now():
            closed = True
        form = SubmitForm()
        if request.user.is_authenticated():
            # Ensures template does not display option to submit an answer if the user has already submitted one.
            attempted = Submission.objects.filter(user=request.user, puzzle=puzzle)
            return render(request, "puzzle.html", {
                "puzzle": puzzle,
                "form": form,
                "scheduled": scheduled,
                "closed": closed,
                "attempted": attempted,
            })
        else:
            return render(request, "puzzle.html", {
                "puzzle": puzzle,
                "form": form,
                "closed": closed,
            })

# View for creating a puzzle.
def create(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            puzzle = form.save(commit=False)
            # Defaults scheduled_date to current time if not specified by creator.
            if puzzle.scheduled_date == None:
                puzzle.scheduled_date = timezone.now()
            puzzle.save()    
            messages.success(request, 'Puzzle was created successfully!')
            return redirect("puzzles")
        else:
            messages.warning(request, 'There are some errors on the form.')
            return render(request, "create.html", {
                "form": form,
            })
    else:
        # Ensures that only teachers have ability to create puzzles.
        if request.user.is_authenticated and request.user.profile.teacher:
            form = CreateForm()
            return render(request, "create.html", {
                "form": form,
            })
        else:
            return render(request, "no_access.html")

# View for editing a puzzle.
def editPuzzle(request, puzzleID=None):
    if request.method == "POST":
        puzzle = Puzzle.objects.get(id=puzzleID)
        form = EditPuzzleForm(request.POST)
        if form.is_valid():
            # Cannot just do puzzle = form.save() because scheduled_date may be empty if puzzle is already live.
            # In this case, scheduled_date should be left as it is.
            puzzle.title = form.cleaned_data['title']
            puzzle.question = form.cleaned_data['question']
            puzzle.answer = form.cleaned_data['answer']
            puzzle.subject = form.cleaned_data['subject']
            if form.cleaned_data['scheduled_date'] != None:
                puzzle.scheduled_date = form.cleaned_data['scheduled_date']
            puzzle.end_date = form.cleaned_data['end_date']
            puzzle.correct_points = form.cleaned_data['correct_points']
            puzzle.incorrect_points = form.cleaned_data['incorrect_points']
            puzzle.save()
            messages.success(request, 'Puzzle was updated succesfully!')
            return HttpResponseRedirect(reverse("puzzle", kwargs={'puzzleID': puzzle.id}))
        else:
            messages.warning(request, 'There are some errors on the form.')
            return render(request, "editPuzzle.html", {
                'puzzleID': puzzle.id,
                'form': form,
            })
    else:
        # Ensures user must be logged in to edit a puzzle.
        if request.user.is_authenticated:
            # Ensures user must be a teacher to edit a puzzle.
            if request.user.profile.teacher:
                # Exception handling to ensure program does not crash when given puzzle that does not exist.
                try:
                    puzzle = Puzzle.objects.get(id=puzzleID)
                except:
                    return render(request, "no_puzzle.html")
                if puzzle.scheduled_date > timezone.now():
                    scheduled_in_future = True
                else:
                    scheduled_in_future = False
                    
                if puzzle.end_date > timezone.now():
                    end_in_future = True
                else:
                    end_in_future = False
                
                form = EditPuzzleForm(initial={
                    'title': puzzle.title,
                    'question': puzzle.question,
                    'answer': puzzle.answer,
                    'subject': puzzle.subject,
                    'scheduled_date': puzzle.scheduled_date,
                    'end_date': puzzle.end_date,
                    'correct_points': puzzle.correct_points,
                    'incorrect_points': puzzle.incorrect_points,
                    })
                return render(request, "editPuzzle.html", {
                    "form": form,
                    "puzzle": puzzle,
                    "scheduled_in_future": scheduled_in_future,
                    "end_in_future": end_in_future,
                })
            else:
                return render(request, "no_access.html")
        else:
            return render(request, "signup.html")

# View for deleting a puzzle.
def deletePuzzle(request, puzzleID=None):
    # Exception handling to ensure program does not crash when given puzzle that does not exist.
    try:
        puzzle = Puzzle.objects.get(id=puzzleID)
    except:
        return render(request, "no_puzzle.html")
    # Ensures only teachers can delete a puzzle.
    if request.user.profile.teacher:
        puzzle.delete()
        return redirect("puzzles")
    else:
        return render(request, "no_access.html")

# View for scheduled puzzles.
def scheduled(request):
    # Ensures user must be logged in to view scheduled puzzles.
    if request.user.is_authenticated:
        # Ensures user must be a teacher to view scheduled puzzles.
        if request.user.profile.teacher:
            puzzles = Puzzle.objects.filter(scheduled_date__range=(timezone.now(), "2999-01-01"))
            return render(request, "scheduled.html", {
                'puzzles': puzzles,
            })
        else:
            return render(request, "no_access.html")
    else:
        return render(request, "no_access.html")

# View for achived puzzles.
def archive(request):
    puzzles = Puzzle.objects.filter(end_date__range=("2011-01-01", timezone.now()))
    return render(request, "archive.html", {
        'puzzles': puzzles,
    })

# View for tracking a user's submissions.
def submissions(request, username=None):
    # Exception handling to ensure program does not crash when given username that does not exist.
    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "no_user.html")
    currentLoggedIn = False
    if target == request.user:
        currentLoggedIn = True
    submissions = Submission.objects.all().filter(user=target).order_by('-datetime')
    return render(request, "submissions.html", {
        "target": target,
        "submissions": submissions,
        "timenow": timezone.now(),
        "currentLoggedIn": currentLoggedIn,
    })

# View for viewing all solutions to a given puzzle.
def solutions(request, puzzleID=None):
    # Ensures user must be logged in to view solutions.
    # Important because this means students cannot just sign out, view the solutions, then submit
    # the correct answer without actually solving the puzzle themselves.
    if request.user.is_authenticated:
        # Exception handling to ensure program does not crash when given puzzle that does not exist.
        try:
            puzzle = Puzzle.objects.get(id=puzzleID)
        except:
            return render(request, "no_puzzle.html")
        scheduled = False
        if puzzle.scheduled_date > timezone.now():
            if not request.user.is_authenticated() or not request.user.profile.teacher:
                return render(request, "no_page.html")
            scheduled = True
        closed = False
        if puzzle.end_date < timezone.now():
            closed = True
        attempted = Submission.objects.filter(user=request.user, puzzle=puzzle)
        # Generate two queries to give user option of viewing in order of popularity or time posted.
        # solutions_popular is sorted using Python's sorted() instead of Django's order_by()
        # because order_by() does not support sorting a calculated field.
        solutions_popular = sorted(Solution.objects.filter(puzzle__id=puzzleID), key=lambda t: t.points, reverse=True)
        solutions_newest = Solution.objects.filter(puzzle__id=puzzleID).order_by('-datetime')
        return render(request, "solutions.html", {
            "puzzle": puzzle,
            "scheduled": scheduled,
            "closed": closed,
            "solutions_popular": solutions_popular,
            "solutions_newest": solutions_newest,
            "attempted": attempted,
        })
    else:
        return redirect('signup')

# View for an individual solution.
def solution(request, puzzleID=None, solutionID=None):
    # Ensures only logged in users can view individual solutions.
    if request.user.is_authenticated:
        # This is if user adds a comment from the page.
        # It was an intentional design decision to embed an add comment feature into this page
        # instead of creating a new page dedicated to creating comments.
        # The reason is to make it as easy as possible for users to comment, which will hopefully encourage them to do so.
        if request.method == "POST":
            form = AddCommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.solution = Solution.objects.get(id=solutionID)
                comment.save()    
                messages.success(request, 'Comment was created successfully!')
                return HttpResponseRedirect(reverse("solution", kwargs={
                    'puzzleID': puzzleID,
                    'solutionID': solutionID,
                }))
            else:
                messages.warning(request, 'There are some errors on the form.')
                return render(request, "solution.html", {
                    "form": form,
                })
        else:
            # Exception handling to ensure that program does not crash if solution does not exist
            try:
                solution = Solution.objects.get(id=solutionID)
            except:
                return render(request, "no_solution.html")
            puzzle = Puzzle.objects.get(id=puzzleID)
            closed = False
            if puzzle.end_date < timezone.now():
                closed = True
            attempted = Submission.objects.filter(user=request.user, puzzle=puzzle)
            # Ensures individual solution can only be viewed if user has submitted an answer or puzzle is archived.
            if attempted or closed:
                scheduled = False
                if puzzle.scheduled_date > timezone.now():
                    if not request.user.is_authenticated() or not request.user.profile.teacher:
                        return render(request, "no_page.html")
                    scheduled = True
                comments = Comment.objects.filter(solution=solution).order_by('-datetime')
                form = AddCommentForm()
                # Important that I send up_votes and down_votes as a list of usernames so that Django Template Language
                # can quickly iterate over it without much unnecessary client-side processing.
                up_votes = [u.username for u in solution.up_votes.all()]
                down_votes = [u.username for u in solution.down_votes.all()]
                return render(request, 'solution.html', {
                    "solution": solution,
                    "puzzle": puzzle,
                    "scheduled": scheduled,
                    "closed": closed,
                    "attempted": attempted,
                    "comments": comments,
                    "form": form,
                    "up_votes": up_votes,
                    "down_votes": down_votes,
                })
            else:
                return render(request, "no_access.html")
    else:
        return redirect('signup')

# View for adding a solution.
def add_solution(request, puzzleID=None):
    if request.method == "POST":
        form = AddSolutionForm(request.POST)
        if form.is_valid():
            solution = form.save(commit=False)
            solution.user = request.user
            solution.puzzle = Puzzle.objects.get(id=puzzleID)
            solution.save()    
            messages.success(request, 'Solution was created successfully!')
            return HttpResponseRedirect(reverse("solutions", kwargs={'puzzleID': puzzleID}))
        else:
            messages.warning(request, 'There are some errors on the form.')
            return render(request, "add_solution.html", {
                "form": form,
            })
    # Ensures only logged in users can add solutions.
    if request.user.is_authenticated:
        # Exception handling to ensure program does not crash when given puzzle that does not exist.
        try:
            puzzle = Puzzle.objects.get(id=puzzleID)
        except:
            return render(request, "no_puzzle.html")
        closed = False
        if puzzle.end_date < timezone.now():
            closed = True
        attempted = Submission.objects.filter(user=request.user, puzzle=puzzle)
        # Ensures solution can only be added if user has submitted an answer or puzzle is archived.
        if attempted or closed:
            scheduled = False
            if puzzle.scheduled_date > timezone.now():
                if not request.user.is_authenticated() or not request.user.profile.teacher:
                    return render(request, "no_page.html")
                scheduled = True
            form = AddSolutionForm()
            return render(request, "add_solution.html", {
                "puzzle": puzzle,
                "scheduled": scheduled,
                "closed": closed,
                "attempted": attempted,
                "form": form,
            })
        else:
            return render(request, "no_access.html")
    else:
        return redirect("signup")

# View for editing a solution.
def edit_solution(request, puzzleID=None, solutionID=None):
    # Exception handling to ensure that program does not crash if solution does not exist
    try:
        solution = Solution.objects.get(id=solutionID)
    except:
        return render(request, "no_solution.html")
    if request.method == "POST":
        form = EditSolutionForm(request.POST)
        if form.is_valid():
            solution.title = form.cleaned_data['title']
            solution.content = form.cleaned_data['content']
            solution.save()
            messages.success(request, 'Solution was edited successfully!')
            return HttpResponseRedirect(reverse("solutions", kwargs={'puzzleID': puzzleID}))
        else:
            messages.warning(request, 'There are some errors on the form.')
            return render(request, "edit_solution.html", {
                "form": form,
            })
    else:
        # Ensures user must be logged in to edit a solution.
        if request.user.is_authenticated:
            # Ensures user must be author of solution or a teacher to edit a solution.
            if solution.user.username == request.user.username or request.user.profile.teacher:
                puzzle = Puzzle.objects.get(id=puzzleID)
                scheduled = False
                if puzzle.scheduled_date > timezone.now():
                    if not request.user.is_authenticated() or not request.user.profile.teacher:
                        return render(request, "no_page.html")
                    scheduled = True
                closed = False
                if puzzle.end_date < timezone.now():
                    closed = True
                attempted = Submission.objects.filter(user=request.user, puzzle=puzzle)
                form = EditSolutionForm(initial={
                    'title': solution.title,
                    'content': solution.content,
                    })
                return render(request, "edit_solution.html", {
                    "form": form,
                    "puzzle": puzzle,
                    "scheduled": scheduled,
                    "closed": closed,
                    "attempted": attempted,
                })
            else:
                return render(request, "no_access.html")
        else:
            return redirect('signup')

# View for deleting a solution.
def delete_solution(request, puzzleID=None, solutionID=None):
    # Exception handling to ensure that program does not crash if solution does not exist
    try:
        solution = Solution.objects.get(id=solutionID)
    except:
        return render(request, "no_solution.html")
    # Ensures only author of solution or teachers can delete a solution.
    if request.user.username == solution.user.username or request.user.profile.teacher:
        solution.delete()
        return HttpResponseRedirect(reverse("solutions", kwargs={'puzzleID': puzzleID}))
    else:
        return render(request, "no_access.html")

# View for editing a comment.
def edit_comment(request, puzzleID=None, solutionID=None, commentID=None):
    # Exception handling to ensure that program does not crash if comment does not exist
    try:
        comment = Comment.objects.get(id=commentID)
    except:
        return render(request, "no_comment.html")
    solution = Solution.objects.get(id=solutionID)
    if request.method == "POST":
        form = EditSolutionForm(request.POST)
        if form.is_valid():
            comment.title = form.cleaned_data['title']
            comment.content = form.cleaned_data['content']
            comment.save()
            messages.success(request, 'Comment was edited successfully!')
            return HttpResponseRedirect(reverse("solution", kwargs={
                'puzzleID': puzzleID,
                'solutionID': solutionID,
            }))
        else:
            messages.warning(request, 'There are some errors on the form.')
            return render(request, "edit_comment.html", {
                "form": form,
            })
    else:
        # Ensures user must be logged in to edit a solution.
        if request.user.is_authenticated:
            # Ensures user must be author of comment or a teacher to edit a comment.
            if solution.user.username == request.user.username or request.user.profile.teacher:
                puzzle = Puzzle.objects.get(id=puzzleID)
                scheduled = False
                if puzzle.scheduled_date > timezone.now():
                    if not request.user.is_authenticated() or not request.user.profile.teacher:
                        return render(request, "no_page.html")
                    scheduled = True
                closed = False
                if puzzle.end_date < timezone.now():
                    closed = True
                attempted = Submission.objects.filter(user=request.user, puzzle=puzzle)
                form = EditCommentForm(initial={
                    'title': comment.title,
                    'content': comment.content,
                })
                return render(request, 'edit_comment.html', {
                    "comment": comment,
                    "solution": solution,
                    "puzzle": puzzle,
                    "scheduled": scheduled,
                    "closed": closed,
                    "attempted": attempted,
                    "form": form,
                })
            else:
                return render(request, "no_access.html")
        else:
            return redirect('signup')

# View for deleting a comment.
def delete_comment(request, puzzleID=None, solutionID=None, commentID=None):
    # Exception handling to ensure that program does not crash if comment does not exist
    try:
        comment = Comment.objects.get(id=commentID)
    except:
        return render(request, "no_comment.html")
    # Ensures only author of comment or teachers can delete a comment.
    if request.user.username == comment.user.username or request.user.profile.teacher:
        comment.delete()
        return HttpResponseRedirect(reverse("solution", kwargs={
            'puzzleID': puzzleID,
            'solutionID': solutionID,
        }))
    else:
        return render(request, "no_access.html")

# View called by Ajax call to search live puzzles.
def search_puzzles(request):
    if request.is_ajax():
        search_text = request.GET.get('search_text')
        # Ajax only allows me to send data as strings, so I am unable to transfer a boolean directly.
        # So I improvise by converting the string to a boolean value using Python.
        title = request.GET.get('title') == "true"
        question = request.GET.get('question') == "true"
        subject = request.GET.get('subject') == "true"
        
        # Uses Django's Q object to dynamically build a query depending on which checkboxes are ticked.
        query = Q()
        if title:
            query |= Q(title__icontains=search_text)
        if question:
            query |= Q(question__icontains=search_text)
        if subject:
            query |= Q(subject__subject_name__icontains=search_text)

        if not (title or question or subject):
            puzzles = []
        # Intentional design decision to not perform search if only two or less characters are inputted.
        # This is because it could get annoying to see every puzzle appear when the user has typed one letter.
        elif search_text == '' or len(search_text) <= 2:
            puzzles = []
        else:
            puzzles = Puzzle.objects.filter(end_date__range=(timezone.now(), "2999-01-01"), scheduled_date__range=("2011-01-01", timezone.now())).order_by('-end_date').reverse()
            puzzles = puzzles.filter(query)

        return render(request, "ajax_search_puzzles.html", {
            'puzzles': puzzles,
            'search_len': len(search_text),
        })

# View called by Ajax call to search archived puzzles.
def search_archive(request):
    if request.is_ajax():
        search_text = request.GET.get('search_text')
        # Ajax only allows me to send data as strings, so I am unable to transfer a boolean directly.
        # So I improvise by converting the string to a boolean value using Python.
        title = request.GET.get('title') == "true"
        question = request.GET.get('question') == "true"
        subject = request.GET.get('subject') == "true"
        
        # Uses Django's Q object to dynamically build a query depending on which checkboxes are ticked.
        query = Q()
        if title:
            query |= Q(title__icontains=search_text)
        if question:
            query |= Q(question__icontains=search_text)
        if subject:
            query |= Q(subject__subject_name__icontains=search_text)

        if not (title or question or subject):
            puzzles = []
        # Intentional design decision to not perform search if only two or less characters are inputted.
        # This is because it could get annoying to see every puzzle appear when the user has typed one letter.
        elif search_text == '' or len(search_text) <= 2:
            puzzles = []
        else:
            puzzles = Puzzle.objects.filter(end_date__range=("2011-01-01", timezone.now()))
            puzzles = puzzles.filter(query)

        return render(request, "ajax_search_archive.html", {
            'puzzles': puzzles,
            'search_len': len(search_text),
        })

# View called by Ajax call to search scheduled puzzles.
def search_scheduled(request):
    if request.is_ajax():
        search_text = request.GET.get('search_text')
        # Ajax only allows me to send data as strings, so I am unable to transfer a boolean directly.
        # So I improvise by converting the string to a boolean value using Python.
        title = request.GET.get('title') == "true"
        question = request.GET.get('question') == "true"
        subject = request.GET.get('subject') == "true"
        
        # Uses Django's Q object to dynamically build a query depending on which checkboxes are ticked.
        query = Q()
        if title:
            query |= Q(title__icontains=search_text)
        if question:
            query |= Q(question__icontains=search_text)
        if subject:
            query |= Q(subject__subject_name__icontains=search_text)

        if not (title or question or subject):
            puzzles = []
        # Intentional design decision to not perform search if only two or less characters are inputted.
        # This is because it could get annoying to see every puzzle appear when the user has typed one letter.
        elif search_text == '' or len(search_text) <= 2:
            puzzles = []
        else:
            puzzles = Puzzle.objects.filter(scheduled_date__range=(timezone.now(), "2999-01-01"))
            puzzles = puzzles.filter(query)

        return render(request, "ajax_search_scheduled.html", {
            'puzzles': puzzles,
            'search_len': len(search_text),
        })

# View called by Ajax call to up vote a solution.
def up_vote(request):
    solutionID = request.GET.get('solutionID')
    solution = Solution.objects.get(id=solutionID)
    # Ensures that user cannot both up vote and down vote a solution.
    if request.user in solution.up_votes.all():
        solution.up_votes.remove(request.user)
    else:
        solution.up_votes.add(request.user)
        if request.user in solution.down_votes.all():
            solution.down_votes.remove(request.user)
    solution.save()
    return HttpResponse()

# View called by Ajax call to down vote a solution.
def down_vote(request):
    solutionID = request.GET.get('solutionID')
    solution = Solution.objects.get(id=solutionID)
    # Ensures that user cannot both up vote and down vote a solution.
    if request.user in solution.down_votes.all():
        solution.down_votes.remove(request.user)
    else:
        solution.down_votes.add(request.user)
        if request.user in solution.up_votes.all():
            solution.up_votes.remove(request.user)
    solution.save()
    return HttpResponse()

# View for an invalid URL.
def error(request):
    return render(request, 'no_page.html')