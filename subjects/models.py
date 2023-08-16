from django.db import models


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

    def __str__(self) -> str:
        return self.name
