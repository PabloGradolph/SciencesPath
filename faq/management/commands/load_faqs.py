from django.core.management.base import BaseCommand
from typing import Any
from ...models import FAQ


class Command(BaseCommand):
    """Loads predefined FAQ data into the database."""

    help = 'Loading FAQ in the database'

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Executes the command to load FAQs into the database.

        Args:
            *args: Variable length argument list, not used in this command.
            **options: Arbitrary keyword options, not used in this command.

        Returns:
            None
        """
        questions = [
            {'question': '¿A qué universidad voy después del segundo cuatrimestre de 2&ordm?', 
            'answer': 'Una vez terminado el segundo cuatrimestre de 2&ordm, cada alumno continuará sus estudios en la universidad en la que fue aceptado. Sin embargo, existe la posibilidad de solicitar un traslado de universidad.'},
            {'question': "¿Puedo cursar cualquier asignatura de la universidad?",
            'answer': "Podrás cursar únicamente las asignaturas de la facultad/campus al que pertenezcas:\n\t- UAM: Cualquier asignatura de las facultades de Ciencias y/o Biología.\n\t- UAB: Cualquier asignatura de las facultades de Ciencias y/o Biociencias.\n\t- UC3M: Cualquier asignatura del campus de Leganés."},
            {'question': "¿Cuántos créditos externos a asignaturas me puedo convalidar?",
            'answer': "Puedes convalidar un máximo de 6 créditos externos, que pueden provenir de idioma, deportes, prácticas extracurriculares u otras modalidades."},
            {'question': "¿Puedo realizar mis prácticas externas en verano?",
            'answer': "Si es posible realizar la prácticas externas en verano, pero es necesario que te hayas matriculado previemente de la asignatura. No puedes hacerlas en verano si no estás matriculado de la asignatura. También tienes la opción de hacerlas extracurriculares y luego convalidar los créditos (si te lo aceptan)"},
            {'question': "¿Cuándo debo saber el tema y tutor de mi TFG?",
            'answer': "Por lo general, es conveniente comunicar al coordinador de las prácticas de tu universidad tanto el tema como el tutor de TFG antes de matricularte de la asignatura aqunque podría haber excepciones. Recuerda que tienes que tener superados un mínimo de 150 créditos para poder matrícularte de la asignatura de TFG."},
            {'question': "¿Qué universidad gestiona las prácticas externas?",
            'answer': "Aunque pertenezcas a las universidades UC3M o UAB, la gestión de las prácticas externas se hará por la OPE de la UAM, ellos llevarán a cabo todos los procedimientos y tu tutor académico deberá ser también de la UAM. En caso de ser curriculares, también se evaluará allí tu asignatura."}
        ]

        for question in questions:
            FAQ.objects.get_or_create(question=question['question'], answer=question['answer'])