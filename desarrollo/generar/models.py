from django.db import models
from django.db.models.fields import CharField, IntegerField
import os

#------------------Función para guardar los archivos e imagenes en carpetas separadas y personalizadas----------------------------s
def carpetas_inmuebles(instance, filename):
    # Obtener el nombre de la carpeta basado en el ID del inmueble
    folder_name = str(instance.inmueble.id) + "_" + str(instance.inmueble.direccion)
    # Crear la ruta completa hacia la carpeta
    folder_direct = os.path.join('media', folder_name)
    
    if not os.path.exists(folder_direct):# Verificar si la carpeta existe, si no, crearla
        os.makedirs(folder_direct)
    return os.path.join(folder_name, filename)# Concatenar la ruta de la carpeta con el nombre de archivo original
#---------------------------------------------------------------------------------------------------------------------------------s
#Si molesta esta función aquí puede ser pertinente crear un archivo donde metamos todas las funciones


# Creations the models.
class superuser(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length = 100)
    documento = models.CharField(max_length = 50, unique = True)
    password = models.CharField(max_length = 250)
    telefono = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 100)
    habilitar = models.IntegerField(default=1) #Saber si un usuario está habilitado o no (declarar super usuario)
    
    class Meta:
        db_table = 'superuser' #Se le agrega el nombre que tendrá la tabla

class usuarios(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length = 100)
    tipo_documento = models.CharField(max_length = 100)
    documento = models.CharField(max_length = 50)
    expedida = models.CharField(max_length =100)
    email = models.EmailField(max_length = 100)
    email2 = models.EmailField(max_length = 100)
    email3 = models.EmailField(max_length = 100)
    telefono = models.CharField(max_length = 50)
    telefono2 = models.CharField(max_length = 50)
    telefono3 = models.CharField(max_length = 50)
    habilitar = models.IntegerField(default=1)
    propie_client = models.IntegerField() 
    
    class Meta:
        db_table = 'usuarios' 

class arrendatario(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True)
    usuarios_id = models.ForeignKey('usuarios', on_delete=models.PROTECT) #Declaracion de FK
    propiedad_id = models.ForeignKey('inmueble', on_delete=models.PROTECT)
    direccion = models.CharField(max_length = 200)
    valor_cobro = models.IntegerField()
    fecha_inicio_cobro = models.DateField(max_length = 20)
    fecha_fin_cobro = models.DateField(max_length = 20)
    inicio_contrato = models.DateField(max_length = 20)
    fin_contrato = models.DateField(max_length = 20)
    tipo_contrato = models.CharField(max_length = 100) #Se puede hacer la alarma mediante este campo.
    habilitarPago = models.IntegerField(default=2) 
    obs = models.CharField(max_length = 400) 
    
    class Meta:
        db_table = 'arrendatario'
    
class propietario(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True)
    usuarios_id = models.ForeignKey('usuarios', on_delete=models.PROTECT) #Declaracion de FK
    propiedad_id = models.ForeignKey('inmueble', on_delete=models.PROTECT)
    direccion = models.CharField(max_length = 200)
    fecha_pago = models.DateField(max_length = 20)
    habilitarPago = models.IntegerField(default=2)
    bancos = models.CharField(max_length = 200)
    obs = models.CharField(max_length = 400)
    
    class Meta:
        db_table = 'propietario'
        
class inmueble(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True) 
    propietario_id = models.ForeignKey('propietario', on_delete=models.PROTECT) 
    arrendatario_id = models.ForeignKey('arrendatario', on_delete=models.PROTECT)
    ref = models.CharField(max_length = 10) #referencia unica que se pueda mostrar al usuario   
    tipo = models.IntegerField() #Si es casa, edificio, local...   
    canon = models.IntegerField() 
    porcentaje = models.IntegerField() 
    servicios = models.CharField(max_length =200)
    direccion = models.CharField(max_length =300) 
    descripcion = models.CharField(max_length = 400) 
    habilitada = models.CharField(max_length = 3) #Saber si esta ocupada o no. 
    descuento = models.IntegerField() #Descuento que se descuenta al propietario
    #estrato = models.IntegerField() #opcional, uso del inmueble (vivienda unifamiliar, multifamiliar, local comercial)
    
    
    class Meta:
        db_table = 'inmueble'

#Datos ficticio...Investigar como se puede implementar con API Calendar o tipo de arrastre que cambie de estado con notificiación...
class tareas(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    superuser_id = models.ForeignKey('superuser', on_delete=models.PROTECT)
    titulo = models.CharField(max_length=300)
    descrip = models.CharField(max_length = 400)
    estado = models.CharField(max_length = 100) #Saber si esta en pendiente, completada o incompleta
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField(max_length = 20)
    etiqueta = models.CharField(max_length = 100)
    hora_inicio = models.TimeField()

    class Meta:
        db_table = 'tareas'

class Imagenes(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    inmueble = models.ForeignKey(inmueble, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to=carpetas_inmuebles)
    class Meta:
        db_table = 'Imagenes'
    
class Documentos(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    inmueble = models.ForeignKey(inmueble, related_name='documentos', on_delete=models.CASCADE)
    documento = models.FileField(upload_to=carpetas_inmuebles)
    class Meta:
        db_table = 'Documentos'

#Revisar el tema de documentos e imagenes - con columnas independientes o relacionado.