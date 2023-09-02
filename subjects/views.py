from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.core.paginator import Paginator
from .models import Subject
from django.db.models import Q
from datetime import datetime
from .forms import SubjectFilterForm

current_year = datetime.now().year

@login_required(login_url='login')
def index(request):
    search_query = request.GET.get('search', '').strip()
    subjects = Subject.objects.filter(
        Q(name__icontains=search_query) | Q(university__name__icontains=search_query)
        | Q(degree__name__icontains=search_query)
    )

    filter_form = SubjectFilterForm(request.GET)  # Crear el formulario con los datos de la solicitud GET

    if filter_form.is_valid():
        degree = filter_form.cleaned_data.get('degree')
        university = filter_form.cleaned_data.get('university')
        credits = filter_form.cleaned_data.get('credits')
        year = filter_form.cleaned_data.get('year')
        semester = filter_form.cleaned_data.get('semester')

        if degree:
            subjects = subjects.filter(degree=degree)
        if university:
            subjects = subjects.filter(university=university)
        if credits:
            subjects = subjects.filter(credits=credits)
        if year:
            subjects = subjects.filter(year=year)
        if semester:
            if semester == '1':
                subjects = subjects.filter(Q(semester='1') | Q(semester='Primer semestre'))
            elif semester == '2':
                subjects = subjects.filter(Q(semester='2') | Q(semester='Segundo semestre'))
            elif semester == 'A':
                subjects = subjects.filter(Q(semester='A') | Q(semester='Anual'))

    # Configuración de la paginación
    items_per_page = 50
    paginator = Paginator(subjects, items_per_page)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    # Recuperar los datos del formulario para mantenerlos en la paginación
    form_data = request.GET.copy()
    if 'page' in form_data:
        del form_data['page']

    context = {
        'page_subjects': page,
        'current_year': current_year,
        'search_query': search_query,
        'filter_form': filter_form,
        'form_data': form_data,
    }
    return render(request, 'subjects/index.html', context)


@login_required(login_url='login')
def detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    context = {'subject': subject, 'current_year': current_year}
    return render(request, 'subjects/detail.html', context)