from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Year)
admin.site.register(Solution)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(Submission)