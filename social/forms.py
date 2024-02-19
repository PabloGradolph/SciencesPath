from django import forms
from django.contrib.auth.models import User
from .models import Post, Profile
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

class PostForm(forms.ModelForm):
    """Form for creating or updating a Post instance."""
    
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control w-100', 'id': 'contentsBox', 'rows': '3',
        'placeholder': 'Participa en la comunidad SciencePath!'
    }))

    image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={
        'class': 'form-control-file',
    }))

    class Meta:
        model = Post
        fields = ['content', 'image']

class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'username']


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile.
    """
    phone_number = PhoneNumberField(widget=PhoneNumberPrefixWidget(initial='ES'))
                                    
    class Meta:
        model = Profile
        fields = ['phone_number', 'image', 'bio']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'hide-current-image'})
        }