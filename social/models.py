from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from subjects.models import Subject


class Address(models.Model):
    street = models.CharField(max_length=255, verbose_name="Calle", blank=True, null=True)
    number = models.PositiveIntegerField(verbose_name="Número", blank=True, null=True)
    floor = models.PositiveIntegerField(blank=True, null=True, verbose_name="Piso")
    door = models.CharField(max_length=10, blank=True, verbose_name="Letra")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    country = CountryField(blank_label='(Seleccionar país)', verbose_name="País")

    def __str__(self):
        address_str = f"{self.street} {self.number}"
        if self.floor and self.door:
            address_str += f", Piso {self.floor}, Puerta {self.door}"
        elif self.floor:
            address_str += f", Piso {self.floor}"
        address_str += f", {self.city}, {self.country.name}"
        return address_str


class Profile(models.Model):
    """Represents a user profile with extended information."""
    UNIVERISITY_CHOICES = [
        ('', 'No especificado'),
        ('UAM', 'Universidad Autónoma de Madrid'),
        ('UC3M', 'Universidad Carlos III de Madrid'),
        ('UAB', 'Universidad Autónoma de Barcelona'),
    ]

    YEAR_CHOICES = [
        ('', 'No especificado'),
        ('1', '1º'),
        ('2', '2º'),
        ('3', '3º'),
        ('4', '4º'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default='Hola, SciencesPath!')
    image = models.ImageField(default='default.png')
    birth_date = models.DateField(null=True, blank=True)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    is_student = models.BooleanField(default=True)
    university = models.CharField(max_length=50, choices=UNIVERISITY_CHOICES, blank=True, null=True, default='')
    year = models.CharField(max_length=2, choices=YEAR_CHOICES, blank=True, null=True, default='')
    university_email = models.EmailField(max_length=254, blank=True, null=True)
    credits_passed = models.PositiveIntegerField(default=0)
    linkedin_url = models.URLField(max_length=255, blank=True, null=True)
    instagram_url = models.URLField(max_length=255, blank=True, null=True)
    twitter_url = models.URLField(max_length=255, blank=True, null=True)

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
    

class Event(models.Model):
    """Model that represents an event in a user's calendar."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="subjects", blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    is_all_day = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f'{self.title} ({self.start_time.strftime("%Y-%m-%d %H:%M")} - {self.end_time.strftime("%Y-%m-%d %H:%M")})'
    

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
    
    def num_likes(self):
        """Returns the number of likes this post has."""
        return self.likes.count()

    def num_comments(self):
        """Returns the number of comments this post has."""
        return self.comments.count()


class Relationship(models.Model):
    """Represents a follow-unfollow relationship between two users."""

    from_user = models.ForeignKey(User, related_name='relationships', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='related_to', on_delete=models.CASCADE)

    def __str__(self) -> str:
        """Returns the relationship's string representation, showing the direction of the relationship."""
        return f'{self.from_user} to {self.to_user}'


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_posts')
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self) -> str:
        return f'{self.user} likes {self.post}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_made')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self) -> str:
        return f'Comment by {self.user} on {self.post}'