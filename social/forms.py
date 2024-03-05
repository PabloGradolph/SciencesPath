from django import forms
from django.contrib.auth.models import User
from .models import Post, Profile, Address
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField


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
    first_name = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile.
    """
    phone_number = PhoneNumberField(widget=PhoneNumberPrefixWidget(initial='ES'), required=False)
    university_email = forms.EmailField(required=False)
    facebook_url = forms.URLField(required=False)
    instagram_url = forms.URLField(required=False)
    twitter_url = forms.URLField(required=False)
    birth_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)
    is_student = forms.BooleanField(required=False)
    university = forms.ChoiceField(choices=Profile.UNIVERISITY_CHOICES, required=False)
    year = forms.ChoiceField(choices=Profile.YEAR_CHOICES, required=False)
                                    
    class Meta:
        model = Profile
        fields = ['phone_number', 'image', 'bio', 'university_email', 'facebook_url', 'instagram_url', 'twitter_url',
                   'birth_date', 'is_student', 'university', 'year']
        widgets = {
            'image': forms.FileInput(attrs={'id': 'profileImageUpload', 'class': 'hide-current-image'})
        }


class AddressUpdateForm(forms.ModelForm):
    """
    Form for updating user address.
    """
    street = forms.CharField(required=False)
    number = forms.IntegerField(required=False)
    floor = forms.IntegerField(required=False)
    door = forms.CharField(required=False)
    city = forms.CharField(required=False)

    class Meta:
        model = Address
        fields = ['street', 'number', 'floor', 'door', 'city', 'country']
        widgets = {
            'country': CountrySelectWidget()
        }
    
    def __init__(self, *args, **kwargs):
        super(AddressUpdateForm, self).__init__(*args, **kwargs)
        self.fields['country'].required = False