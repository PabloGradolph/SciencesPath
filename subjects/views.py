from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseBadRequest, HttpRequest, HttpResponse
from django.db.models import Sum
from django.db.models import Q
from django.contrib import messages

from decimal import Decimal
from datetime import datetime
from icalendar import Calendar
from datetime import datetime
from .models import Subject, SubjectRating, SubjectMaterial, TimeTable, SubjectSchedule, Dossier, SubjectInDossier, ExtraCurricularCredits
from social.models import Event
from .forms import SubjectFilterForm, SubjectMaterialForm

import pytz
import json
import html
import random


# Global variable
current_year = datetime.now().year


@login_required(login_url='login')
def index(request: HttpRequest) -> HttpResponse:
    """
    View function to display the index page with subjects.

    Retrieves subjects based on search query and filters,
    paginates the results, and renders the index page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object rendering the index page.
    """
    search_query = request.GET.get('search', '').strip()
    filter_form = SubjectFilterForm(request.GET)
    subjects = Subject.objects.all().order_by('degree')

    # Filter subjects based on search query
    if search_query:
        subjects = Subject.objects.filter(
            Q(name__icontains=search_query) | 
            Q(subject_key__icontains=search_query)
        )

    # Apply filters from the filter form
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

    # Pagination configuration
    items_per_page = 50
    paginator = Paginator(subjects, items_per_page)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    # Retain form data in pagination
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
def delete_review(request: HttpRequest, review_id: int, subject_id: int) -> HttpResponse:
    """
    View function to delete a review.

    Retrieves the review by its ID, deletes it, and redirects
    to the detail page of the subject associated with the review.

    Args:
        request (HttpRequest): The HTTP request object.
        review_id (int): The ID of the review to delete.
        subject_id (int): The ID of the subject associated with the review.

    Returns:
        HttpResponse: A redirect response to the detail page of the subject.
    """
    review = SubjectRating.objects.get(id=review_id)
    review.delete()
    return redirect('detail', subject_id=subject_id)


@login_required(login_url='login')
def detail(request: HttpRequest, subject_id: int) -> HttpResponse:
    """
    View function to display the details of a subject, including its ratings.

    Retrieves the subject by its ID and its associated ratings. Handles user ratings and comments.
    Calculates the average rating and percentage for the subject.

    Args:
        request (HttpRequest): The HTTP request object.
        subject_id (int): The ID of the subject to display details for.

    Returns:
        HttpResponse: A render response containing the details of the subject.
    """
    star_total = 5
    subject = get_object_or_404(Subject, id=subject_id)
    ratings = SubjectRating.objects.filter(subject=subject)
    user_rating = SubjectRating.objects.filter(subject=subject, user=request.user).first()
    
    # Define possible ratings from 1 to 5
    possible_ratings = [1, 2, 3, 4, 5]
    ratings_count = []

    # Calculate the percentage of each rating
    for rating in possible_ratings:
        quantity = 0
        for r in ratings:
            if r == rating:
                quantity += 1
        quantity = (quantity / star_total) * 100
        quantity = round((quantity / 10) * 10)
        quantity = str(quantity) + "%"
        ratings_count.append(quantity)

    if request.method == 'POST':
        # Handle the user's rating submission
        rating_value = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating_value and 1 <= int(rating_value) <= 5:
            if user_rating:
                user_rating.rating = rating_value
                user_rating.comment = comment
                user_rating.save()
            else:
                # Create a new rating instance if the user hasn't rated the subject before
                SubjectRating.objects.create(user=request.user, subject=subject, rating=rating_value, comment=comment)
            messages.success(request, 'Tu valoración ha sido registrada.')
            return redirect('detail', subject_id=subject_id)
    
    # Calculate the average rating for the subject
    avg_rating = subject.avg_rating()
    avg_rating_percentage = (avg_rating / star_total) * 100
    avg_rating_percentage_rounded = round((avg_rating_percentage / 10)*10)
    rating_range = range(1,6)
    context = {
        'subject': subject,
        'current_year': current_year,
        'ratings': ratings,
        'user_rating': user_rating,
        'rating_range': rating_range,
        'avg_1': ratings_count[0],
        'avg_2': ratings_count[1],
        'avg_3': ratings_count[2],
        'avg_4': ratings_count[3],
        'avg_5': ratings_count[4],
        'avg_rating': avg_rating,
        'avg_rating_percentage_rounded': avg_rating_percentage_rounded,
    }
    return render(request, 'subjects/detail.html', context)


@login_required(login_url='login')
def upload_material(request: HttpRequest, subject_id: int) -> HttpResponse:
    """
    View function to upload materials for a subject.

    Retrieves the subject by its ID and displays the upload form. Handles form submission to upload new materials.

    Args:
        request (HttpRequest): The HTTP request object.
        subject_id (int): The ID of the subject to upload materials for.

    Returns:
        HttpResponse: A render response containing the upload form and uploaded materials.
    """
    subject = get_object_or_404(Subject, pk=subject_id)
    materials = SubjectMaterial.objects.filter(subject=subject).order_by('material_type')
    
    if request.method == 'POST':
        # If the form is submitted, process the form data
        form = SubjectMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.subject = subject
            material.user = request.user
            material.save()
            return redirect('upload_material', subject_id=subject_id)
    else:
        # If the request is not POST, create a new form instance
        form = SubjectMaterialForm()
    
    return render(request, 'subjects/material.html', {'form': form, 'subject': subject, 'materials': materials, 'current_year': current_year})


@login_required(login_url='login')
@require_http_methods(["DELETE"])
def delete_material(request: HttpRequest, material_id: int) -> JsonResponse:
    """
    View function to delete a material.

    Retrieves the material by its ID and checks if the current user has permission to delete it.
    Deletes the material if the user has permission.

    Args:
        request (HttpRequest): The HTTP request object.
        material_id (int): The ID of the material to be deleted.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the deletion operation.
    """
    # Retrieve the material object or return a 404 error if not found
    material = get_object_or_404(SubjectMaterial, id=material_id)
    
    # Check if the current user has permission to delete the material
    if material.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para borrar este material.'}, status=403)
    
    # Delete the material
    material.delete()
    return JsonResponse({'message': 'Material borrado correctamente.'})


@login_required(login_url='login')
def horario(request:HttpRequest, subject_id: int) -> HttpResponse:
    """
    View function to display the schedule for a subject.

    Retrieves the subject by its ID and attempts to read the appropriate schedule file based on the university.
    Parses the schedule file and formats the events for display on the calendar.

    Args:
        request (HttpRequest): The HTTP request object.
        subject_id (int): The ID of the subject for which the schedule is requested.

    Returns:
        render: A rendered HTML page displaying the schedule for the subject.
    """
    # Retrieve the subject object or return a 404 error if not found
    subject = get_object_or_404(Subject, pk=subject_id)
    try:
        # Try to retrieve the timetable for the subject
        schedule = TimeTable.objects.get(subject=subject)
        c = None

        # Try to read the appropriate schedule file based on the university
        try:
            if subject.university.name == 'UAM':
                c = Calendar.from_ical(schedule.schedule_file_uam.read())
            elif subject.university.name == 'UC3M':
                c = Calendar.from_ical(schedule.schedule_file_uc3m.read())
            elif subject.university.name == 'UAB':
                c = Calendar.from_ical(schedule.schedule_file_uab.read())
        except FileNotFoundError:
            return render(request, 'subjects/error.html', {'error': 'No se ha encontrado un horario para esta asignatura.', 'subject_url': subject.subject_url})
    
        events = []
        if c is not None:
        
            for event in c.walk('vevent'):
                dtstart_utc = event.decoded('dtstart')
                dtend_utc = event.decoded('dtend')

                formatted_event = {
                    'title': html.unescape(event.get('summary')),
                    'start': dtstart_utc.strftime('%Y-%m-%dT%H:%M:%S'),
                    'end': dtend_utc.strftime('%Y-%m-%dT%H:%M:%S'),
                    'location': html.unescape(event.get('location', 'Ubicación no especificada')),
                }
                events.append(formatted_event)
                
        events_json = json.dumps(events)
    
    except TimeTable.DoesNotExist:
        return render(request, 'subjects/error.html', {'error': 'No se ha encontrado un horario para esta asignatura.', 'subject_url': subject.subject_url})

    return render(request, 'subjects/horarios.html', {
        'subject': subject,
        'current_year': current_year,
        'schedule': schedule,
        'events_json': events_json,
        })


@login_required(login_url='login')
def search_subjects(request: HttpRequest) -> JsonResponse:
    """
    View function to search for subjects based on a query string.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of matching subjects.
    """
    search_query = request.GET.get('search_query', '')
    subjects = Subject.objects.filter(name__icontains=search_query) | Subject.objects.filter(subject_key__icontains=search_query)
    subjects_list = list(subjects.values('id', 'name', 'subject_key', 'degree__name'))
    response = JsonResponse({'subjects': subjects_list})
    return response


@login_required(login_url='login')
def parse_ics_to_json(request: HttpRequest, subject_id: int) -> JsonResponse:
    """
    View function to parse an ICS file for a subject and add its events to the user's schedule.

    Parses the ICS file associated with the subject, extracts its events, and adds them to the user's schedule.
    Returns a JSON response with the details of the added events.

    Args:
        request (HttpRequest): The HTTP request object.
        subject_id (int): The ID of the subject.

    Returns:
        JsonResponse: A JSON response containing the details of the added events or an error message.
    """
    # Ensure the request is AJAX
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('Acceso no permitido')
    
    # Get the subject object and generate a random color for the subject schedule
    subject = get_object_or_404(Subject, pk=subject_id)
    color = '#' + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])  # Genera un color hex aleatorio
 
    try:
        # Check if the user already has too many subjects in their schedule
        if SubjectSchedule.objects.filter(user=request.user).count() >= 12:
            return JsonResponse({'error': 'No puedes tener más de 12 asignaturas en tu horario.'}, status=401)

        # Check if the user already has the subject in their schedule
        if SubjectSchedule.objects.filter(user=request.user, subject=subject).exists():
            return JsonResponse({'error': 'El usuario ya tiene esta asignatura en su horario.'}, status=400)

        # Get the timetable for the subject and parse its events
        schedule = TimeTable.objects.get(subject=subject)
        c = None
        try:
            if subject.university.name == 'UAM':
                c = Calendar.from_ical(schedule.schedule_file_uam.read())
            elif subject.university.name == 'UC3M':
                c = Calendar.from_ical(schedule.schedule_file_uc3m.read())
            elif subject.university.name == 'UAB':
                c = Calendar.from_ical(schedule.schedule_file_uab.read())
        except FileNotFoundError:
            return JsonResponse({'error': 'Horario no encontrado para la asignatura.'}, status=404)

        # List to store parsed events
        events = []

        if c:
            # Convert event times to local timezone and add events to the schedule
            subject_schedule = SubjectSchedule.objects.create(
                user=request.user,
                subject=subject,
                color=color
            )
            for event in c.walk('vevent'):
                title = html.unescape(event.get('summary'))
                if "Día festi" in title or "Dia festi" in title:
                    continue

                dtstart_utc = event.decoded('dtstart')
                dtend_utc = event.decoded('dtend')

                # Create an Event object for each event in the schedule
                created_event = Event.objects.create(
                    user=request.user,
                    title=html.unescape(event.get('summary')),
                    start_time=dtstart_utc,
                    end_time=dtend_utc,
                    location=html.unescape(event.get('location', 'Ubicación no especificada')),
                    description=html.unescape(event.get('description', '')),
                    is_all_day=False,
                    subject_id=subject_id
                )
                
                # Append event details to the list of events
                formatted_event = {
                    'id': created_event.id,
                    'title': title,
                    'start': dtstart_utc.strftime('%Y-%m-%dT%H:%M:%S'),
                    'end': dtend_utc.strftime('%Y-%m-%dT%H:%M:%S'),
                    'location': html.unescape(event.get('location', 'Ubicación no especificada')),
                    'color': color,
                    'subject': subject_id
                }
                events.append(formatted_event)
                
        return JsonResponse({'events': events})

    except TimeTable.DoesNotExist:
        return JsonResponse({'error': 'Horario no encontrado para la asignatura.'}, status=404)
    

@login_required(login_url='login')
def add_subject_to_dossier(request: HttpRequest) -> JsonResponse:
    """
    View function to add a subject to the user's dossier.

    Parses the request to extract subject and grade information, validates the data, and adds the subject to the user's dossier.
    Returns a JSON response with the status of the operation and additional information about the updated dossier.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the status of the operation and additional dossier information.
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user = request.user
        data = json.loads(request.body)
        subject_id = data.get('subject_id')
        grade = data.get('grade')

        # Convert grade to Decimal format
        if grade == 'N/A':
            grade = None
            grade_decimal = None
        elif ',' in grade:
            grade = grade.replace(',', '.')
            grade_decimal = Decimal(grade)
        else:
            grade_decimal = Decimal(grade)

        try:
            # Validate required data
            if subject_id is None:
                return HttpResponseBadRequest("Faltan datos para añadir la asignatura al expediente.")

            # Get the subject object
            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                return HttpResponseBadRequest("La asignatura especificada no existe.")

            # Get or create the Dossier for the current user
            dossier, _ = Dossier.objects.get_or_create(user=user)

            # Check if adding the subject exceeds the credit limit
            total_credits = dossier.subjectindossier_set.aggregate(
                total=Sum('subject__credits')
            )['total'] or 0
            new_subject_credits = Subject.objects.get(id=subject_id).credits

            if total_credits + new_subject_credits > 245:
                return JsonResponse({
                    'error': 'No se puede añadir la asignatura debido al límite de créditos.'
                }, status=400)
            
            # Check if the subject is already in the dossier
            if SubjectInDossier.objects.filter(dossier=dossier, subject=subject).exists():
                return JsonResponse({
                    'error': 'La asignatura ya ha sido añadida al expediente.'
                }, status=400)
        
            # Add the subject and grade to the dossier
            new_subject_in_dossier = SubjectInDossier.objects.create(dossier=dossier, subject=subject, grade=grade_decimal)

            # Return additional dossier information for the frontend
            return JsonResponse({
                'status': 'success',
                'message': 'Asignatura añadida al expediente con éxito.',
                'subject_name': subject.name,
                'subject_code': subject.subject_key,
                'credits': subject.credits,
                'grade': grade,
                'average_grade': dossier.calculate_average_grade(),
                'total_credits': dossier.total_credits(),
                'credits_achieved': dossier.credits_achieved(),
                'credits_remaining': dossier.credits_remaining(),
                'subject_in_dossier_id': new_subject_in_dossier.id,
            })

        except Exception as e:
            return HttpResponseBadRequest(f"Error al procesar la solicitud: {str(e)}")
    else:
        return HttpResponseBadRequest("Solicitud no válida.")
    

@login_required(login_url='login')
@require_http_methods(["DELETE"])
def delete_subject_from_dossier(request: HttpRequest, subject_in_dossier_id: int) -> JsonResponse:
    """
    View function to delete a subject from the user's dossier.

    Args:
        request (HttpRequest): The HTTP request object.
        subject_in_dossier_id (int): The ID of the subject in the dossier to delete.

    Returns:
        JsonResponse: A JSON response containing the updated dossier information.
    """
    subject_in_dossier = get_object_or_404(SubjectInDossier, pk=subject_in_dossier_id)
    dossier = subject_in_dossier.dossier
    subject_in_dossier.delete()

    # Recalculate values after deletion
    average_grade = dossier.calculate_average_grade()
    total_credits = dossier.total_credits()
    credits_achieved = dossier.credits_achieved()
    credits_remaining = dossier.credits_remaining()

    # Return response with updated values
    return JsonResponse({
        'average_grade': average_grade,
        'total_credits': total_credits,
        'credits_achieved': credits_achieved,
        'credits_remaining': credits_remaining,
    })


@login_required(login_url='login')
def add_extra_credits(request: HttpRequest) -> JsonResponse:
    """
    View function to add extra-curricular credits to the user's dossier.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the updated dossier information.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        credits = data.get('credits')

        # Basic validation
        if not name or credits <= 0:
            return HttpResponseBadRequest("Datos inválidos.")

        dossier, _ = Dossier.objects.get_or_create(user=request.user)

        # Calculate the total sum of current extra-curricular credits
        total_extra_credits = sum(credit.credits for credit in dossier.extra_curricular_credits.all())
        if total_extra_credits + credits > 6:
            return JsonResponse({'error': 'La suma total de créditos extracurriculares no puede exceder 6.'}, status=400)

        new_extra_credits = ExtraCurricularCredits.objects.create(dossier=dossier, name=name, credits=credits)
        average_grade = dossier.calculate_average_grade()
        credits_achieved = dossier.credits_achieved()
        credits_remaining = dossier.credits_remaining()
        total_credits = dossier.total_credits()
        
        return JsonResponse({'status': 'success', 'message': 'Créditos extracurriculares añadidos con éxito.', 
                             'new_extra_credits_id': new_extra_credits.id, 
                            'average_grade': average_grade,
                            'credits_achieved': credits_achieved,
                            'credits_remaining': credits_remaining,
                            'total_credits': total_credits,
                            })
    else:
        return HttpResponseBadRequest("Método no permitido.")
    

@login_required(login_url='login')
@require_http_methods(["DELETE"])
def delete_extra_credit(request: HttpRequest, extra_credit_id: int) -> JsonResponse:
    """
    View function to delete an extra-curricular credit from the user's dossier.

    Deletes the specified extra-curricular credit from the user's dossier, recalculates
    dossier statistics, and returns a JSON response with the updated dossier information.

    Args:
        request (HttpRequest): The HTTP request object.
        extra_credit_id (int): The ID of the extra-curricular credit to delete.

    Returns:
        JsonResponse: A JSON response containing the updated dossier information.
    """
    if request.method == 'DELETE':
        try:
            extra_credit = ExtraCurricularCredits.objects.get(id=extra_credit_id, dossier__user=request.user)
            extra_credit.delete()

            # Recalculate values after deleting the credit
            dossier = Dossier.objects.get(user=request.user)
            average_grade = dossier.calculate_average_grade()
            credits_achieved = dossier.credits_achieved()
            credits_remaining = dossier.credits_remaining()
            total_credits = dossier.total_credits()

            # Return recalculated values in the response
            return JsonResponse({
                'message': 'Crédito extracurricular eliminado con éxito.',
                'average_grade': average_grade,
                'credits_achieved': credits_achieved,
                'credits_remaining': credits_remaining,
                'total_credits': total_credits,
            })
        except ExtraCurricularCredits.DoesNotExist:
            return HttpResponseBadRequest('Crédito extracurricular no encontrado.')
    else:
        return HttpResponseBadRequest('Método no permitido.')


@login_required(login_url='login')
def add_event(request: HttpRequest) -> JsonResponse:
    """
    View function to add a new event.

    Creates a new event object based on the data provided in the request body
    and saves it to the database.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating the status of the operation and
        optionally containing the ID of the newly created event.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        event = Event.objects.create(
            user=request.user,
            title=data['title'],
            start_time=data['start'],
            end_time=data['end'],
            is_all_day=data['allDay']
        )
        return JsonResponse({'status': 'success', 'event_id': event.id})
    return JsonResponse({'status': 'error'}, status=400)


@login_required(login_url='login')
def update_event(request: HttpRequest) -> JsonResponse:
    """
    View function to update an existing event.

    Retrieves the event object from the database based on the provided ID and user,
    updates its attributes with the data from the request body, and saves the changes.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating the status of the operation.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            event = Event.objects.get(id=data['id'], user=request.user)
            event.title = data['title']
            event.start_time = data['start']
            event.end_time = data['end']
            event.is_all_day = data['allDay']
            event.save()
            return JsonResponse({'status': 'success'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)


@login_required(login_url='login')
def delete_event(request: HttpRequest, event_id: int) -> JsonResponse:
    """
    View function to delete an existing event.

    Retrieves the event object from the database based on the provided ID and user,
    and deletes it.

    Args:
        request (HttpRequest): The HTTP request object.
        event_id (int): The ID of the event to be deleted.

    Returns:
        JsonResponse: A JSON response indicating the status of the operation.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Autenticación requerida'}, status=401)

    event = get_object_or_404(Event, id=event_id, user=request.user)
    event.delete()
    return JsonResponse({'status': 'success'})