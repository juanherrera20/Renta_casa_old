# Generated by Django 5.0.3 on 2024-04-17 20:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generar', '0010_arrendatario_habilitarpago'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentos',
            name='imagen',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='images/'),
            preserve_default=False,
        ),
    ]
