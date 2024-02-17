from django.core.management.base import BaseCommand
from django.db.models import Count
from ...models import Subject

class Command(BaseCommand):
    help = 'Check for subjects with duplicate subject_keys in the same university'

    def handle(self, *args, **options):
        # Get subjects grouped by 'subject_key' and 'university' with count
        duplicates = Subject.objects.values('subject_key', 'university') \
                                    .annotate(subject_count=Count('id')) \
                                    .order_by()\
                                    .filter(subject_count__gt=1)

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