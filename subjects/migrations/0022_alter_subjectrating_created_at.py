# Generated by Django 4.2.2 on 2024-03-28 10:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0021_alter_subjectmaterial_material_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectrating',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 28, 11, 12, 52, 400235)),
        ),
    ]
