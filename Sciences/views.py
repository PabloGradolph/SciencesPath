from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.core.serializers import serialize
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.mail import EmailMessage
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages

from .tokens import account_activation_token
from .forms import CustomUserCreationForm, SetPasswordForm, CustomAuthenticationForm
from faq.models import FAQ
from subjects.models import Subject, SubjectSchedule, Dossier, SubjectInDossier
from social.models import Event, Profile

from datetime import datetime
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
def profile(request: HttpRequest, username: str) -> HttpResponse:
    """
    Displays the profile page of a user, including their posts, scheduled events, and academic information.
    
    The view retrieves and processes the user's posts, events, and subject schedules for display. 
    It also calculates academic details like average grade and credits achieved if a dossier exists.
    
    Args:
        request: HttpRequest object.
        username: Username of the user to display the profile for.
    
    Returns:
        HttpResponse object rendering the 'Sciences/profile.html' template with the context containing user data and academic information.
    """
    # User and related entities retrieval
    user = User.objects.get(username=username)
    posts = user.posts.all()
    events = user.events.all()
    user_subjects = user.subject_schedules.all()
    subjects_colors = {subject.subject_id: subject.color for subject in user_subjects}

    # Event processing
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

        # Removing unused fields
        del event['fields']['user']
        del event['fields']['start_time']
        del event['fields']['end_time']
        del event['fields']['is_all_day']

    events_json = json.dumps([event['fields'] for event in events_json])

    # Subject information retrieval
    subject_ids = user.subject_schedules.values_list('subject_id', flat=True)
    subjects = Subject.objects.filter(id__in=subject_ids)

    # Dossier information retrieval and processing
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
def delete_subject_from_schedule(request: HttpRequest, subject_id: int) -> JsonResponse:
    """
    Deletes a subject from the user's schedule and associated events, responding with a JSON status message.

    Args:
        request: The HttpRequest object.
        subject_id: The ID of the subject to be deleted.

    Returns:
        JsonResponse object containing the status ('success' or 'error') and a message about the action's result.
    """
    user = request.user
    subject = get_object_or_404(Subject, id=subject_id)
    
    try:
        subject_schedule = SubjectSchedule.objects.get(user=user, subject=subject)
        subject_schedule.delete()
        events = Event.objects.filter(user=user, subject=subject)
        events.delete()
        return JsonResponse({'status': 'success', 'message': 'Asignatura eliminada del horario.'})
    except SubjectSchedule.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Asignatura no encontrada en el horario.'}, status=404)
    

@login_required(login_url='login')
def documents(request: HttpRequest) -> HttpResponse:
    """
    Renders the documents page for the Sciences section of the site.

    Args:
        request: The HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse object rendering the 'Sciences/documents.html' template.
    """
    context = {'current_year': current_year}
    return render(request, 'Sciences/documents.html', context)


@login_required(login_url='login')
def password_change(request: HttpRequest) -> HttpResponse:
    """
    Allows the user to change their password.

    This view displays a form for password change on GET requests and processes the form on POST requests.

    Args:
        request: HttpRequest object containing metadata about the request.

    Returns:
        HttpResponse object either rendering the password change form or redirecting to the login page upon successful password change.
    """
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
                
                # Check if the password is longer than 8 chars and no completly numeric.
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
        return render(request, 'logs/login.html', {'form': CustomAuthenticationForm})
    
    else: # POST request

        username_or_email = request.POST['username_or_email']
        password = request.POST['password2']

        # Check if the input contains "@" symbol to determine if it's an email
        if "@" in username_or_email:
            # If it's an email, try to authenticate using email
            user = User.objects.get(email=username_or_email)
            username = user.username
            user = authenticate(request, username=username, password=password)
        else:
            # Otherwise, try to authenticate using username
            user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            # Authentication failed, return to login page with an error
            return render(request, 'logs/login.html', {'current_year': current_year, 'form': CustomAuthenticationForm,
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


# --------------------- COMPLEMENTARY FUNCTIONS ---------------------

def activate(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """
    Activates a user's account if the provided token is valid.

    This view attempts to decode the user's ID from `uidb64`, retrieve the user model, and then checks the
    provided token.

    Args:
        request: HttpRequest object containing metadata about the request.
        uidb64: URL-safe base64-encoded string representing the user's ID.
        token: Account activation token to be verified.

    Returns:
        HttpResponse object redirecting to either the login page upon successful activation or the main page if activation fails.
    """
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


def activateEmail(request: HttpRequest, user: User, to_email: str) -> None:
    """
    Sends email to `to_email` with an activation link.

    Args:
        request (HttpRequest): The request object.
        user (User): User instance to activate.
        to_email (str): Email address to send the activation link.
    """
    # Email content setup
    mail_subject = "Activa tu cuenta."
    message = render_to_string("logs/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })

    # Attempt to send email
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Estimado <b>{user}</b>, por favor comprueba tu email: <b>{to_email}</b> y haz click \
                         en el link recibido para completar el registro. <b>Nota:</b> Cualquier problema escriba a <b>sciences.paths@gmail.com</b>.')
    else:
        messages.error(request, f'Problema enviando el email a {to_email}, comprueba que el correo es correcto.')


def password_reset_request(request: HttpRequest) -> HttpResponse:
    """
    Handles the password reset request by sending an email with reset instructions.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Renders the password reset request form or redirects to home on successful email dispatch.
    """
    if request.method == 'POST':

        form = PasswordResetForm(request.POST)

        if form.is_valid():
            # Extract the email from the form and look for the associated user
            user_email = form.cleaned_data['email']
            associated_user = User.objects.filter(email=user_email).first()

            if associated_user:
                # Prepare and send the password recovery email
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
                    # Success message if the email is successfully sent
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

        # Adds form errors to error messages
        for error in list(form.errors.values()):
            messages.error(request, error)

    # If not POST, display the password recovery form
    form = PasswordResetForm()
    context = {'current_year': current_year, 'form': form}
    return render(request,"logs/password_reset.html",context)


def passwordResetConfirm(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """
    Handles the password reset confirmation process.

    Validates the user's token and uidb64 from the password reset email, allowing them to set a new password if valid.
    
    Args:
        request (HttpRequest): The request object containing metadata about the request.
        uidb64 (str): The user's ID encoded in base64.
        token (str): Token for validating the password reset request.

    Returns:
        HttpResponse: Renders the password reset form or redirects to the login page upon successful password update.
    """
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64)) # Decode the user's ID from base64.
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # Process the form if the token is valid.
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
        # Invalid link or expired token.
        messages.error(request, "El link ha expirado.")

    # Fallback message in case something else goes wrong.
    messages.error(request, 'Algo ha ido mal, redirigiendo a la página de inicio.')
    return redirect('home')