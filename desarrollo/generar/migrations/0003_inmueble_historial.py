# Generated by Django 5.0.2 on 2024-05-16 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generar', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inmueble',
            name='historial',
            field=models.IntegerField(default=0),
        ),
    ]