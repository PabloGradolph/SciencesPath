from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Subject
from django.db.models import Q
from datetime import datetime

current_year = datetime.now().year

@login_required(login_url='login')
def index(request):
    search_query = request.GET.get('search', '').strip()
    subjects = Subject.objects.filter(
        Q(name__icontains=search_query) | Q(university__name__icontains=search_query)
        | Q(degree__name__icontains=search_query)
    )
    context = {'subjects': subjects, 'current_year': current_year}
    return render(request, 'subjects/index.html', context)


@login_required(login_url='login')
def detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    context = {'subject': subject, 'current_year': current_year}
    return render(request, 'subjects/detail.html', context)