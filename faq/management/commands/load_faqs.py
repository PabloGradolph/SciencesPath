from django.core.management.base import BaseCommand
from ...models import FAQ

class Command(BaseCommand):
    help = 'Loading FAQ in the database'

    def handle(self, *args, **options):
        questions = [
            {'question': '¿A qué universidad voy después del segundo cuatrimestre de 2º?', 
            'answer': 'Una vez terminado el segundo cuatrimestre de 2º, cada alumno continuará sus estudios en la universidad en la que fue aceptado. Sin embargo, existe la posibilidad de solicitar un traslado de universidad.'},
            {'question': "¿Puedo cursar cualquier asignatura de la universidad?",
            'answer': "Podrás cursar únicamente las asignaturas de la facultad/campus al que pertenezcas:\n\t- UAM: Cualquier asignatura de las facultades de Ciencias y/o Biología.\n\t- UAB: Cualquier asignatura de las facultades de Ciencias y/o Biociencias.\n\t- UC3M: Cualquier asignatura del campus de Leganés."},
            {'question': "¿Cuántos créditos externos a asignaturas me puedo convalidar?",
            'answer': "Puedes convalidar un máximo de 6 créditos externos, que pueden provenir de idioma, deportes, prácticas extracurriculares u otras modalidades."},
            {'question': "¿Puedo realizar mis prácticas externas en verano?",
            'answer': "Si es posible realizar la prácticas externas en verano, pero es necesario que te hayas matriculado previemente de la asignatura. No puedes hacerlas en verano si no estás matriculado de la asignatura. También tienes la opción de hacerlas extracurriculares y luego convalidar los créditos (si te lo aceptan)"},
            {'question': "¿Cuándo debo saber el tema y tutor de mi TFG?",
            'answer': "Por lo general, es conveniente comunicar al coordinador de las prácticas de tu universidad tanto el tema como el tutor de TFG antes de matricularte de la asignatura aqunque podría haber excepciones. Recuerda que tienes que tener superados un mínimo de 150 créditos para poder matrícularte de la asignatura de TFG."},
            {'question': "¿Qué universidad gestiona las prácticas externas?",
            'answer': "Aunque la matrícula la hagas por la UAM, si perteneces a la UC3M o UAB, generan una copia en dichas universidades. Podrás realizar tus prácticas a través de la OPE de tu universidad y con un tutor académico de prácticas de tu universidad."}
        ]

        for question in questions:
            FAQ.objects.get_or_create(question=question['question'], answer=question['answer'])