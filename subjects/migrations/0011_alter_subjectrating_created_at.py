# Generated by Django 4.2.2 on 2024-03-14 10:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0010_alter_subjectrating_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectrating',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 14, 11, 45, 56, 506280)),
        ),
    ]
