# Generated by Django 5.0.2 on 2024-05-28 07:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generar', '0007_alter_arrendatario_usuarios_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inmueble',
            name='propietario_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inmueble', to='generar.propietario'),
        ),
    ]
