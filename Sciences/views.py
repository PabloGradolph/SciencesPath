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

current_year = datetime.now().year

def home(request):
    return render(request, 'Sciences/home.html', {'current_year': current_year})

@login_required(login_url='login')
def main(request):
    faqs = FAQ.objects.all()
    context = {'current_year': current_year, 'faqs': faqs}
    return render(request, 'Sciences/main.html', context)

@login_required(login_url='login')
def profile(request, username):
    user = User.objects.get(username=username)
    posts = user.posts.all()
    context = {'current_year': current_year, 'user': user, 'posts':posts}
    return render(request, 'Sciences/profile.html', context)

def register(request):
    if request.method == 'GET':
        form = CustomUserCreationForm()
        return render(request, 'logs/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        if request.POST['password1'] == request.POST['password2']:
            username = request.POST['username']
            if re.match(r'^[a-zA-Z]+$', username):
                try:
                    user = User.objects.create_user(username=username, email=request.POST['email'], password=request.POST['password1'])
                    user.save()
                    login(request, user)
                    return redirect('main')
                except IntegrityError:
                    return render(request, 'logs/register.html', {'current_year': current_year, 'form': form, 'error': 'El usuario ya existe'})
            else:
                return render(request, 'logs/register.html', {'current_year': current_year, 'form': form, 'error': 'El nombre de usuario debe contener solo letras'})
        return render(request, 'logs/register.html', {'current_year': current_year, 'form': form, 'error': 'Las contraseñas no coinciden'})


def login_view(request):
    if request.method == 'GET':
        return render(request, 'logs/login.html', {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'],
            password=request.POST['password']
        )
        if user is None:
            return render(request, 'logs/login.html', {'current_year': current_year, 'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrectos'}
            )
        else:
            login(request, user)
            return redirect('main')


def logout_view(request):
    logout(request)
    return redirect('home')