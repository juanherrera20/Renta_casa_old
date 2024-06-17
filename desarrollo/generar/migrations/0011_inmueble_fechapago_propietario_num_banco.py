# Generated by Django 5.0.2 on 2024-06-17 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generar', '0010_remove_propietario_habilitarpago_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inmueble',
            name='fechaPago',
            field=models.DateField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='propietario',
            name='num_banco',
            field=models.CharField(default=123456, max_length=200),
            preserve_default=False,
        ),
    ]
