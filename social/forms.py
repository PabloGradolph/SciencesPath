from django import forms
from django.contrib.auth.models import User
from .models import Post, Profile
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class PostForm(forms.ModelForm):
    """Form for creating or updating a Post instance."""
    
    content = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={
                'class': 'area-comentario', 
                'placeholder': 'Participa en la comunidad SciencePath!',
                'rows': 3,  
            }
        )
    )

    image = forms.ImageField(
        label='Adjuntar archivo',
        required=False,  
        widget=forms.FileInput(  
            attrs={
                'id': 'adjuntar', 
                'class': 'boton-file',
            }
        )
    )

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