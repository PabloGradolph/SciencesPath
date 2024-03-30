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

        # This piece of code in case you want to load the Science Degree subjects.
        # for key, value in data.items():

        #     if "(A1, A2)" in key or "(B1)" in key or "(B2)" in key or "(A2) (UC3M)" in key:
        #         university_name = "UC3M"
        #     elif "(A1)" in key or "(A2) (UAM)" in key:
        #         university_name = "UAM"
        #     else:
        #         university_name = key.split('(')[1]
        #         university_name = university_name[:-1]
        #     degree_name = "Grado en Ciencias"
        #     name = key.split('(')[0]
        #     name = name[:-1]

        #     university, _ = University.objects.get_or_create(
        #         name=university_name
        #     )

        #     university_degree = University.objects.get(name="UAM, UAB, UC3M")
        #     degree, _ = Degree.objects.get_or_create(
        #         name=degree_name, university=university_degree
        #     )

        #     subject_data = {
        #         'name': name,
        #         'subject_key': value['Codigo'] if 'Codigo' in value else \
        #             value['Código'],
        #         'year': value['Curso'],
        #         'semester': value['Cuatrimestre'],
        #         'credits': value['Créditos'],
        #         'language': value['Idioma'],
        #         'coordinator': value['Coordinador/a'],
        #         'previous_requirements': value['Requisitos previos'],
        #         'subject_url': value['Guia docente'],
        #         'content': value['Programa']
        #     }

        #     matching_subjects = Subject.objects.filter(degree=degree, 
        #         university=university, 
        #         subject_key=subject_data['subject_key']
        #     )

        #     if not matching_subjects.exists():
        #         subject = Subject.objects.create( 
        #             university=university, degree=degree, **subject_data
        #         )

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
                if university == "UAM":
                    key2 = capitalize_words(key2)
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

def capitalize_words(name):
    return ' '.join(word.capitalize() if len(word) > 3 else word.lower() for word in name.split())
