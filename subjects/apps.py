from django.apps import AppConfig


class SubjectsConfig(AppConfig):
    """
    Django application configuration for the 'subjects' app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subjects'
    verbose_name = 'Subjects'
