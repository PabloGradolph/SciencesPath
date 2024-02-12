from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from typing import Any


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