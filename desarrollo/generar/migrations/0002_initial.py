# Generated by Django 5.0.2 on 2024-05-16 19:26

import django.db.models.deletion
import generar.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('generar', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='arrendatario',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('direccion', models.CharField(max_length=200)),
                ('fecha_inicio_cobro', models.DateField(max_length=20)),
                ('fecha_fin_cobro', models.DateField(max_length=20)),
                ('inicio_contrato', models.DateField(max_length=20)),
                ('fin_contrato', models.DateField(max_length=20)),
                ('tipo_contrato', models.CharField(max_length=100)),
                ('habilitarPago', models.IntegerField(default=2)),
                ('obs', models.CharField(max_length=400)),
            ],
            options={
                'db_table': 'arrendatario',
            },
        ),
        migrations.CreateModel(
            name='propietario',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('direccion', models.CharField(max_length=200)),
                ('fecha_pago', models.DateField(max_length=20)),
                ('habilitarPago', models.IntegerField(default=2)),
                ('bancos', models.CharField(max_length=200)),
                ('obs', models.CharField(max_length=400)),
            ],
            options={
                'db_table': 'propietario',
            },
        ),
        migrations.CreateModel(
            name='superuser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=100)),
                ('documento', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=250)),
                ('telefono', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=100)),
                ('habilitar', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'superuser',
            },
        ),
        migrations.CreateModel(
            name='usuarios',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=100)),
                ('tipo_documento', models.CharField(max_length=100)),
                ('documento', models.CharField(max_length=50)),
                ('expedida', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('email2', models.EmailField(max_length=100)),
                ('email3', models.EmailField(max_length=100)),
                ('telefono', models.CharField(max_length=50)),
                ('telefono2', models.CharField(max_length=50)),
                ('telefono3', models.CharField(max_length=50)),
                ('habilitar', models.IntegerField(default=1)),
                ('propie_client', models.IntegerField()),
            ],
            options={
                'db_table': 'usuarios',
            },
        ),
        migrations.CreateModel(
            name='inmueble',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('ref', models.CharField(max_length=10)),
                ('tipo', models.IntegerField()),
                ('canon', models.IntegerField()),
                ('porcentaje', models.IntegerField()),
                ('servicios', models.CharField(max_length=200)),
                ('direccion', models.CharField(max_length=300)),
                ('descripcion', models.CharField(max_length=400)),
                ('habilitada', models.CharField(max_length=3)),
                ('arrendatario_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='generar.arrendatario')),
                ('propietario_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='generar.propietario')),
            ],
            options={
                'db_table': 'inmueble',
            },
        ),
        migrations.CreateModel(
            name='Imagenes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('imagen', models.ImageField(upload_to=generar.models.Crear_carpetas)),
                ('inmueble', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='generar.inmueble')),
            ],
            options={
                'db_table': 'Imagenes',
            },
        ),
        migrations.CreateModel(
            name='Documentos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('documento', models.FileField(upload_to=generar.models.Crear_carpetas)),
                ('inmueble', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='generar.inmueble')),
            ],
            options={
                'db_table': 'Documentos',
            },
        ),
        migrations.CreateModel(
            name='Docdescuentos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('valor', models.IntegerField()),
                ('descrip', models.CharField(max_length=400)),
                ('documento', models.CharField(max_length=600)),
                ('inmueble', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Docdescuento', to='generar.inmueble')),
            ],
            options={
                'db_table': 'Docdescuentos',
            },
        ),
        migrations.CreateModel(
            name='DocsPersonas',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('documento', models.FileField(upload_to=generar.models.Crear_carpetas)),
                ('arrendatario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='DocsPersona', to='generar.arrendatario')),
                ('propietario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='DocsPersona', to='generar.propietario')),
            ],
            options={
                'db_table': 'DocsPersonas',
            },
        ),
        migrations.CreateModel(
            name='tareas',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('titulo', models.CharField(max_length=300)),
                ('descrip', models.CharField(max_length=400)),
                ('estado', models.CharField(max_length=100)),
                ('fecha_inicio', models.DateField(auto_now_add=True)),
                ('fecha_fin', models.DateField(max_length=20)),
                ('etiqueta', models.CharField(max_length=100)),
                ('hora_inicio', models.TimeField()),
                ('superuser_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='generar.superuser')),
            ],
            options={
                'db_table': 'tareas',
            },
        ),
        migrations.AddField(
            model_name='propietario',
            name='usuarios_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='generar.usuarios'),
        ),
        migrations.AddField(
            model_name='arrendatario',
            name='usuarios_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='generar.usuarios'),
        ),
    ]
