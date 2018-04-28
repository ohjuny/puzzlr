from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Year, Profile

import re

# Form for a user to sign up.
class UserForm(UserCreationForm):
    # Uses regular expressions to determine if email is student or teacher.
    def validate_dc(email):
        student = re.compile("^[A-Za-z]+[0-9][0-9][0-9][0-9]\@dubaicollege.org$")
        teacher = re.compile("^[A-Za-z]+\.[A-Za-z]+\@dubaicollege.org$")
        if student.match(email):
            pass
        elif teacher.match(email):
            pass
        else:
            raise forms.ValidationError("Not a valid DC email address.")
    
    email = forms.EmailField(
        max_length=200,
        required=True,
        validators=[validate_dc],
    )
    
    year = forms.ModelChoiceField(
        queryset= Year.objects.all().order_by('pk'),
        required = True
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(pk=self.instance.pk).get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u'Username "%s" is already in use.' % username)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('This email address is already in use.')

    # Overrides Django's default clean method to ensure students can't use N/A.
    # Can't use regular 'validators' tag because this validation requires data from multiple fields (email and year).
    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get("email")
        year = cleaned_data.get("year")
        if email == None:
            raise forms.ValidationError('Email is invalid.')
        student = re.compile("^[A-Za-z]+[0-9][0-9][0-9][0-9]\@dubaicollege.org$")
        if student.match(email) and year.year == 'N/A':
            self._errors["year"] = self.error_class(['Students cannot use N/A as year.'])
            raise forms.ValidationError('Students cannot use N/A as year.')

        return cleaned_data

    # Overrides Django's default save method because I need to account for extended User model.
    def save(self):
        user = super(UserForm, self).save()
        profile = Profile(
            user = user,
            year = self.cleaned_data['year'],
        )
        profile.save()

        return user, profile
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'year']

# Form for a user to edit their profile.
class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=40, required=False)
    last_name = forms.CharField(max_length=40, required=False)
    year = forms.ModelChoiceField(
        queryset= Year.objects.all().order_by('year'),
        required = True
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'year']