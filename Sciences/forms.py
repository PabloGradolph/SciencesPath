from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django import forms
from typing import Any
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for user creation that extends Django's built-in UserCreationForm.
    """
    is_student = forms.BooleanField(required=False, label='¿Eres estudiante del Grado en Ciencias?', help_text='Marca esta casilla si lo eres.')

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes the form with custom help texts and validators for specific fields.

        Args:
            *args: Variable length argument list for form initialization.
            **kwargs: Arbitrary keyword arguments for form initialization.
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Introduce solo letras y no más de 35 caracteres.'
        self.fields['username'].validators = [
            RegexValidator(
                regex='^[a-zA-Z]*$',
                message='Introduce solo letras.',
                code='invalid_username'
            ),
        ]
        self.fields['password1'].help_text = "Su contraseña debe contener al menos 8 caracteres y no puede ser completamente numérica."
        self.fields['password2'].help_text = ""
    
    class Meta:
        model = User # The model associated with this form.
        fields = ['username', 'email', 'password1', 'password2', 'is_student'] # Fields included in the form.


class CustomAuthenticationForm(AuthenticationForm):
    """ 
    Customized authentication form that accepts email or username.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar el campo 'username'
        self.fields.pop('username')
        self.fields.pop('password')

    username_or_email = forms.CharField(label='Usuario o email')
    password2 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

    

class SetPasswordForm(SetPasswordForm):
    """
    Custom form for setting a new password, using the active user model.
    """
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']