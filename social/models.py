from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Represents a user profile with extended information."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default='Hola, SciencesPath!')
    image = models.ImageField(default='default.png')

    def __str__(self) -> str:
        """Returns the profile's string representation, showing the username."""
        return f"Perfil de {self.user.username}"
    
    def following(self) -> models.QuerySet:
        """Returns a QuerySet of users that this user is following."""
        user_ids = Relationship.objects.filter(from_user=self.user).values_list('to_user_id', flat=True)
        return User.objects.filter(id__in=user_ids)
    
    def followers(self) -> models.QuerySet:
        """Returns a QuerySet of users that follow this user."""
        user_ids = Relationship.objects.filter(to_user=self.user).values_list('from_user_id', flat=True)
        return User.objects.filter(id__in=user_ids)


# A profile is generated automatically, when a user is registered.
@receiver(post_save, sender=User)
def create_user_profile(sender: type, instance: User, created: bool, **kwargs) -> None:
    """Creates a Profile instance for every new User instance created."""
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


class Post(models.Model):
    """Represents a post made by a user."""

    timestamp = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self) -> str:
        """Returns the post's content as its string representation."""
        return self.content


class Relationship(models.Model):
    """Represents a follow-unfollow relationship between two users."""

    from_user = models.ForeignKey(User, related_name='relationships', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='related_to', on_delete=models.CASCADE)

    def __str__(self) -> str:
        """Returns the relationship's string representation, showing the direction of the relationship."""
        return f'{self.from_user} to {self.to_user}'