# Generated by Django 4.2.2 on 2024-03-12 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0010_alter_subjectrating_created_at'),
        ('social', '0011_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='subjects.subject'),
        ),
    ]
