from django.core.management.base import BaseCommand
from subjects.models import Subject, Degree, University

class Command(BaseCommand):
    help = 'Clears all data from the Subject, Degree, and University tables'

    def handle(self, *args, **kwargs):
        # Borrar todos los datos de la tabla Subject
        Subject.objects.all().delete()

        # Borrar todos los datos de la tabla Degree
        Degree.objects.all().delete()

        # Borrar todos los datos de la tabla University
        University.objects.all().delete()

        # Borrar la relación many-to-many entre Degree y Subject
        degrees = Degree.objects.all()
        for degree in degrees:
            degree.subjects.clear()

        self.stdout.write(self.style.SUCCESS('All data has been cleared successfully.'))