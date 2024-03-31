from django import forms
from django.contrib.auth.models import User
from django_countries.widgets import CountrySelectWidget
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

from .models import Post, Profile, Address, Comment
import re


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


class CommentForm(forms.ModelForm):
    """
    A form for creating or editing a Comment instance.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Escribe un comentario...'}),
        }


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user information.
    """
    first_name = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'username']
    
    def clean_username(self) -> str:
        """
        Validates that the username contains only letters and does not exceed 35 characters.

        Returns:
            str: The validated username.

        Raises:
            ValidationError: If the username does not meet the criteria.
        """
        username = self.cleaned_data['username']
        if not re.match(r'^[a-zA-Z]+$', username):
            raise ValidationError(_('El nombre de usuario sólo puede contener letras.'))
        if len(username) > 35:
            raise ValidationError(_('El nombre de usuario no puede tener más de 35 caracteres.'))
        return username
    
    def clean_first_name(self) -> str:
        """
        Validates that the first name contains only letters and spaces.

        Returns:
            str: The validated first name.

        Raises:
            ValidationError: If the first name does not meet the criteria.
        """
        first_name = self.cleaned_data['first_name']
        if first_name and not re.match(r'^[a-zA-Z ]+$', first_name):
            raise ValidationError(_('El nombre sólo puede contener letras y espacios.'))
        return first_name


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile.
    """
    phone_number = PhoneNumberField(widget=PhoneNumberPrefixWidget(initial='ES'), required=False)
    university_email = forms.EmailField(required=False)
    linkedin_url = forms.URLField(required=False)
    instagram_url = forms.URLField(required=False)
    twitter_url = forms.URLField(required=False)
    birth_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)
    is_student = forms.BooleanField(required=False)
    university = forms.ChoiceField(choices=Profile.UNIVERISITY_CHOICES, required=False)
    year = forms.ChoiceField(choices=Profile.YEAR_CHOICES, required=False)
    is_expediente_public = forms.BooleanField(required=False)

    def clean_instagram_url(self) -> str:
        """
        Validate Instagram URL belongs to instagram.com.
        """
        instagram_url = self.cleaned_data.get('instagram_url', '')
        if instagram_url and "instagram.com" not in instagram_url:
            raise ValidationError(_('La URL debe pertenecer a instagram.com.'))
        return instagram_url

    def clean_twitter_url(self) -> str:
        """
        Validate Twitter URL belongs to twitter.com.
        """
        twitter_url = self.cleaned_data.get('twitter_url', '')
        if twitter_url and "twitter.com" not in twitter_url:
            raise ValidationError(_('La URL debe pertenecer a twitter.com.'))
        return twitter_url

    def clean_linkedin_url(self) -> str:
        """
        Validate LinkedIn URL belongs to linkedin.com.
        """
        linkedin_url = self.cleaned_data.get('linkedin_url', '')
        if linkedin_url and "linkedin.com" not in linkedin_url:
            raise ValidationError(_('La URL debe pertenecer a linkedin.com.'))
        return linkedin_url

    def clean_university_email(self) -> str:
        """
        Validate university email domain.
        """
        university_email = self.cleaned_data.get('university_email', '')
        valid_domains = ['uam.es', 'uc3m.es', 'uab.cat']

        if university_email:
            if '@' not in university_email:
                raise ValidationError(_('Introduce una dirección de correo electrónico válida.'))
            
            domain_part = university_email.split('@')[-1]
            if not any(domain_part.endswith(domain) for domain in valid_domains):
                raise ValidationError(_('El correo universitario debe terminar con uno de los siguientes dominios: %(valid_domains)s'),
                                      params={'valid_domains': ', '.join(valid_domains)})
        return university_email
                              
    class Meta:
        model = Profile
        fields = ['phone_number', 'image', 'bio', 'university_email', 'linkedin_url', 'instagram_url', 'twitter_url',
                   'birth_date', 'is_student', 'university', 'year', 'is_expediente_public']
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
        """
        Initializes the form instance, setting the country field to optional.
        """
        super(AddressUpdateForm, self).__init__(*args, **kwargs)
        self.fields['country'].required = False