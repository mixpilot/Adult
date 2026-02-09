from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        label='I want to',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        help_text='Choose your account type'
    )
    terms_accepted = forms.BooleanField(
        required=True,
        label='I agree to the Terms of Service',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    age_verified = forms.BooleanField(
        required=True,
        label='I confirm that I am 18 years or older',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password',
            'id': 'id_password1'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })


class UserLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False,
        label='Remember me',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
        self.fields['username'].label = 'Username or Email'
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Allow login with either username or email
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'avatar', 'date_of_birth', 'phone_number', 'user_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 0712345678'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }
