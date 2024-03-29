from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from ...models import TimeTable
import json

class Command(BaseCommand):
    help = 'Export timetables to JSON files'

    def handle(self, *args, **kwargs):
        # Definir los nombres de los archivos de salida
        filenames = {
            'UAM': 'schedules_uam.json',
            'UC3M': 'schedules_uc3m.json',
            'UAB': 'schedules_uab.json',
        }
        
        # Inicializar diccionarios para almacenar la información
        data = {
            'UAM': {},
            'UC3M': {},
            'UAB': {},
        }
        
        # Iterar sobre todos los horarios y agruparlos por universidad
        for timetable in TimeTable.objects.all():
            if timetable.schedule_file_uam:
                data['UAM'][timetable.subject_id] = timetable.schedule_file_uam.url
            if timetable.schedule_file_uc3m:
                data['UC3M'][timetable.subject_id] = timetable.schedule_file_uc3m.url
            if timetable.schedule_file_uab:
                data['UAB'][timetable.subject_id] = timetable.schedule_file_uab.url
        
        # Escribir cada diccionario en su correspondiente archivo JSON
        for university, schedule_data in data.items():
            with open(filenames[university], 'w') as outfile:
                json.dump(schedule_data, outfile, ensure_ascii=False, indent=4)
        
        self.stdout.write(self.style.SUCCESS('Successfully exported timetables to JSON'))