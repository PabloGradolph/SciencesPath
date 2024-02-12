from django.apps import AppConfig


class FaqConfig(AppConfig):
    """Configuration for the FAQ application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faq'
    verbose_name = 'FAQ'
