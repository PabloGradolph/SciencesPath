import json
from django.core.management.base import BaseCommand
from ...models import Subject, Degree, University

class Command(BaseCommand):
    help = 'Load data from JSON files into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        load_subjects_from_json(file_path)

def load_subjects_from_json(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for key, value in data.items():
            university_name = key.split(' | ')[1]
            degree_name = key.split(' | ')[0]

            university, _ = University.objects.get_or_create(
                name=university_name
            )
            degree, _ = Degree.objects.get_or_create(
                name=degree_name, university=university
            )

            for key2, value2 in value.items():
                key2 = key2.lower().capitalize()
                subject_data = {
                    'name': key2,
                    'subject_key': value2['Codigo'] if 'Codigo' in value2 else \
                        value2['Código'],
                    'year': value2['Curso'],
                    'semester': value2['Cuatrimestre'],
                    'credits': value2['Créditos'],
                    'language': value2['Idioma'],
                    'coordinator': value2['Coordinador/a'],
                    'previous_requirements': value2['Requisitos previos'],
                    'subject_url': value2['Guia docente'],
                    'content': value2['Programa']
                }

                matching_subjects = Subject.objects.filter(degree=degree, 
                    university=university, 
                    subject_key=subject_data['subject_key']
                )

                if not matching_subjects.exists():
                    subject = Subject.objects.create( 
                        university=university, degree=degree, **subject_data
                    )
