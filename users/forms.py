from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)

        # custom password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

        # help texts
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields[
            'password1'].help_text = 'Your password must contain at least 8 characters and can\'t be entirely numeric.'
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'

    def clean_email(self):
        ''' make sure email is unique'''
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'

    def clean_email(self):
        ''' email uniqueness, excluding cur user '''
        email = self.cleaned_data.get('email')
        # cur user not included in uniquenes check
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean_username(self):
        ''' excluding current user'''
        username = self.cleaned_data.get('username')
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['image'].help_text = 'Upload a profile picture. Maximum size: 2MB. Supported formats: JPG, PNG, GIF'

    def clean_image(self):
        ''' for img size n format '''
        image = self.cleaned_data.get('image')

        if image:
            # 2MB limit
            if image.size > 2 * 1024*1024:
                raise forms.ValidationError('Image file too large. Size should not exceed 2MB.')

            # check file extensions
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            import os
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Unsupported file extension. Allowed extensions are: {", ".join(valid_extensions)}'
                )

        return image


class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['show_email', 'show_activity']
        widgets = {
            'show_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_activity': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'show_email': 'Show email on profile',
            'show_activity': 'Show activity status',
        }


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['email_comments', 'email_replies', 'email_reposts', 'email_newsletter']
        widgets = {
            'email_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_replies': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_reposts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_newsletter': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'email_comments': 'New comments on your posts',
            'email_replies': 'Replies to your comments',
            'email_reposts': 'Someone reposts your content',
            'email_newsletter': 'Weekly newsletter',
        }


class AppearanceSettingsForm(forms.ModelForm):
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
    ]

    POSTS_PER_PAGE_CHOICES = [
        (5, '5 posts'),
        (10, '10 posts'),
        (20, '20 posts'),
    ]

    theme = forms.ChoiceField(
        choices=THEME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    posts_per_page = forms.ChoiceField(
        choices=POSTS_PER_PAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['theme', 'posts_per_page']


class AccountDeletionForm(forms.Form):
    confirm_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type your username to confirm'
        }),
        help_text='Please type your username exactly as shown to confirm deletion.'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AccountDeletionForm, self).__init__(*args, **kwargs)

    def clean_confirm_username(self):
        username = self.cleaned_data.get('confirm_username')
        if username != self.user.username:
            raise forms.ValidationError('Username does not match. Please type your username exactly.')
        return username