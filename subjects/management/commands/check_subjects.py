from django.core.management.base import BaseCommand
from django.db.models import Count
from typing import Any
from ...models import Subject


class Command(BaseCommand):
    """
    Django management command to check for duplicate subjects based on their 'subject_key' within the same university.
    """
    help = 'Check for subjects with duplicate subject_keys in the same university'

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Handles the command execution. Fetches and reports duplicate subjects.
        """
        # Query to identify duplicates
        duplicates = Subject.objects.values('subject_key', 'university') \
                                    .annotate(subject_count=Count('id')) \
                                    .order_by()\
                                    .filter(subject_count__gt=1)

        # Report findings
        if duplicates:
            self.stdout.write(self.style.SUCCESS('Found duplicates:'))
            for duplicate in duplicates:
                self.stdout.write(
                    f"SubjectKey: {duplicate['subject_key']}, "
                    f"University: {duplicate['university']}, "
                    f"Count: {duplicate['subject_count']}"
                )
        else:
            self.stdout.write(self.style.SUCCESS('No duplicates found.'))