from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from django.utils import timezone
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.mail import EmailMessage

from .models import *
from .forms import *
from .tokens import account_activation_token
from puzzles.models import Subject
from django.contrib import messages

import re


# Create your views here.

# Global variable to store leaderboard status.
# Must be global because this variable must be accessed from multiple views.
leaderboard_public = False

# Loads my Django context processor.
# Ensures that 'leaderboard_public' is accessible from all templates in this app.
def leaderboard_status(request):
    return {
        'leaderboard_public': leaderboard_public,
    }

# View for sign ups without email verification.
# Very useful to have this view for sign ups during development and debugging.
def signup_without_email(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user, Profile = form.save()

            # Uses regular expressions to determine if email is student or teacher.
            email = user.email
            student = re.compile("^[A-Za-z]+[0-9][0-9][0-9][0-9]\@dubaicollege.org$")
            teacher = re.compile("^[A-Za-z]+\.[A-Za-z]+\@dubaicollege.org$")
            if student.match(email):
                user.profile.teacher = False
            elif teacher.match(email):
                user.profile.teacher = True
            
            user.save()
            user.profile.save()
            login(request, user)
            messages.success(request, 'Account created succesfully!')
            return redirect("profile", user.username)
        else:
            messages.warning(request, 'There are some errors on the form.')
            return render(request, "signup.html", {
                'form': form,
            })    
            
    else:
        form = UserForm()  
        return render(request, "signup.html", {
            'form': form,
        })

# View for sign ups with email verification.
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user, Profile = form.save()

            # Uses regular expressions to determine if email is student or teacher.
            email = user.email
            student = re.compile("^[A-Za-z]+[0-9][0-9][0-9][0-9]\@dubaicollege.org$")
            teacher = re.compile("^[A-Za-z]+\.[A-Za-z]+\@dubaicollege.org$")
            if student.match(email):
                user.profile.teacher = False
            elif teacher.match(email):
                user.profile.teacher = True
            
            user.save()
            user.profile.save()

            # Ensures user must verify email address before allowed to use account.
            user.is_active=False
            user.save()

            # Generates email.
            current_site = get_current_site(request)
            message = render_to_string('confirmation.html', {
                'user':user, 
                'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your blog account.'

            # Sends email.
            user.email_user(mail_subject, message)

            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            return render(request, "signup.html", {
                'form': form,
            })    
            
    else:
        form = UserForm()        
        return render(request, "signup.html", {
            'form': form,
        })    

# View called when user clicks activation link sent in verification email.
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. Now you can login to your account.')
    else:
        return HttpResponse('Activation link is invalid!')

# View for viewing user profiles.
def profile(request, username=None):
    # Exception handling to ensure program does not crash when given username that does not exist.
    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "no_user.html")

    # I could do this check in the template, but intentionally chose to do it in view
    # because I wanted to do all my processing server-side to reduce client-side load.
    currentLoggedIn = False
    if target == request.user:
        currentLoggedIn = True

    # Gets subjects as a list of subject_names in order to minimise processing in the front end.
    subjects = list(Subject.objects.values('subject_name'))
    subjects = [i['subject_name'] for i in subjects]

    return render(request, "profile.html", {
        "target": target,
        "currentLoggedIn": currentLoggedIn,
        "subjects": subjects,
    })

# View for editing user profiles.
def editProfile(request, username=None):
    if request.method == "POST":
        user = request.user
        form = EditProfileForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.profile.year = form.cleaned_data['year']
            user.save()
            user.profile.save()
            messages.success(request, 'Profile was updated successfully!')
        return HttpResponseRedirect(reverse("profile", kwargs={'username': user.username}))
    else:
        # Exception handling to ensure program does not crash when given username that does not exist.
        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, "no_user.html")
        # Ensures that only logged in users can edit profile.
        if request.user.is_authenticated:
            # Ensures that users cannot edit other users' profiles.
            if request.user.username == target.username:
                form = EditProfileForm(initial={
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'year': request.user.profile.year,
                    })
                return render(request, "editProfile.html", {
                    "form": form,
                })
            else:
                return render(request, "no_access.html")
        else:
            return render(request, "signup.html")

# View to track all solutions and comments made by a user.
def engagement(request, username=None):
    # Exception handling to ensure program does not crash when given username that does not exist.
    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "no_user.html")
    solutions = Solution.objects.filter(user=target).order_by('-datetime')
    comments = Comment.objects.filter(user=target).order_by('-datetime')
    return render(request, "engagement.html", {
        "target": target,
        "solutions": solutions,
        "comments": comments,
    })

# View to see the leaderboard.
def leaderboard(request):
    global leaderboard_public

    # Note that for reasons described in accounts/forms.py, I implemented .points in two ways:
    # using a dictionary and using a list of lists.
    # That's why I have a commented out a line below which assumes .points is a dictionary.
    users = sorted(User.objects.all(), key=lambda t: t.profile.points[0], reverse=True)
    # users = sorted(User.objects.all(), key=lambda t: t.profile.points['total'], reverse=True)

    if request.method == "POST":
        leaderboard_public = not leaderboard_public
        return redirect(leaderboard)

    if leaderboard_public or request.user.profile.teacher:
        subjects = list(Subject.objects.values('subject_name'))
        subjects = [i['subject_name'] for i in subjects]
        return render(request, "leaderboard.html", {
            "users": users,
            "subjects": subjects,
        })
    else:
        return render(request, "no_access.html")