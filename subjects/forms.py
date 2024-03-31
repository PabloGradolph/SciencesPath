from django import forms
from django.core.validators import FileExtensionValidator
from .models import Degree, University, Subject, SubjectMaterial


class SubjectFilterForm(forms.Form):
    """
    A form for filtering Subject instances based on degree, university, credits, year, and semester.
    """
    degree = forms.ModelChoiceField(queryset=Degree.objects.all(), required=False, empty_label="Todos", label="Grado")
    university = forms.ModelChoiceField(queryset=University.objects.all(), required=False, empty_label="Todas", label="Universidad")
    credits = forms.ChoiceField(choices=[], required=False, label="Créditos")
    year = forms.ChoiceField(choices=[], required=False, label="Curso")

    SEMESTER_CHOICES = [
        ('', 'Todos'),
        ('1', 'Primer Cuatrimestre'),
        ('2', 'Segundo Cuatrimestre'),
        ('A', 'Anual'),
    ]
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, required=False, label="Cuatrimestre")

    def __init__(self, *args, **kwargs):
        """
        Initializes the form with dynamic choices for the 'credits' and 'year' fields.
        """
        super().__init__(*args, **kwargs)
        self.fields['credits'].choices = self.get_credits_choices()
        self.fields['year'].choices = self.get_year_choices()
    
    def get_credits_choices(self) -> list:
        """
        Retrieves a list of distinct credit values from Subject instances to use as form choices.

        Returns:
            list: A list of tuples for the 'credits' field choices.
        """
        credits_choices =  [(str(credits), str(credits)) for credits in Subject.objects.order_by('credits').values_list('credits', flat=True).distinct()]
        credits_choices.insert(0, ('', 'Todos'))
        return credits_choices

    def get_year_choices(self) -> list:
        """
        Retrieves a list of distinct year values from Subject instances to use as form choices.

        Returns:
            list: A list of tuples for the 'year' field choices.
        """
        year_choices = [(str(year), str(year)) for year in Subject.objects.order_by('year').values_list('year', flat=True).distinct()]
        if ('', '') in year_choices:
            year_choices.remove(('', ''))
        year_choices.insert(0, ('', 'Todos'))
        return year_choices


class SubjectMaterialForm(forms.ModelForm):
    """
    A form for uploading subject-related materials, specifically PDF files.
    """
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

    class Meta:
        model = SubjectMaterial
        fields = ['title', 'material_type', 'file']
        labels = {
            'title': 'Título',
            'material_type': 'Tipo de material',
            'file': 'Archivo',
        }