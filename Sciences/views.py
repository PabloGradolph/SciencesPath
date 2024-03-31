from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.core.serializers import serialize
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from datetime import datetime
from .forms import CustomUserCreationForm, SetPasswordForm
from django.contrib.auth.forms import PasswordResetForm
from faq.models import FAQ
from subjects.models import Subject, SubjectSchedule, Dossier, SubjectInDossier
from social.models import Event, Profile
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q
from .tokens import account_activation_token
import re
import json

# Global variable
current_year = datetime.now().year

def home(request: HttpRequest) -> HttpResponse:
    """
    Renders the home page of the site's Science section.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse object rendering the 'Sciences/home.html' template with the provided context.
    """
    return render(request, 'Sciences/home.html', {'current_year': current_year})

@login_required(login_url='login')
def main(request: HttpRequest) -> HttpResponse:
    """
    Renders the main page of the Science section, requiring authentication.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse object rendering the 'Sciences/main.html' template with the provided context, including the current year and FAQs.
    """
    faqs = FAQ.objects.all()
    context = {'current_year': current_year, 'faqs': faqs}
    return render(request, 'Sciences/main.html', context)


@login_required(login_url='login')
def profile(request, username):
    user = User.objects.get(username=username)
    posts = user.posts.all()
    events = user.events.all()
    user_subjects = user.subject_schedules.all()
    subjects_colors = {subject.subject_id: subject.color for subject in user_subjects}

    events_json = json.loads(serialize('json', events))

    for event in events_json:
        if "Día festi" in event['fields']['title'] or "Dia festi" in event['fields']['title']:
            continue

        subject_id = event['fields'].get('subject')
        event_color = subjects_colors.get(subject_id, '#3788D8')

        event['fields']['id'] = event['pk']
        event['fields']['start'] = event['fields']['start_time']
        event['fields']['end'] = event['fields']['end_time']
        event['fields']['allDay'] = event['fields']['is_all_day']
        event['fields']['title'] = event['fields']['title']
        event['fields']['description'] = event['fields']['description']
        event['fields']['location'] = event['fields']['location']
        event['fields']['color'] = event_color
        event['fields']['textColor'] = '#ffffff'

        del event['fields']['user']
        del event['fields']['start_time']
        del event['fields']['end_time']
        del event['fields']['is_all_day']

    events_json = json.dumps([event['fields'] for event in events_json])

    # Obtener los ids de las asignaturas del usuario
    subject_ids = user.subject_schedules.values_list('subject_id', flat=True)

    # Usar esos ids para obtener los objetos Subject correspondientes
    subjects = Subject.objects.filter(id__in=subject_ids)

    try:
        dossier = Dossier.objects.get(user=user)
        average_grade = dossier.calculate_average_grade()
        credits_achieved = dossier.credits_achieved()
        credits_remaining = dossier.credits_remaining()
        total_credits = dossier.total_credits()
        subjects_in_dossier = SubjectInDossier.objects.filter(dossier=dossier)
        extra_curricular_credits = dossier.extra_curricular_credits.all()

    except Dossier.DoesNotExist:
        average_grade = 0
        credits_achieved = 0
        total_credits = 0
        credits_remaining = 240
        subjects_in_dossier = []
        extra_curricular_credits = []

    context = {'current_year': current_year, 'user': user, 'posts':posts, 'events_json': events_json, 'user_subjects': subjects, 'subjects_in_dossier': subjects_in_dossier,
               'average_grade': average_grade, 'credits_achieved': credits_achieved, 'credits_remaining': credits_remaining, 'total_credits': total_credits, 'extra_curricular_credits': extra_curricular_credits}
    return render(request, 'Sciences/profile.html', context)


@login_required(login_url='login')
@require_POST
def delete_subject_from_schedule(request, subject_id):
    # Asegúrate de que el usuario esté autenticado y la petición sea POST
    user = request.user
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Intenta eliminar la asignatura del horario del usuario
    try:
        subject_schedule = SubjectSchedule.objects.get(user=user, subject=subject)
        subject_schedule.delete()
        events = Event.objects.filter(user=user, subject=subject)
        events.delete()
        return JsonResponse({'status': 'success', 'message': 'Asignatura eliminada del horario.'})
    except SubjectSchedule.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Asignatura no encontrada en el horario.'}, status=404)
    

@login_required(login_url='login')
def documents(request):
    context = {'current_year': current_year}
    return render(request, 'Sciences/documents.html', context)


@login_required(login_url='login')
def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu contraseña ha sido cambiada.")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    context = {'current_year': current_year, 'form': form}
    return render(request, 'logs/password_reset_confirm.html', context)


def register(request: HttpRequest) -> HttpResponse:
    """
    Handles user registration using a custom user creation form.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        For GET requests: HttpResponse object rendering the 'logs/register.html' template with the registration form.
        For POST requests with successful registration: HttpResponseRedirect object redirecting to the 'main' view.
        For POST requests with errors: HttpResponse object rendering the 'logs/register.html' template with the form and error messages.
    """
    if request.method == 'GET': # GET request
        form = CustomUserCreationForm()
        return render(request, 'logs/register.html', {'form': form})
    
    else: # POST request

        form = CustomUserCreationForm()
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            is_student = form.cleaned_data.get('is_student')
        else:
            messages.error(request, "Está ocurriendo un error con el formulario.")
            is_student = True

        # Check if the username is longer than 35 chars.
        if len(username) > 35:
            return render(request, 'logs/register.html', {'form': form, 'error': 'El nombre de usuario es demasiado largo.'})
        
        # Check if the passwords are equal.
        if password1 == password2:
            
            # Check if the username only has letters.
            if re.match(r'^[a-zA-Z]+$', username):
                
                # Check if the email exists on the database.
                if User.objects.filter(email=email).exists():
                    return render(request, 'logs/register.html', {'current_year': current_year, 'form': form, 'error': 'El email ya está registrado.'})
                
                # Check if the password is longer than 8 chars and no completly numeric
                if len(password1) < 8:
                    return render(request, 'logs/register.html', {'current_year': current_year, 'form': form, 'error': 'La contraseña debe contener al menos 8 caracteres.'})
                elif re.fullmatch(r'\d+', password1):
                    return render(request, 'logs/register.html', {'current_year': current_year, 'form': form, 'error': 'La contraseña no puede ser solamente numérica.'})
                
                # We try to create a user but an IntegrityError could be thrown -> User already exists.
                try:
                    user = User.objects.create_user(username=username, email=email, password=password1)
                    user.is_active=False
                    activateEmail(request, user, email)
                    user.save()
                    Profile.objects.update_or_create(user=user, defaults={'is_student': is_student})
                    return redirect('home')
                except IntegrityError as e:
                    print(e)
                    return render(request, 'logs/register.html', {'current_year': current_year, 'form': form, 'error': 'El usuario ya existe'})
            
            else:
                return render(request, 'logs/register.html', {'current_year': current_year, 'form': form, 'error': 'El nombre de usuario debe contener solo letras'})
        
        return render(request, 'logs/register.html', {'current_year': current_year, 'form': form, 'error': 'Las contraseñas no coinciden'})


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Handles the user login process.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        For GET requests: HttpResponse object rendering the 'logs/login.html' template with the login form.
        For POST requests with failed authentication: HttpResponse object rendering the 'logs/login.html' template with the form and an error message.
        For POST requests with successful authentication: HttpResponseRedirect object redirecting to the 'main' view.
    """
    if request.method == 'GET': # GET request
        return render(request, 'logs/login.html', {'form': AuthenticationForm})
    
    else: # POST request

        user = authenticate(request, username=request.POST['username'],
            password=request.POST['password'])

        if user is None:
            # Authentication failed, return to login page with an error
            return render(request, 'logs/login.html', {'current_year': current_year, 'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrectos'}
            )
        
        else:
            # Authentication successful, log the user in and redirect to the main page
            login(request, user)
            return redirect('main')


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    """
    Logs out the current user and redirects to the home page.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponseRedirect object to the URL mapped to the 'home' view, effectively redirecting the user to the home page after logout.
    """
    logout(request)
    return redirect('home')



def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Gracias por confirmar tu email. Ya puedes iniciar sesión.")
        return redirect('login')
    else:
        messages.error(request, "El link de activación es inválido!")

    return redirect('main')


def activateEmail(request, user, to_email):
    mail_subject = "Activa tu cuenta."
    message = render_to_string("logs/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Estimado <b>{user}</b>, por favor comprueba tu email: <b>{to_email}</b> y haz click \
                         en el link recibido para completar el registro. <b>Nota:</b> Cualquier problema escriba a <b>sciences.paths@gmail.com</b>.')
    else:
        messages.error(request, f'Problema enviando el email a {to_email}, comprueba que el correo es correcto.')


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = User.objects.filter(email=user_email).first()
            if associated_user:
                subject = "Recuperar Contraseña SciencesPath!"
                message = render_to_string("logs/template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                }) 
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                                        """
                                        <h2>Recuperación de Contraseña enviada</h2><hr>
                                        <p>
                                            Te hemos enviado un email con todas las instrucciones. Si existe una cuenta con tu email, deberías recibirlo pronto.<br>
                                            Si no recibes el email, asegúrate de que el email es correcto, comprueba la carpeta de spam o ponte en contacto con <b>sciences.paths@gmail.com</b>.
                                        </p>
                                        """
                                    )
                else:
                    messages.error(request, "Problema encontrado al enviar el email, <b>PROBLEMA EN EL SERVIDOR</b>. \
                                   Inténtalo más tarde o póngase en contacto con <b>sciences.paths@gmail.com</b>.")
            
            return redirect('home')

        for error in list(form.errors.values()):
            messages.error(request, error)

    form = PasswordResetForm()
    context = {'current_year': current_year, 'form': form}
    return render(request=request,
                  template_name="logs/password_reset.html",
                  context=context
                  )


def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Tu contraseña ha sido actualizada. Ya puedes iniciar sesión con la nueva contraseña.")
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        
        form = SetPasswordForm(user)
        context = {'current_year': current_year, 'form': form}
        return render(request, 'logs/password_reset_confirm.html', context=context)
    else:
        messages.error(request, "El link ha expirado.")

    messages.error(request, 'Algo ha ido mal, redirigiendo a la página de inicio.')
    return redirect('home')