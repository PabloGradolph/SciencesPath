from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default='Hola, SciencesPath!')
    image = models.ImageField(default='default.png')

    def __str__(self) -> str:
        return f"Perfil de {self.user.username}"


class Post(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self) -> str:
        return self.content