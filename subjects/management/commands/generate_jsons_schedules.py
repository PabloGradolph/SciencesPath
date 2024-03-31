from django.core.management.base import BaseCommand
from typing import Any
from ...models import TimeTable
import json


class Command(BaseCommand):
    """
    Django management command to export timetable data to JSON files for each university.
    """
    help = 'Export timetables to JSON files'

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """
        Gathers timetable data from the database and exports it to separate JSON files for each university.
        """
        # Define output filenames for each university
        filenames = {
            'UAM': 'schedules_uam.json',
            'UC3M': 'schedules_uc3m.json',
            'UAB': 'schedules_uab.json',
        }
        
        # Initialize dictionaries to store information
        data = {
            'UAM': {},
            'UC3M': {},
            'UAB': {},
        }
        
        # Iterate over all timetables and group them by university
        for timetable in TimeTable.objects.all():
            if timetable.schedule_file_uam:
                data['UAM'][timetable.subject_id] = timetable.schedule_file_uam.url
            if timetable.schedule_file_uc3m:
                data['UC3M'][timetable.subject_id] = timetable.schedule_file_uc3m.url
            if timetable.schedule_file_uab:
                data['UAB'][timetable.subject_id] = timetable.schedule_file_uab.url
        
        # Write each dictionary to its corresponding JSON file
        for university, schedule_data in data.items():
            with open(filenames[university], 'w') as outfile:
                json.dump(schedule_data, outfile, ensure_ascii=False, indent=4)
        
        self.stdout.write(self.style.SUCCESS('Successfully exported timetables to JSON'))