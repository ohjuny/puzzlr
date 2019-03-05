"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as authViews

from django.conf import settings
from django.conf.urls.static import static

# import views from apps

from accounts import views as accountsViews
from puzzles import views as puzzlesViews

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^signup/$', accountsViews.signup, name="signup"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', accountsViews.activate, name='activate'),
    url(r'^logout/$', authViews.LogoutView.as_view(), name='logout'),
    url(r'^login/$', authViews.LoginView.as_view(template_name='login.html'), name="login"),

    url(r'^puzzle/(?P<puzzleID>.+)/solution/(?P<solutionID>.+)/edit/$', puzzlesViews.edit_solution, name="edit_solution"),
    url(r'^puzzle/(?P<puzzleID>.+)/solution/(?P<solutionID>.+)/delete/$', puzzlesViews.delete_solution, name="delete_solution"),
    url(r'^puzzle/(?P<puzzleID>.+)/solution/(?P<solutionID>.+)/comment/(?P<commentID>.+)/edit$', puzzlesViews.edit_comment, name="edit_comment"),
    url(r'^puzzle/(?P<puzzleID>.+)/solution/(?P<solutionID>.+)/comment/(?P<commentID>.+)/delete$', puzzlesViews.delete_comment, name="delete_comment"),
    url(r'^puzzle/(?P<puzzleID>.+)/solution/(?P<solutionID>.+)/$', puzzlesViews.solution, name="solution"),
    url(r'^puzzle/(?P<puzzleID>.+)/edit/$', puzzlesViews.editPuzzle, name="editPuzzle"),
    url(r'^puzzle/(?P<puzzleID>.+)/delete/$', puzzlesViews.deletePuzzle, name="deletePuzzle"),
    url(r'^puzzle/(?P<puzzleID>.+)/solutions/$', puzzlesViews.solutions, name="solutions"),
    url(r'^puzzle/(?P<puzzleID>.+)/addsolution/$', puzzlesViews.add_solution, name="add_solution"),
    url(r'^puzzle/(?P<puzzleID>.+)/$', puzzlesViews.puzzle, name="puzzle"),
    url(r'^scheduled/$', puzzlesViews.scheduled, name="scheduled"),
    url(r'^archive/$', puzzlesViews.archive, name="archive"),
    url(r'^create/$', puzzlesViews.create, name="create"),

    url(r'^leaderboard/$', accountsViews.leaderboard, name="leaderboard"),

    url(r'^profile/(?P<username>.+)/submissions/$', puzzlesViews.submissions, name="submissions"),
    url(r'^profile/(?P<username>.+)/engagement/$', accountsViews.engagement, name="engagement"),
    url(r'^profile/(?P<username>.+)/edit/$', accountsViews.editProfile, name="editProfile"),
    url(r'^profile/(?P<username>.+)/$', accountsViews.profile, name="profile"),
    # URLs for ajax calls
    url(r'^ajax/searchpuzzles/$', puzzlesViews.search_puzzles, name="search_puzzles"),
    url(r'^ajax/searcharchive/$', puzzlesViews.search_archive, name="search_archive"),
    url(r'^ajax/searchscheduled/$', puzzlesViews.search_scheduled, name="search_scheduled"),
    url(r'^ajax/upvote/$', puzzlesViews.up_vote, name="up_vote"),
    url(r'^ajax/downvote/$', puzzlesViews.down_vote, name="down_vote"),

    #Views for password reset
    url(r'^password_reset/$', authViews.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', authViews.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        authViews.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', authViews.password_reset_complete, name='password_reset_complete'),

    # Intentional design decision to make landing page the page with all the live puzzles.
    # This is because the main purpose of the app is to encourage people to solve puzzles.
    url(r'^$', puzzlesViews.puzzles, name="puzzles"),
    # Ensures that invalid URLs do not crash the program.
    url(r'^.*/$', puzzlesViews.error, name="error"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
