from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from typing import Any, Mapping

from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList


class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for user creation that extends Django's built-in UserCreationForm.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes the form with custom help texts and validators for specific fields.

        Args:
            *args: Variable length argument list for form initialization.
            **kwargs: Arbitrary keyword arguments for form initialization.
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Introduce solo letras y no más de 35 caracteres.'
        self.fields['username'].validators = []
        self.fields['password1'].help_text = "Su contraseña debe contener al menos 8 caracteres y no puede ser completamente numérica."
        self.fields['password2'].help_text = ""
    
    class Meta:
        model = User # The model associated with this form.
        fields = ['username', 'email', 'password1', 'password2'] # Fields included in the form.


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']