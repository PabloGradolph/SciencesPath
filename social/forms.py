from django import forms
from django.contrib.auth.models import User
from .models import Post, Profile, Address, Comment
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django_countries.widgets import CountrySelectWidget
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


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
        fields = ['first_name', 'username', 'email']


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

    def clean_instagram_url(self):
        instagram_url = self.cleaned_data.get('instagram_url', '')
        if instagram_url and "instagram.com" not in instagram_url:
            raise ValidationError(_('La URL debe pertenecer a instagram.com.'))
        return instagram_url

    def clean_twitter_url(self):
        twitter_url = self.cleaned_data.get('twitter_url', '')
        if twitter_url and "twitter.com" not in twitter_url:
            raise ValidationError(_('La URL debe pertenecer a twitter.com.'))
        return twitter_url

    def clean_linkedin_url(self):
        linkedin_url = self.cleaned_data.get('linkedin_url', '')
        if linkedin_url and "linkedin.com" not in linkedin_url:
            raise ValidationError(_('La URL debe pertenecer a linkedin.com.'))
        return linkedin_url

    def clean_university_email(self):
        university_email = self.cleaned_data.get('university_email', '')
        valid_domains = ['uam.es', 'uc3m.es', 'uab.cat']
        if university_email:
            # Verificar si hay un '@' en el email
            if '@' not in university_email:
                raise ValidationError(_('Introduce una dirección de correo electrónico válida.'))
            # Extraer el dominio del email y verificar si termina con uno de los dominios válidos
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
        super(AddressUpdateForm, self).__init__(*args, **kwargs)
        self.fields['country'].required = False