from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    help = 'Corrige errores en los archivos json de las asignaturas.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Ruta al archivo JSON con las correcciones.')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        main_function(json_file_path)


def main_function(json_file_path: str) -> None:
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    first_key = next(iter(data))
    if first_key.endswith("UAM"):
        error = data["Grado en Biología | UAM"]
        
    elif first_key.endswith("UAB"):
        error = data["Grau en Matemàtiques | UAB"]
        del(error["Prácticas en empresas"])

    elif first_key.endswith("UC3M"):
        error = data["Grado en Ingeniería en Tecnologías Industriales | UC3M"]
        del(error["Trabajo fin de Grado"])
        del(error["Prácticas Externas (A), (B), (C), (D), (E),"])

    else: # Grado en Ciencias
        pass
    
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print("Correcciones aplicadas correctamente.")