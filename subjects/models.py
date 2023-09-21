from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from datetime import datetime
import os
from django.conf import settings

class University(models.Model):
    name = models.TextField(max_length=10000)

    def __str__(self) -> str:
        return self.name
    

class Degree(models.Model):
    name = models.TextField(max_length=10000)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Subject(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, null=True)
    name = models.TextField(max_length=10000, null=False)
    subject_key = models.IntegerField(null=False)
    year = models.TextField(null=True, max_length=30)
    semester = models.TextField(null=True, max_length=30)
    credits = models.FloatField(null=True)
    language = models.TextField(max_length=10000, null=True)
    coordinator = models.TextField(max_length=10000, null=True)
    previous_requirements = models.TextField(null=True)
    subject_url = models.URLField(null=True)
    content = models.TextField(null=True)
    reviews = models.ManyToManyField(User, through='SubjectRating')

    def __str__(self) -> str:
        return self.name

    def avg_rating(self) -> float:
        avg = self.subjectrating_set.aggregate(Avg('rating'))['rating__avg']
        if avg is None:
            return 0.0
        
        rounded_avg = round(avg * 2) / 2
        return rounded_avg


class SubjectRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(default='')
    created_at = models.DateTimeField(default=datetime.now())

    class Meta:
        unique_together = ('user', 'subject')


class TimeTable(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    schedule_file_uab = models.FileField(storage=settings.ICAL_STORAGE_UAB, null=True)
    schedule_file_uam = models.FileField(storage=settings.ICAL_STORAGE_UAM, null=True)
    schedule_file_uc3m = models.FileField(storage=settings.ICAL_STORAGE_UC3M, null=True)


class SubjectMaterial(models.Model):
    MATERIAL_TYPES = (
        ('Apuntes', 'Apuntes'),
        ('Ejercicios', 'Ejercicios'),
        ('Examenes', 'Exámenes'),
    )

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='Apuntes')
    file = models.FileField(upload_to='subject_materials/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title