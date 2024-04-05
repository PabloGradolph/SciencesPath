from django.core.management.base import BaseCommand
from typing import Any
import json
from ...models import Subject, Degree


class Command(BaseCommand):
    """
    A command to solve some information errors that JSON files have.
    """
    help = 'Corrige errores en los archivos json de las asignaturas.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Ruta al archivo JSON con las correcciones.')

    def handle(self, *args: Any, **options: Any) -> None:
        json_file_path = options['json_file']
        # correct_json_file(json_file_path)
        update_database_with_json(json_file_path)


def update_database_with_json(json_file_path: str) -> None:
    """
    Corrects also the changes in the database

    Args:
        json_file_path (str): Path to JSON file.
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    first_key = next(iter(data))
    if first_key.endswith("UAM"):
        biology_degree = Degree.objects.get(name='Grado en Biología')
        subjects_in_biology = Subject.objects.filter(degree=biology_degree)
        zoology = subjects_in_biology.filter(name="ZOOLOGÍA")
        zoology.credits = 12
        zoology.save()
        error2 = subjects_in_biology.filter(name="BIOLOGÍA CELULAR E HISTOLOGÍA")
        error2.semester = "Anual"
        error2.credits = 12
        error2.save()
        error3 = subjects_in_biology.filter(name="BIOLOGÍA CELULAR E HISTOLOGÍA")
        
    elif first_key.endswith("UAB"):
        pass

    elif first_key.endswith("UC3M"):
        pass

    else: # Handle corrections for the "Grado en Ciencias"
        pass

    print("Base de datos actualizada con éxito.")

# def correct_json_file(json_file_path: str) -> None:
#     """
#     Opens a JSON file, corrects specific errors based on university identifiers, and writes the corrections back to the file.

#     Args:
#         json_file_path (str): The file path to the JSON data file to be corrected.
#     """
#     with open(json_file_path, 'r', encoding='utf-8') as file:
#         data = json.load(file)

#     # Identify the university based on the first key and apply specific corrections
#     first_key = next(iter(data))
#     if first_key.endswith("UAM"):
#         biology_degree = data["Grado en Biología | UAM"]
#         zoology = biology_degree["ZOOLOGÍA"]
#         zoology["Créditos"] = 12
        
#     elif first_key.endswith("UAB"):
#         error = data["Grau en Matemàtiques | UAB"]
#         # del(error["Prácticas en empresas"])

#     elif first_key.endswith("UC3M"):
#         error = data["Grado en Ingeniería en Tecnologías Industriales | UC3M"]
#         # del(error["Trabajo fin de Grado"])
#         # del(error["Prácticas Externas (A), (B), (C), (D), (E),"])

#     else: # Handle corrections for the "Grado en Ciencias"
#         pass
    
#     with open(json_file_path, 'w', encoding='utf-8') as file:
#         json.dump(data, file, ensure_ascii=False, indent=4)

#     print('Json actualizado con éxito.')