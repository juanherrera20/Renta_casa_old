from django.db import models
from django.db.models.fields import CharField, IntegerField
import os

#------------------Función para guardar los documentos e imagenes en carpetas separadas y personalizadas----------------------------s
def Crear_carpetas(instance, filename): #Inmuebles
    if hasattr(instance, 'inmueble'):
        folder_name = str(instance.inmueble.direccion)
        subfolder = "Inmuebles"
        if hasattr(instance, 'imagen'):
            tipo = "Imagenes"
        else:
            tipo = "Documentos"
    elif hasattr(instance, 'propietario'): #hasattr sirve para verificar si un objeto tiene cierto atributo
        folder_name = str(instance.propietario.usuarios_id.documento)
        subfolder = "Propietarios"
        tipo = ""
    elif hasattr(instance, 'arrendatario'):
        folder_name = str(instance.arrendatario.usuarios_id.documento)
        subfolder = "Arrendatarios"
        tipo = ""

    folder_direct = os.path.join('media', subfolder, folder_name, tipo)
    if not os.path.exists(folder_direct):
        os.makedirs(folder_direct)
    return os.path.join(subfolder, folder_name, tipo, filename)
 
    
# def Crear_carpetas_propi(instance, filename): #Inmueble
#         folder_name = str(instance.propietario.usuarios_id.documento) # Obtener el nombre de la carpeta basado en el documento del propietario
       
#         folder_direct = os.path.join('media', "Propietarios", folder_name)
        
#         if not os.path.exists(folder_direct): 
#             os.makedirs(folder_direct)
#         return os.path.join("Propietarios",folder_name, filename)
#---------------------------------------------------------------------------------------------------------------------------------s
#Si molesta tenerla aquí, se puede contemplar el crear un archivo solo para funciones

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
    direccion = models.CharField(max_length = 200)
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
    arrendatario_id = models.ForeignKey('arrendatario', related_name='inmueble', on_delete=models.PROTECT)
    ref = models.CharField(max_length = 10) #referencia unica que se pueda mostrar al usuario   
    tipo = models.IntegerField() #Si es casa, edificio, local...   
    canon = models.IntegerField() 
    porcentaje = models.IntegerField() 
    servicios = models.CharField(max_length =200)
    direccion = models.CharField(max_length =300) 
    descripcion = models.CharField(max_length = 400) 
    habilitada = models.CharField(max_length = 3) #Saber si esta ocupada o no. 
    historial = models.IntegerField(default=0)
   
    # descuento = models.IntegerField() #Descuento que se descuenta al propietario por comisión 
    
    def save(self, *args, **kwargs): #pk igual a id
        if self.pk: #Verificó si es actualización o creación de una instacia
            original = inmueble.objects.get(pk=self.pk)# Obtener la instancia original del inmueble
            if hasattr(original, 'arrendatario_id'):
                if hasattr(self, 'arrendatario_id') and original.arrendatario_id != self.arrendatario_id:
                    self.historial += 1
            else:
                if hasattr(self, 'arrendatario_id'):
                    self.historial += 1
                
        else:
            if hasattr(self, 'arrendatario_id'):# Si es una nueva instancia y el arrendatario_id no es nulo, incrementar el historial
                self.historial += 1
        
        super().save(*args, **kwargs) # Llamar al método save de la superclase para guardar todo lo demas que se solicita en la vista
        
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
    imagen = models.ImageField(upload_to=Crear_carpetas)
    class Meta:
        db_table = 'Imagenes'
    
class Documentos(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    inmueble = models.ForeignKey(inmueble, related_name='documentos', on_delete=models.CASCADE)
    documento = models.FileField(upload_to=Crear_carpetas)
    class Meta:
        db_table = 'Documentos'
        
class DocsPersonas(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    propietario = models.ForeignKey(propietario, related_name='DocsPersona', on_delete=models.CASCADE) #Al hacer las migraciones cambiar este valor en la base de dato a Nulo
    arrendatario = models.ForeignKey(arrendatario, related_name='DocsPersona', on_delete=models.CASCADE)  #Al hacer las migraciones cambiar este valor en la base de dato a Nulo
    documento = models.FileField(upload_to=Crear_carpetas) 
    class Meta:
        db_table = 'DocsPersonas'
    
class Docdescuentos(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    inmueble = models.ForeignKey(inmueble, related_name='Docdescuento', on_delete=models.CASCADE)
    valor = models.IntegerField()
    descrip = models.CharField(max_length = 400) 
    documento = models.CharField(max_length = 600)  
    class Meta:
        db_table = 'Docdescuentos'

