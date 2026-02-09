from django import forms
from .models import UserProfile, ProfilePhoto, Message, UserReport


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['gender', 'seeking', 'age', 'location', 'bio', 'interests']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'seeking': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 18, 'max': 100}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, State'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Tell others about yourself...'}),
            'interests': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., movies, music, sports'}),
        }


class ProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = ProfilePhoto
        fields = ['photo', 'is_primary']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message...'
            })
        }


class UserSearchForm(forms.Form):
    gender = forms.ChoiceField(
        choices=[('', 'All')] + UserProfile.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    seeking = forms.ChoiceField(
        choices=[('', 'All')] + UserProfile.SEEKING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_age = forms.IntegerField(
        required=False,
        min_value=18,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min age', 'min': 18})
    )
    max_age = forms.IntegerField(
        required=False,
        min_value=18,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max age', 'min': 18})
    )
    # Location filters
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City (e.g., Nairobi)'})
    )
    area = forms.ChoiceField(
        choices=[('', 'Any Area')] + UserProfile.AREA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    online_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Advanced filters
    body_type = forms.ChoiceField(
        choices=[('', 'Any')] + UserProfile.BODY_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ethnicity = forms.ChoiceField(
        choices=[('', 'Any')] + UserProfile.ETHNICITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    education_level = forms.ChoiceField(
        choices=[('', 'Any')] + UserProfile.EDUCATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    relationship_status = forms.ChoiceField(
        choices=[('', 'Any')] + UserProfile.RELATIONSHIP_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    smokes = forms.ChoiceField(
        choices=[('', 'Any')] + UserProfile.FREQUENCY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    drinks = forms.ChoiceField(
        choices=[('', 'Any')] + UserProfile.FREQUENCY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    verified_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    photo_verified_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class UserReportForm(forms.ModelForm):
    """Form for reporting a user profile for moderation/safety."""
    class Meta:
        model = UserReport
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe why this user should be reviewed (e.g., harassment, spam, fake profile, etc.).'
            }),
        }
