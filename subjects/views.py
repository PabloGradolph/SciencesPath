from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Sum
from .models import Subject, SubjectRating, SubjectMaterial, TimeTable, SubjectSchedule, Dossier, SubjectInDossier, ExtraCurricularCredits
from social.models import Event
from decimal import Decimal
from django.db.models import Q
from django.contrib import messages
from datetime import datetime
from .forms import SubjectFilterForm, SubjectMaterialForm
from icalendar import Calendar
import pytz
from datetime import datetime
import json
import html
import random

current_year = datetime.now().year

@login_required(login_url='login')
def index(request):
    search_query = request.GET.get('search', '').strip()
    filter_form = SubjectFilterForm(request.GET)
    subjects = Subject.objects.all().order_by('degree')

    if search_query:
        subjects = Subject.objects.filter(
            Q(name__icontains=search_query) | 
            Q(subject_key__icontains=search_query)
        )

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
def delete_review(request, review_id, subject_id):
    review = SubjectRating.objects.get(id=review_id)
    review.delete()
    return redirect('detail', subject_id=subject_id)

@login_required(login_url='login')
def detail(request, subject_id):
    star_total = 5
    subject = get_object_or_404(Subject, id=subject_id)
    ratings = SubjectRating.objects.filter(subject=subject)
    user_rating = SubjectRating.objects.filter(subject=subject, user=request.user).first()
    
    possible_ratings = [1, 2, 3, 4, 5]
    ratings_count = []
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
        rating_value = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating_value and 1 <= int(rating_value) <= 5:
            if user_rating:
                user_rating.rating = rating_value
                user_rating.comment = comment
                user_rating.save()
            else:
                SubjectRating.objects.create(user=request.user, subject=subject, rating=rating_value, comment=comment)
            messages.success(request, 'Tu valoración ha sido registrada.')
            return redirect('detail', subject_id=subject_id)
    
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

# TODO terminar esta view.
@login_required(login_url='login')
def upload_material(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    
    if request.method == 'POST':
        form = SubjectMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.subject = subject
            material.save()
            return redirect('detail', subject_id=subject_id)
    else:
        form = SubjectMaterialForm()
    
    return render(request, 'subjects/material.html', {'form': form, 'subject': subject, 'current_year': current_year})

@login_required(login_url='login')
def horario(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    try:
        schedule = TimeTable.objects.get(subject=subject)
        c = None

        # Intenta leer el archivo de horario adecuado según la universidad
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
        
            local_timezone = pytz.timezone('Europe/Madrid')
            for event in c.walk('vevent'):
                dtstart_utc = event.decoded('dtstart')
                dtend_utc = event.decoded('dtend')
                dtstart_local = dtstart_utc.astimezone(local_timezone)
                dtend_local = dtend_utc.astimezone(local_timezone)

                formatted_event = {
                    'title': html.unescape(event.get('summary')),
                    'start': dtstart_local.strftime('%Y-%m-%dT%H:%M:%S'),
                    'end': dtend_local.strftime('%Y-%m-%dT%H:%M:%S'),
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
def search_subjects(request):
    search_query = request.GET.get('search_query', '')
    subjects = Subject.objects.filter(name__icontains=search_query) | Subject.objects.filter(subject_key__icontains=search_query)
    subjects_list = list(subjects.values('id', 'name', 'subject_key', 'degree__name'))
    response = JsonResponse({'subjects': subjects_list})
    return response


@login_required(login_url='login')
def parse_ics_to_json(request, subject_id):
    # Asegurarse de que la petición es AJAX
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('Acceso no permitido')
    
    subject = get_object_or_404(Subject, pk=subject_id)
    color = '#' + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])  # Genera un color hex aleatorio
 
    try:

        if SubjectSchedule.objects.filter(user=request.user, subject=subject).exists():
            return JsonResponse({'error': 'El usuario ya tiene esta asignatura en su horario.'}, status=400)

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

        events = []
        if c:
            local_timezone = pytz.timezone('Europe/Madrid')
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
                dtstart_local = dtstart_utc.astimezone(local_timezone)
                dtend_local = dtend_utc.astimezone(local_timezone)

                created_event = Event.objects.create(
                    user=request.user,
                    title=html.unescape(event.get('summary')),
                    start_time=dtstart_local,
                    end_time=dtend_local,
                    location=html.unescape(event.get('location', 'Ubicación no especificada')),
                    description=html.unescape(event.get('description', '')),
                    is_all_day=False,
                    subject_id=subject_id
                )
                
                formatted_event = {
                    'id': created_event.id,
                    'title': title,
                    'start': dtstart_local.strftime('%Y-%m-%dT%H:%M:%S'),
                    'end': dtend_local.strftime('%Y-%m-%dT%H:%M:%S'),
                    'location': html.unescape(event.get('location', 'Ubicación no especificada')),
                    'color': color,
                    'subject': subject_id
                }
                events.append(formatted_event)
                
        return JsonResponse({'events': events})

    except TimeTable.DoesNotExist:
        return JsonResponse({'error': 'Horario no encontrado para la asignatura.'}, status=404)
    

@login_required(login_url='login')
def add_subject_to_dossier(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user = request.user
        data = json.loads(request.body)
        subject_id = data.get('subject_id')
        grade = data.get('grade')
        if grade == 'N/A':
            grade = None
            grade_decimal = None
        elif ',' in grade:
            grade = grade.replace(',', '.')
            grade_decimal = Decimal(grade)
        else:
            grade_decimal = Decimal(grade)

        try:
            # Valida que tengamos los datos necesarios
            if subject_id is None:
                print("Datos")
                return HttpResponseBadRequest("Faltan datos para añadir la asignatura al expediente.")

            # Obtiene el subject basado en el subject_id proporcionado
            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                print("Subject")
                return HttpResponseBadRequest("La asignatura especificada no existe.")

            # Obtiene o crea el Dossier para el usuario actual
            dossier, _ = Dossier.objects.get_or_create(user=user)

            total_credits = dossier.subjectindossier_set.aggregate(
                total=Sum('subject__credits')
            )['total'] or 0
            new_subject_credits = Subject.objects.get(id=subject_id).credits

            if total_credits + new_subject_credits > 245:
                return JsonResponse({
                    'error': 'No se puede añadir la asignatura debido al límite de créditos.'
                }, status=400)
            
            if SubjectInDossier.objects.filter(dossier=dossier, subject=subject).exists():
                return JsonResponse({
                    'error': 'La asignatura ya ha sido añadida al expediente.'
                }, status=400)
        
            # Añade la asignatura y la nota al expediente (Dossier)
            new_subject_in_dossier = SubjectInDossier.objects.create(dossier=dossier, subject=subject, grade=grade_decimal)

            # Aquí puedes devolver cualquier información adicional necesaria para el front-end
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
            print("Exception")
            return HttpResponseBadRequest(f"Error al procesar la solicitud: {str(e)}")
    else:
        print("Solicitud")
        return HttpResponseBadRequest("Solicitud no válida.")
    

@login_required(login_url='login')
@require_http_methods(["DELETE"])
def delete_subject_from_dossier(request, subject_in_dossier_id):
    subject_in_dossier = get_object_or_404(SubjectInDossier, pk=subject_in_dossier_id)
    dossier = subject_in_dossier.dossier
    subject_in_dossier.delete()

    # Recalcular los valores después de la eliminación
    average_grade = dossier.calculate_average_grade()
    total_credits = dossier.total_credits()
    credits_achieved = dossier.credits_achieved()
    credits_remaining = dossier.credits_remaining()

    # Devolver la respuesta con los valores actualizados
    return JsonResponse({
        'average_grade': average_grade,
        'total_credits': total_credits,
        'credits_achieved': credits_achieved,
        'credits_remaining': credits_remaining,
    })


@login_required(login_url='login')
def add_extra_credits(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        credits = data.get('credits')

        # Validación básica
        if not name or credits <= 0:
            return HttpResponseBadRequest("Datos inválidos.")

        dossier, _ = Dossier.objects.get_or_create(user=request.user)

        # Calcular la suma total de créditos extracurriculares actuales
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
def delete_extra_credit(request, extra_credit_id):
    if request.method == 'DELETE':
        try:
            extra_credit = ExtraCurricularCredits.objects.get(id=extra_credit_id, dossier__user=request.user)
            extra_credit.delete()

            # Recalcular valores después de eliminar el crédito
            dossier = Dossier.objects.get(user=request.user)
            average_grade = dossier.calculate_average_grade()
            credits_achieved = dossier.credits_achieved()
            credits_remaining = dossier.credits_remaining()
            total_credits = dossier.total_credits()

            # Devolver valores recalculados en la respuesta
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
def add_event(request):
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
def update_event(request):
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
def delete_event(request, event_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Autenticación requerida'}, status=401)

    event = get_object_or_404(Event, id=event_id, user=request.user)
    event.delete()
    return JsonResponse({'status': 'success'})