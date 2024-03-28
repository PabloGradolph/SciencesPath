# Generated by Django 4.2.2 on 2024-03-28 09:27

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subjects', '0018_alter_subjectrating_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectmaterial',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='materials', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='subjectrating',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 28, 10, 27, 43, 805575)),
        ),
    ]