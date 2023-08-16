from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from datetime import datetime

current_year = datetime.now().year

@login_required(login_url='login')
def home(request):
    return render(request, 'Sciences/home.html', {'current_year': current_year})

@login_required(login_url='login')
def about(request):
    return render(request, 'Sciences/about.html', {'current_year': current_year})


def register(request):
    if request.method == 'GET':
        return render(request, 'logs/register.html', {'form': UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                return render(request, 'logs/register.html', {'form': UserCreationForm, 
                    'error': 'El usuario ya existe'})
        return render(request, 'logs/register.html', {'form': UserCreationForm, 
                    'error': 'Las contraseñas no coinciden'})


def login_view(request):
    if request.method == 'GET':
        return render(request, 'logs/login.html', {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'],
            password=request.POST['password']
        )
        if user is None:
            return render(request, 'logs/login.html', {'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrectos'}
            )
        else:
            login(request, user)
            return redirect('home')


def logout_view(request):
    logout(request)
    return redirect('home')