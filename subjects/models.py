from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from datetime import datetime
from .storages import UABStorage, UAMStorage, UC3MStorage
from django.conf import settings


class University(models.Model):
    """
    A model representing a university.
    
    Attributes:
        name (str): The name of the university.
    """
    name = models.TextField(max_length=10000)

    def __str__(self) -> str:
        """
        Returns a string representation of the university.
        """
        return self.name
    

class Degree(models.Model):
    """
    A model representing an educational degree.
    
    Attributes:
        name (str): The name of the degree.
        university (University): The university offering the degree (foreign key reference).
    """
    name = models.TextField(max_length=10000)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """
        Returns a string representation of the degree.
        """
        return self.name


class Subject(models.Model):
    """
    A model representing a subject offered by a university.

    Attributes:
        university (University): The university offering the subject (foreign key reference).
        degree (Degree): The degree associated with the subject (foreign key reference).
        name (str): The name of the subject.
        subject_key (int): Unique identifier for the subject.
        year (str): The academic year the subject belongs to (e.g., '2023-2024').
        semester (str): The semester the subject belongs to (e.g., 'Spring').
        credits (float): The credit value of the subject.
        language (str): The language in which the subject is taught.
        coordinator (str): The coordinator of the subject.
        previous_requirements (str): Previous requirements for taking the subject.
        subject_url (str): URL to access additional information about the subject.
        content (str): Description or content of the subject.
        reviews (ManyToManyField): Users who have reviewed the subject (through SubjectRating).

    Methods:
        __str__(): Returns a string representation of the subject.
        avg_rating(): Calculates the average rating of the subject based on user reviews.

    Meta:
        ordering: Default ordering of subjects by degree.
    """
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
        """
        Returns a string representation of the subject.
        """
        return self.name

    def avg_rating(self) -> float:
        """
        Calculates the average rating of the subject based on user reviews.

        Returns:
            float: The average rating rounded to the nearest 0.5.
        """
        avg = self.subjectrating_set.aggregate(Avg('rating'))['rating__avg']
        if avg is None:
            return 0.0
        
        rounded_avg = round(avg * 2) / 2
        return rounded_avg
    
    class Meta:
        """
        Metadata for the Subject model.
        """
        ordering = ['degree']


class SubjectRating(models.Model):
    """
    A model representing a user's rating and review for a subject.

    Attributes:
        user (User): The user who rated the subject (foreign key reference).
        subject (Subject): The subject being rated (foreign key reference).
        rating (int): The rating given by the user (choices: 1-5).
        comment (str): Optional comment or review by the user.
        created_at (datetime): The timestamp when the rating was created.

    Meta:
        unique_together: Ensure each user can rate a subject only once.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(default='')
    created_at = models.DateTimeField(default=datetime.now())

    class Meta:
        """
        Metadata for the SubjectRating model.
        """
        unique_together = ('user', 'subject')


class TimeTable(models.Model):
    """
    Model representing a timetable file for a subject at different universities.

    Attributes:
        subject (Subject): The subject associated with the timetable.
        schedule_file_uab (FileField): The timetable file for UAB university.
        schedule_file_uam (FileField): The timetable file for UAM university.
        schedule_file_uc3m (FileField): The timetable file for UC3M university.
    """
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # schedule_file_uab = models.FileField(storage=UABStorage(), null=True)
    # schedule_file_uam = models.FileField(storage=UAMStorage(), null=True)
    # schedule_file_uc3m = models.FileField(storage=UC3MStorage(), null=True)
    # For local development:
    schedule_file_uab = models.FileField(storage=settings.ICAL_STORAGE_UAB, null=True)
    schedule_file_uam = models.FileField(storage=settings.ICAL_STORAGE_UAM, null=True)
    schedule_file_uc3m = models.FileField(storage=settings.ICAL_STORAGE_UC3M, null=True)


class SubjectMaterial(models.Model):
    """
    Model representing study materials related to a subject.

    Attributes:
        user (User): The user who uploaded the material.
        subject (Subject): The subject to which the material belongs.
        title (str): The title of the material.
        material_type (str): The type of material (e.g., Apuntes, Ejercicios/Prácticas, Examenes).
        file (FileField): The file containing the material.
        upload_date (datetime): The date and time when the material was uploaded.
    """
    MATERIAL_TYPES = (
        ('Apuntes', 'Apuntes'),
        ('Ejercicios/Prácticas', 'Ejercicios/Prácticas'),
        ('Examenes', 'Exámenes'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='materials')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='Apuntes')
    file = models.FileField(upload_to='subject_materials/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the material.
        """
        return self.title


class SubjectSchedule(models.Model):
    """
    Model representing a user's schedule for a subject.

    Attributes:
        user (User): The user to whom the schedule belongs.
        subject (Subject): The subject for which the schedule is created.
        color (str): The color code (in hex) used to display the subject's schedule in the calendar.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, default='#3788D8')  # Hex color for display in the calendar

    class Meta:
        """
        Metadata for the SubjectSchedule model.
        """
        unique_together = ('user', 'subject')

    def __str__(self) -> str:
        """
        Returns a string representation of the user's schedule.
        """
        return f'{self.user.username} - {self.subject.name}'
    

class Dossier(models.Model):
    """
    Model representing a user's academic dossier.

    Attributes:
        user (User): The user to whom the dossier belongs.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dossier')

    def calculate_average_grade(self) -> float:
        """
        Calculate the average grade based on the grades obtained in subjects.

        Returns:
            float: The calculated average grade.
        """
        subjects_in_dossier = self.subjectindossier_set.exclude(grade__isnull=True)
        total_weighted_grades = sum(item.grade * int(item.subject.credits) for item in subjects_in_dossier)
        total_credits = int(sum(item.subject.credits for item in subjects_in_dossier))
        average_grade = total_weighted_grades / total_credits if total_credits > 0 else 0
        return round(average_grade, 2)

    def calculate_extra_curricular_credits(self) -> int:
        """
        Calculate the total extra-curricular credits.

        Returns:
            int: The total extra-curricular credits.
        """
        return int(sum(extra_credits.credits for extra_credits in self.extra_curricular_credits.all()))
    
    def credits_achieved(self) -> int:
        """
        Calculate the total credits achieved, including extra-curricular credits.

        Returns:
            int: The total credits achieved.
        """
        return int(sum(item.subject.credits for item in self.subjectindossier_set.filter(grade__gte=5)) + self.calculate_extra_curricular_credits())
    
    def credits_remaining(self) -> int:
        """
        Calculate the remaining credits needed to complete the degree.

        Returns:
            int: The remaining credits.
        """
        total_credits_achieved = sum(item.subject.credits for item in self.subjectindossier_set.filter(grade__gte=5))
        return int(240 - total_credits_achieved - self.calculate_extra_curricular_credits())
    
    def total_credits(self) -> int:
        """
        Calculate the total credits, including both academic and extra-curricular credits.

        Returns:
            int: The total credits.
        """
        total_credits = sum(item.subject.credits for item in self.subjectindossier_set.all())
        return int(total_credits + self.calculate_extra_curricular_credits())
    

class SubjectInDossier(models.Model):
    """
    Model representing a subject within a user's academic dossier.

    Attributes:
        dossier (Dossier): The dossier to which the subject belongs.
        subject (Subject): The subject associated with the entry.
        grade (Decimal): The grade obtained in the subject.
    """
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    def __str__(self) -> str:
        """
        Return a string representation of the subject within the dossier.
        """
        return f'{self.subject} - Grade: {self.grade}'


class ExtraCurricularCredits(models.Model):
    """
    Model representing extra-curricular credits within a user's academic dossier.

    Attributes:
        dossier (Dossier): The dossier to which the extra-curricular credits belong.
        name (str): The name or description of the extra-curricular activity.
        credits (float): The number of extra-curricular credits earned.
    """
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='extra_curricular_credits')
    name = models.CharField(max_length=255)
    credits = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self) -> str:
        """
        Return a string representation of the extra-curricular credits entry.
        """
        return f"{self.name} - {self.credits} créditos"