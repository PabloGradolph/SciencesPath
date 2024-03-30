from django.core.management.base import BaseCommand
from django.core.files import File
from ...models import TimeTable, Subject
import json
import os

class Command(BaseCommand):
    help = 'Create timetables from JSON files into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_files', nargs='+', type=str, help='Path to the JSON files with timetables.')

    def handle(self, *args, **options):
        for json_file in options['json_files']:
            with open(json_file, 'r') as infile:
                timetables_data = json.load(infile)
                university_field = self.get_university_field(json_file)

                for subject_id, file_path in timetables_data.items():
                    try:
                        subject = Subject.objects.get(id=subject_id)
                        with open(file_path, 'rb') as file:
                            # Crea una nueva instancia TimeTable y asocia el archivo
                            timetable, created = TimeTable.objects.get_or_create(
                                subject=subject
                            )
                            if created or not getattr(timetable, university_field):
                                setattr(timetable, university_field, File(file, name=os.path.basename(file_path)))
                                timetable.save()
                            else:
                                self.stdout.write(self.style.WARNING(f'TimeTable for subject {subject_id} with {university_field} already exists'))
                    except Subject.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'Subject with id {subject_id} does not exist'))
                    except FileNotFoundError:
                        self.stdout.write(self.style.ERROR(f'File {file_path} not found'))

    
    def get_university_field(self, json_file_name):
        if 'uab' in json_file_name.lower():
            return 'schedule_file_uab'
        elif 'uam' in json_file_name.lower():
            return 'schedule_file_uam'
        elif 'uc3m' in json_file_name.lower():
            return 'schedule_file_uc3m'
        else:
            self.stdout.write(self.style.ERROR('Invalid JSON file name for university identification'))
            return None