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
    habilitar = models.IntegerField() #Saber si un usuario está habilitado o no (declarar super usuario)
    urls = []
    
    class Meta:
        db_table = 'superuser' #Se le agrega el nombre que tendrá la tabla

class usuarios(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length = 100)
    documento = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 100)
    telefono = models.CharField(max_length = 50)
    propie_client = models.IntegerField() 
    
    class Meta:
        db_table = 'usuarios' 

class arrendatario(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True)
    usuarios_id = models.ForeignKey('usuarios', on_delete=models.PROTECT) #Declaracion de FK
    propiedad_id = models.ForeignKey('propiedad', on_delete=models.PROTECT)
    direccion = models.CharField(max_length = 200)
    valor_cobro = models.IntegerField()
    fecha_cobro = models.DateField(max_length = 20)
    inicio_contrato = models.DateField(max_length = 20)
    fin_contrato = models.DateField(max_length = 20)
    tipo_contrato = models.CharField(max_length = 100) 
    obs = models.CharField(max_length = 400) 
    
    class Meta:
        db_table = 'arrendatario'
    
class propietario(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True)
    usuarios_id = models.ForeignKey('usuarios', on_delete=models.PROTECT) #Declaracion de FK
    propiedad_id = models.ForeignKey('propiedad', on_delete=models.PROTECT)
    direccion = models.CharField(max_length = 200)
    valor_pago = models.IntegerField()
    fecha_pago = models.DateField(max_length = 20)
    tipo_contrato = models.CharField(max_length = 100) 
    obs = models.CharField(max_length = 400) 
    urls = []
    
    class Meta:
        db_table = 'propietario'
        
class propiedad(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True)
    propietario_id = models.ForeignKey('propietario', on_delete=models.PROTECT)
    arrendatario_id = models.ForeignKey('arrendatario', on_delete=models.PROTECT)
    documento_id = models.ForeignKey('documentos', on_delete=models.PROTECT)
    ref = models.CharField(max_length = 10) #referencia unica que se pueda mostrar al usuario
    tipo = models.IntegerField() #Si es casa, edificio, local...
    valor_seguro = models.IntegerField()
    descripcion = models.CharField(max_length = 400) 
    habilitada = models.CharField(max_length = 3) #Saber si esta ocupada o no.
    
    class Meta:
        db_table = 'propiedad'
        
class documentos(models.Model): #Tabla usuarios
    id = models.AutoField(primary_key=True, unique=True)
    propiedad_id = models.ForeignKey('propiedad', on_delete=models.PROTECT)
    pdf = models.FileField(upload_to="pdf/") #Crea una carpeta para guardar los pdf's y tener mejor accebilidad
    descuento = models.IntegerField() #Descuento que se descuenta al propietario
    urls = []
    
    class Meta:
        db_table = 'documentos'