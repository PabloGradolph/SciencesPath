# Generated by Django 4.2.2 on 2023-09-09 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0004_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
