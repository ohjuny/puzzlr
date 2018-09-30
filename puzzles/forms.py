from django import forms
from django.core.validators import MinValueValidator
from .models import Puzzle, Subject
from accounts.models import *
from django.utils import timezone

# Form to create a puzzle.
class CreateForm(forms.ModelForm):
    # Sets placeholders for specified fields.
    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields['correct_points'].widget.attrs['placeholder'] = 'Recommended: 10'
        self.fields['incorrect_points'].widget.attrs['placeholder'] = 'Recommended: 3'
        # Important because dates have been defined to be parsed only in this format.
        self.fields['scheduled_date'].widget.attrs['placeholder'] = 'YYYY-MM-DD HH:MM:SS'
        self.fields['end_date'].widget.attrs['placeholder'] = 'YYYY-MM-DD HH:MM:SS'
        
    title = forms.CharField(max_length=50)
    question = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 4,
        }),
    )
    answer = forms.CharField()
    subject = forms.ModelChoiceField(
        queryset= Subject.objects.all().order_by('subject_name'),
        required = True
    )

    correct_points = forms.IntegerField(
        validators=[MinValueValidator(1)],
    )
    incorrect_points = forms.IntegerField(
        validators=[MinValueValidator(0)],
    )

    scheduled_date = forms.DateTimeField(
        # Defines what format scheduled_date should parse date and time.
        input_formats=['%Y-%m-%d %H:%M:%S'],
        # Important because scheduled_date is an optional field
        required=False,
        label="(OPTIONAL) Scheduled Date",
    )
    end_date = forms.DateTimeField(
        # Defines what format .end_date should parse date and time.
        input_formats=['%Y-%m-%d %H:%M:%S'],
        label="Close Date",
    )

    # Overrides Django's default clean method to ensure all inputted dates and times are be validated.
    # Can't use regular 'validators' tag because this validation requires data from multiple fields (scheduled_date and end_date).
    def clean(self):
        cleaned_data = self.cleaned_data
        correct_points = cleaned_data.get("correct_points")
        incorrect_points = cleaned_data.get("incorrect_points")
        scheduled_date = cleaned_data.get("scheduled_date")
        end_date = cleaned_data.get("end_date")
        # Ensures that correct_points is required.
        if correct_points == None:
            self._errors["correct_points"] = self.error_class(["This field is required."])
            raise forms.ValidationError("This field is required.")
        # Ensures that end_date is required.
        if incorrect_points == None:
            self._errors["incorrect_points"] = self.error_class(["This field is required."])
            raise forms.ValidationError("This field is required.")
        # Ensures correct_points is higher than incorrect_points
        if correct_points < incorrect_points:
            self._errors["correct_points"] = self.error_class(["Correct points must be higher than incorrect points."])
            raise forms.ValidationError("Correct points must be higher than incorrect points.")
        # Ensures that end_date is required.
        if end_date == None:
            self._errors["end_date"] = self.error_class(["This field is required."])
            raise forms.ValidationError("This field is required.")
        # Ensures that if scheduled is not specified (therefore defaulted to current datetime), end_date is in the future.
        elif scheduled_date == None:
            if end_date <= timezone.now():
                self._errors["end_date"] = self.error_class(["End date must be in the future."])
                raise forms.ValidationError("End date must be in the future.")
        else:
            # Ensures that, if specified, scheduled_date is in the future.
            if scheduled_date <= timezone.now():
                self._errors["scheduled_date"] = self.error_class(["Scheduled date must be in the future"])
                raise forms.ValidationError("Scheduled date must be in the future.")
            # Ensures that scheduled_date is before the end_date.
            if scheduled_date >= end_date:
                self._errors["scheduled_date"] = self.error_class(["Scheduled date must be before End date."])
                raise forms.ValidationError("Scheduled date must be before End date.")
            return cleaned_data

    class Meta:
        model = Puzzle
        fields = ["title", "question", "answer", "subject", "correct_points", "incorrect_points", "scheduled_date", "end_date"]

# Form to edit a puzzle.
# Note that the code is almost identical line-by-line to the CreateForm defined above.
class EditPuzzleForm(forms.ModelForm):
    # Sets placeholders for specified fields.
    def __init__(self, *args, **kwargs):
        super(EditPuzzleForm, self).__init__(*args, **kwargs)
        self.fields['correct_points'].widget.attrs['placeholder'] = 'Recommended: 10'
        self.fields['incorrect_points'].widget.attrs['placeholder'] = 'Recommended: 3'
        # Important because dates have been defined to be parsed only in this format.
        self.fields['scheduled_date'].widget.attrs['placeholder'] = 'YYYY-MM-DD HH:MM:SS'
        self.fields['end_date'].widget.attrs['placeholder'] = 'YYYY-MM-DD HH:MM:SS'
        
    title = forms.CharField(max_length=50)
    question = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 4,
        }),
    )
    answer = forms.CharField()
    subject = forms.ModelChoiceField(
        queryset= Subject.objects.all().order_by('subject_name'),
        required = True
    )

    correct_points = forms.IntegerField(
        validators=[MinValueValidator(1)],
    )
    incorrect_points = forms.IntegerField(
        validators=[MinValueValidator(0)],
    )

    scheduled_date = forms.DateTimeField(
        # Defines what format scheduled_date should parse date and time.
        input_formats=['%Y-%m-%d %H:%M:%S'],
        # Important because scheduled_date is an optional field
        required=False,
        label="(OPTIONAL) Scheduled Date",
    )
    end_date = forms.DateTimeField(
        # Defines what format .end_date should parse date and time.
        input_formats=['%Y-%m-%d %H:%M:%S'],
        label="Close Date",
    )

    # Overrides Django's default clean method to ensure all inputted dates and times are be validated.
    # Can't use regular 'validators' tag because this validation requires data from multiple fields (scheduled_date and end_date).
    def clean(self):
        cleaned_data = self.cleaned_data
        correct_points = cleaned_data.get("correct_points")
        incorrect_points = cleaned_data.get("incorrect_points")
        scheduled_date = cleaned_data.get("scheduled_date")
        end_date = cleaned_data.get("end_date")
        # Ensures that correct_points is required.
        if correct_points == None:
            self._errors["correct_points"] = self.error_class(["This field is required."])
            raise forms.ValidationError("This field is required.")
        # Ensures that end_date is required.
        if incorrect_points == None:
            self._errors["incorrect_points"] = self.error_class(["This field is required."])
            raise forms.ValidationError("This field is required.")
        # Ensures correct_points is higher than incorrect_points
        if correct_points < incorrect_points:
            self._errors["correct_points"] = self.error_class(["Correct points must be higher than incorrect points."])
            raise forms.ValidationError("Correct points must be higher than incorrect points.")
        # Ensures that end_date is required.
        if end_date == None:
            self._errors["end_date"] = self.error_class(["This field is required."])
            raise forms.ValidationError("This field is required.")
        # Ensures that if scheduled is not specified (therefore defaulted to current datetime), end_date is in the future.
        elif scheduled_date == None:
            if end_date <= timezone.now():
                self._errors["end_date"] = self.error_class(["End date must be in the future."])
                raise forms.ValidationError("End date must be in the future.")
        else:
            # Ensures that, if specified, scheduled_date is in the future.
            if scheduled_date <= timezone.now():
                self._errors["scheduled_date"] = self.error_class(["Scheduled date must be in the future"])
                raise forms.ValidationError("Scheduled date must be in the future.")
            # Ensures that scheduled_date is before the end_date.
            if scheduled_date >= end_date:
                self._errors["scheduled_date"] = self.error_class(["Scheduled date must be before End date."])
                raise forms.ValidationError("Scheduled date must be before End date.")
            return cleaned_data

    class Meta:
        model = Puzzle
        fields = ["title", "question", "answer", "subject", "correct_points", "incorrect_points", "scheduled_date", "end_date"]


class SubmitForm(forms.ModelForm):
    answer = forms.CharField()

    class Meta:
        model = Submission
        fields = ["answer"]

# Form to add a solution.
class AddSolutionForm(forms.ModelForm):
    # Sets placeholders for specified fields.
    def __init__(self, *args, **kwargs):
        super(AddSolutionForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'Title'
        self.fields['content'].widget.attrs['placeholder'] = 'Content'
    
    title = forms.CharField(max_length=50)
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 6,
        }),
    )

    class Meta:
        model = Solution
        fields = ['title', 'content']

# Form to edit a solution.
class EditSolutionForm(forms.ModelForm):
    title = forms.CharField(max_length=50)
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 6,
        }),
    )

    class Meta:
        model = Solution
        fields = ['title', 'content']

# Form to add a comment.
class AddCommentForm(forms.ModelForm):
    # Sets placeholders for specified fields.
    def __init__(self, *args, **kwargs):
        super(AddCommentForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'Title'
        self.fields['content'].widget.attrs['placeholder'] = 'Content'
    
    title = forms.CharField(max_length=50)
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 6,
        }),
    )

    class Meta:
        model = Comment
        fields = ['title', 'content']

# Form to edit a comment.
class EditCommentForm(forms.ModelForm):
    title = forms.CharField(max_length=50)
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 6,
        }),
    )

    class Meta:
        model = Comment
        fields = ['title', 'content']