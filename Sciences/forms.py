from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django import forms
from typing import Any


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


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']