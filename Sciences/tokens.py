from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.base_user import AbstractBaseUser

import six  


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generates a token for account activation.
    
    Extends Django's PasswordResetTokenGenerator to include the user's activation status.
    """
    def _make_hash_value(self, user: AbstractBaseUser, timestamp: int) -> str:
        """
        Generates a hash value for the token by combining the user's ID, the timestamp, and the activation status.
        
        Args:
            user: The user instance for whom the token is being generated.
            timestamp: The timestamp at which the token is generated.
        
        Returns:
            A string that combines the user's ID, timestamp, and activation status, used to generate a unique token.
        """
        return (
            six.text_type(user.pk) + six.text_type(timestamp)  + six.text_type(user.is_active)
        )

# Create an instance of the token generator
account_activation_token = AccountActivationTokenGenerator()