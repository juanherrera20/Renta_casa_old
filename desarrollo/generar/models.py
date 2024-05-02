from django.db import models
from django.db.models.fields import CharField, IntegerField


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
    #estrato = models.IntegerField() #opcional, uso del inmueble (vivienda unifamiliar, multifamiliar, local comercial)
    #quizas falta el aumento de del canon de arrendamiento
    
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
        
class documentos(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True)
    propiedad_id = models.ForeignKey('inmueble', on_delete=models.PROTECT)
    pdf = models.FileField(upload_to="pdf/") #Crea una carpeta para guardar los pdf's y tener mejor accebilidad
    imagen = models.ImageField(upload_to="images/")
    descuento = models.IntegerField() #Descuento que se descuenta al propietario
    class Meta:
        db_table = 'documentos'

#Revisar el tema de documentos e imagenes - con columnas independientes o relacionado.