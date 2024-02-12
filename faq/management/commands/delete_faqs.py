from django.core.management.base import BaseCommand
from ...models import FAQ

class Command(BaseCommand):
    """
    A Django management command to delete all FAQ entries from the database.

    Attributes:
        help: A short description of the command displayed when using the `help` option from the command line.
    """
    help = 'Delete all FAQs from the database'

    def handle(self, *args: str, **options: str) -> None:
        """
        This method is called when the management command is executed. It deletes all FAQ objects from the database.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
        """
        FAQ.objects.all().delete()