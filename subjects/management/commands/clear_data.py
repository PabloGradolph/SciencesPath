from django.core.management.base import BaseCommand
from typing import Any
from subjects.models import Subject, Degree, University


class Command(BaseCommand):
    """
    Django management command to clear all data from Subject, Degree, and University tables.
    """
    help = 'Clears all data from the Subject, Degree, and University tables'

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """
        Executes the command to delete all data from the tables.
        """
        # Clear Subject table
        Subject.objects.all().delete()

        # Clear Degree table
        Degree.objects.all().delete()

        # Clear University table
        University.objects.all().delete()

        # Clear the many-to-many relationship between Degree and Subject
        degrees = Degree.objects.all()
        for degree in degrees:
            degree.subjects.clear()

        self.stdout.write(self.style.SUCCESS('All data has been cleared successfully.'))