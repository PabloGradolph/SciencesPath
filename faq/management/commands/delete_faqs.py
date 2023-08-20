from django.core.management.base import BaseCommand
from ...models import FAQ

class Command(BaseCommand):
    help = 'Delete all FAQs from the database'

    def handle(self, *args, **options):
        FAQ.objects.all().delete()