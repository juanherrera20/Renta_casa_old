# Generated by Django 5.0.2 on 2024-04-30 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('generar', '0014_rename_fecha_cobro_arrendatario_fecha_fin_cobro_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inmueble',
            old_name='valor_seguro',
            new_name='porcentaje',
        ),
        migrations.RemoveField(
            model_name='propietario',
            name='tipo_contrato',
        ),
        migrations.RemoveField(
            model_name='propietario',
            name='valor_pago',
        ),
    ]
