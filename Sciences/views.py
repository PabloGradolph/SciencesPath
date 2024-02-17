from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from datetime import datetime
from .forms import CustomUserCreationForm
from faq.models import FAQ
import re

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


# TODO -> Tienes que completar la vista de profile.
@login_required(login_url='login')
def profile(request, username):
    user = User.objects.get(username=username)
    posts = user.posts.all()
    context = {'current_year': current_year, 'user': user, 'posts':posts}
    return render(request, 'social/profile.html', context)

# TODO -> Tienes que completar la vista de documents.
@login_required(login_url='login')
def documents(request):
    context = {'current_year': current_year}
    return render(request, 'Sciences/documents.html', context)

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
                
                # We try to create a user but an IntegrityError could be thrown -> User already exists.
                try:
                    user = User.objects.create_user(username=username, email=email, password=password1)
                    user.save()
                    login(request, user)
                    return redirect('main')
                except IntegrityError:
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