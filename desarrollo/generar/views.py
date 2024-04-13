from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import superuser, usuarios, arrendatario, propietario, tareas, inmueble
from werkzeug.security import generate_password_hash, check_password_hash

#Librerias y paquetes posbilemente utiles
# from cryptography.fernet import Fernet
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth import authenticate

# Creations the views.

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Creación de diccionarios que se van a utilizar en la app.
diccionarioTipo = { #Mapeo para el tipo de Identificación
            '1': 'Cedula',
            '2': 'Pasaporte',
            '3': 'Tarjeta de Identidad'
        }

diccionarioContrato = { #Mapeo para guardar el tipo de contrato
            '1': 'Trimestral',
            '2': 'Semestral',
            '3': 'Anual',
            '4': 'Indefinido'
        }
diccionarioTareaEstado = { 
            '1': 'Pendiente',
            '2': 'Completa',
            '3': 'Incompleta',
}
diccionarioTareaEtiqueta = { 
            '1': 'Presentar',
            '2': 'Visitar',
            '3': 'Mantenimiento',
            '4': 'Urgente',
            #'5': 'Finalizar',
            #'6': 'Cancelar',
            #'7': 'Finalizar',
            #'8': 'Cancelar',
}
diccionarioHabilitar ={
    '1': 'Activo',
    '2': 'Inactivo',
    '3': 'Vacaciones',
    '4': 'Indefinido', 
}
diccionarioPago ={
    '1': 'Pagado',
    '2': 'Debe',
    '3': 'No pago',
    '4': 'Indefinido', 
}
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def index(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    else: 
        # Obtengo los valores del formulario de inicio de sesión
        username_form = request.POST.get('documento')
        password_form = request.POST.get('password')
        
        # Busco el usuario en la base de datos
        user = superuser.objects.filter(documento=username_form).first()

        if user is not None:
            # Verifico si la contraseña coincide con la almacenada en la base de datos
            if check_password_hash(user.password, password_form): #Permite autenticar la contraseña del usuario encontrado
                return redirect('dash')
            else:
                return render(request, 'index.html', {"error": "Contraseña incorrecta"})
        else:
            return render(request, 'index.html', {"error": "Usuario no encontrado en la base de datos"})


def prueba(request):  #Esta vista es solo para hacer pruebas
    # Obtener todos los objetos almacenados en la base de datos
    superusers = superuser.objects.all()
    
    # Crear una lista para almacenar los nombres de los superusuarios
    nombres = [su.nombre for su in superusers]
    
    # Convertir la lista de nombres en una cadena para mostrar en la respuesta HTTP
    nombres_str = ", ".join(nombres)
    
    # Devolver una respuesta HTTP con los nombres de los superusuarios
    return HttpResponse(f"Estos son los nombres de los superusuarios: {nombres_str}")
    
def close(request):
    return redirect(request,'index')

def register(request):
    if request.method == 'POST':
        # Procesar el formulario cuando se envíe
        name = request.POST.get('nombre', None)
        lastname = request.POST.get('apellido', None)
        phone = request.POST.get('telefono', None)
        email = request.POST.get('email', None)
        ide = request.POST.get('documento', None)
        passw = request.POST.get('pass', None)
        
        # Encriptar el documento y contraseña
        encrypt_ide = generate_password_hash(ide)
        encrypt_passw = generate_password_hash(passw)
        
        # Crear y guardar el objeto superuser
        model = superuser(nombre=name, apellido=lastname, documento=ide, password=encrypt_passw, telefono=phone, email=email)
        model.save()
        
        # Redireccionar a la página de inicio de sesión después del registro
        return redirect('index')
    
    else:
        # Renderizar el formulario vacío cuando la solicitud es GET
        return render(request, 'register.html')
      
def dash(request):
    objetoPropietario = usuarios.objects.filter(propie_client=1) #Propietarios
    num_propietarios = objetoPropietario.count()
    rango_propietarios = list(range(1, num_propietarios + 1))

    objetoArrendatario = usuarios.objects.filter(propie_client=2) #Clientes
    num_arrendatario = objetoArrendatario.count()
    rango_arrendatarios = list(range(1, num_arrendatario + 1))


    objetoInmueble = inmueble.objects.all()
    num_inmueble = objetoInmueble.count()
    rango_inmuebles = list(range(1, num_inmueble + 1))

    tareas_pendientes = tareas.objects.filter(estado='Pendiente').select_related('superuser_id')
    num_tareas = tareas_pendientes.count()

    context = {
        'propietarios': num_propietarios,
        'arrendatarios': num_arrendatario,
        'inmuebles': num_inmueble,
        'tareas': num_tareas, 
        'pendientes': tareas_pendientes,     
        }
    usuarios_propietarios = []
    for propietario in objetoPropietario:
        direccion = propietario.propietario_set.first().direccion if propietario.propietario_set.exists() else None
        estadosDiccionario = propietario.propietario_set.first().habilitarPago if propietario.propietario_set.exists() else None
        estados = diccionarioPago[str(estadosDiccionario)]
        usuarios_propietarios.append((propietario, direccion, rango_propietarios, estados))

    usuarios_arrendatarios = []
    for arrendatario in objetoArrendatario:
        direccionArrendatario = arrendatario.arrendatario_set.first().direccion if arrendatario.arrendatario_set.exists() else None
        estadosDiccionarioArrendatario = arrendatario.arrendatario_set.first().habilitarPago if arrendatario.arrendatario_set.exists() else None
        estadosArrendatario = diccionarioPago[str(estadosDiccionarioArrendatario)]
        usuarios_arrendatarios.append((arrendatario, direccionArrendatario, rango_arrendatarios, estadosArrendatario))
    
    usuarios_inmuebles = []
    #Espacio para listar los datos de los inmuebles

    return render(request, 'dash.html',{'context':context, 'propietarios': usuarios_propietarios, 'arrendatarios': usuarios_arrendatarios})

def inmu(request):
    return render(request, 'inmuebles/inmueble.html')


def personas_propietarios(request):
    #Logica para la tabla de propietarios-Personas
    objetoUsuario = usuarios.objects.filter(propie_client=1) #Se filtra para saber si son propietarios o clientes
    num_usuarios = objetoUsuario.count()
    rango_ids = range(1, num_usuarios + 1)
    habilitar = usuarios.objects.filter(propie_client=1).values_list('habilitar', flat=True) #Se filtra solo el campo de 'habilitar'
    estados = [diccionarioHabilitar[str(habilitar_value)] for habilitar_value in habilitar] # Se implementa el diciconarioHabilitar
    usuarios_con_estados = list(zip(objetoUsuario, estados, rango_ids)) # Se implementan las dos listas en 1, así Django las puede iterar sin problemas en el HTML
    return render(request, 'personas/propietarios/personas_propietarios.html',{'datosUsuario':usuarios_con_estados, 'contador':num_usuarios})


def personas_inquilinos(request):
    #Logica para la tabla de Inquilinos-Personas
    objetoUsuario = usuarios.objects.filter(propie_client=2) # Se filtra para saber si son propietarios o clientes
    num_usuarios = objetoUsuario.count()
    rango_ids = list(range(1, num_usuarios + 1)) # Convierte el range en lista y pueda ser iterable
    habilitar = usuarios.objects.filter(propie_client=2).values_list('habilitar', flat=True) # Se filtra solo el campo de 'habilitar'
    estados = [diccionarioHabilitar[str(habilitar_value)] for habilitar_value in habilitar] # Se implementa el diccionarioHabilitar
    usuarios_con_estados = []
    for usuario, estado in zip(objetoUsuario, estados): #Enpaquetando variables para que quede en una sola y poder iteraralas
        direccion = usuario.arrendatario_set.first().direccion if usuario.arrendatario_set.exists() else None
        valorCobro = usuario.arrendatario_set.first().valor_cobro if usuario.arrendatario_set.exists() else None
        usuarios_con_estados.append((usuario, estado, direccion, rango_ids, valorCobro))
    return render(request, 'personas/inquilinos/personas_inquilinos.html', {'datosUsuario': usuarios_con_estados, 'contador':num_usuarios})

def analisis_propietarios(request):
    #Logica para la tabla de propietarios
    objetoUsuario = usuarios.objects.filter(propie_client=1) # Se filtra para saber si son propietarios o clientes
    num_usuarios = objetoUsuario.count()
    rango_ids = list(range(1, num_usuarios + 1)) # Convierte el range en lista y pueda ser iterable
    usuarios_con_estados = []
    for usuario in objetoUsuario:
        direccion = usuario.propietario_set.first().direccion if usuario.propietario_set.exists() else None
        fechaPago = usuario.propietario_set.first().fecha_pago if usuario.propietario_set.exists() else None
        valorPago = usuario.propietario_set.first().valor_pago if usuario.propietario_set.exists() else None
        estadosDiccionario = usuario.propietario_set.first().habilitarPago if usuario.propietario_set.exists() else None
        estados = diccionarioPago[str(estadosDiccionario)]
        usuarios_con_estados.append((usuario, direccion, rango_ids, fechaPago, valorPago, estados))
    return render(request, 'analisis/propietarios/analisis_propietarios.html',{'datosUsuario': usuarios_con_estados, 'contador':num_usuarios})


def analisis_inquilinos(request):
    #Logica para la tabla de Inquilinos
    objetoUsuario = usuarios.objects.filter(propie_client=2) # Se filtra para saber si son propietarios o clientes
    num_usuarios = objetoUsuario.count()
    rango_ids = list(range(1, num_usuarios + 1)) # Convierte el range en lista y pueda ser iterable
    usuarios_con_estados = []
    for usuario in objetoUsuario:
        direccion = usuario.arrendatario_set.first().direccion if usuario.arrendatario_set.exists() else None
        fechaPago = usuario.arrendatario_set.first().fecha_cobro if usuario.arrendatario_set.exists() else None
        valorPago = usuario.arrendatario_set.first().valor_cobro if usuario.arrendatario_set.exists() else None
        estadosDiccionario = usuario.arrendatario_set.first().habilitarPago if usuario.arrendatario_set.exists() else None
        estados = diccionarioPago[str(estadosDiccionario)]
        usuarios_con_estados.append((usuario, direccion, rango_ids, fechaPago, valorPago, estados))
    return render(request, 'analisis/inquilinos/analisis_inquilinos.html',{'datosUsuario': usuarios_con_estados, 'contador':num_usuarios})

def tarea(request):
    tareas_completas = tareas.objects.filter(estado='Completa').select_related('superuser_id')#Filtrar tareas Completas
    tareas_incompletas = tareas.objects.filter(estado='Incompleta').select_related('superuser_id')#Filtrar tareas incompletas
    tareas_pendientes = tareas.objects.filter(estado='Pendiente').select_related('superuser_id')#Filtrar tareas pendientes

    contexto = { #Con el contexto se pueden pasar QuerySet's independientes
        'completas': tareas_completas,
        'incompletas': tareas_incompletas,
        'pendientes': tareas_pendientes,
    }

    return render(request, 'tareas/dash_tareas.html',{'context': contexto})    

def add_tarea(request):
    id = superuser.objects.values_list('id', flat=True)
    nombre = superuser.objects.values_list('nombre', flat=True)
    apellido = superuser.objects.values_list('apellido', flat=True)
    nombres_usuario = list(zip(nombre, apellido, id))
    return render(request, 'tareas/add_tarea.html',{'nombres_usuario': nombres_usuario})

def guardar_tarea(request):
    if request.method == "POST":        
        titulo = request.POST.get('titulo', None)
        descrip = request.POST.get('descrip', None)
        tipo_estado = request.POST.get('estado', None)
        tipoEstado = diccionarioTareaEstado[tipo_estado]
        """ fecha_inicio = request.POST.get('fecha_inicio', None) """
        fecha_fin = request.POST.get('fecha_fin', None)
        tipo_etiqueta = request.POST.get('etiqueta', None)
        tipoEtiqueta = diccionarioTareaEtiqueta[tipo_etiqueta]
        hora_inicio = request.POST.get('hora_programada', None)
        superUser=request.POST.get('usuario', None)
        model = tareas(titulo = titulo, descrip =descrip, estado = tipoEstado, fecha_fin = fecha_fin, etiqueta = tipoEtiqueta, hora_inicio = hora_inicio, superuser_id_id = superUser)
        model.save()

    return redirect('tareas')

def modal_ver_tarea(request, id):
    template_path = 'tareas/modal_ver_tarea.html'
    objetoTarea = tareas.objects.filter(id = id).first()
    nombre = superuser.objects.values_list('nombre', flat=True)
    apellido = superuser.objects.values_list('apellido', flat=True)
    idSuperuser = superuser.objects.values_list('id', flat=True)
    nombres_usuario = list(zip(nombre, apellido, idSuperuser))
    print(objetoTarea.superuser_id_id)
    return render(request, template_path, {'nombres_usuario': nombres_usuario, 'objetoTarea': objetoTarea})

def noti(request):
    return render(request, 'noti.html')


def add_propietario(request):
    return render(request, 'personas/propietarios/add_propietario.html')

def guardar(request): #Función para guardar propietarios
    if request.method == "POST":        
        name = request.POST.get('nombre1', None)
        name2 = request.POST.get('nombre2', None)
        apellido = request.POST.get('apellido1', None)
        apellido2 = request.POST.get('apellido2', None)
        tipo = request.POST.get('tipo_documento', None)
        tipoDocumento = diccionarioTipo[tipo]
        documento = request.POST.get('documento1', None)
        email = request.POST.get('email', None)
        telefono = request.POST.get('phone', None)
        propieta = request.POST.get('propie_client', None)
        model = usuarios(nombre = name + " " + name2, apellido = apellido +" "+ apellido2, tipo_documento = tipoDocumento, documento = documento,email = email, telefono = telefono, propie_client = propieta)
        model.save()

    """ Hasta aquí son los datos de usuarios en general. """

    objeto = usuarios.objects.last() #Guarda todo el objeto del último registro
    usuarios_id = objeto.id # id del último registro guardado en la dB
    if request.method == "POST": 
        direc = request.POST.get('direc', None)
        valor_pagar = request.POST.get('valor_pagar', None)
        fecha_pagar = request.POST.get('fecha_pagar', None)
        tipo_contrato = request.POST.get('tipo_contrato', None)
        tipoContrato = diccionarioContrato[tipo_contrato]
        observ = request.POST.get('obs', None)
        modelo = propietario(direccion = direc, valor_pago = valor_pagar, fecha_pago = fecha_pagar, tipo_contrato = tipoContrato, obs = observ, usuarios_id_id = usuarios_id)
        modelo.save()
    print("modelo usuario y propietario, se guardan con éxito!")
    

    return redirect('personas_propietarios')
    #Funciones para añadir inquilinos

def add_inquilino(request):
    return render(request, 'personas/inquilinos/add_inquilino.html')


def guardar_inquilino(request): #Función para guardar inquilinos
    if request.method == "POST":
        id_inmueble = request.POST.get('inmueble', None) #En este espacio debería de existir el id del inmueble al cual se le va a "asociar"
        name = request.POST.get('nombre1', None)
        name2 = request.POST.get('nombre2', None)
        apellido = request.POST.get('apellido1', None)
        apellido2 = request.POST.get('apellido2', None)

        tipo = request.POST.get('tipo_documento', None)
        tipoDocumento = diccionarioTipo[tipo]
        documento = request.POST.get('documento1', None)
        email = request.POST.get('email', None)
        telefono = request.POST.get('phone', None)
        client = request.POST.get('propie_client', None) #Recordar que el valor de '1' es para propietarios y '2' para clientes.
        model = usuarios(nombre = name + " " + name2, apellido = apellido +" "+ apellido2, tipo_documento = tipoDocumento, documento = documento,email = email, telefono = telefono, propie_client = client)
        model.save()

    """ Hasta aquí son los datos de usuarios en general. """
    
    objeto = usuarios.objects.last() #Guarda todo el objeto del último registro
    usuarios_id = objeto.id # id del último registro guardado en la dB
    if request.method == "POST": 
        direc = request.POST.get('direc', None)
        valor_cobrar = request.POST.get('valor_cobrar', None)
        fecha_cobrar = request.POST.get('fecha_cobro', None)
        inicioContrato = request.POST.get('inicioContrato', None)
        finalContrato = request.POST.get('finContrato', None)
        tipo_contrato = request.POST.get('tipo_contrato', None)

        tipoContrato = diccionarioContrato[tipo_contrato]
        observ = request.POST.get('obs', None)
        modelo = arrendatario(direccion = direc, valor_cobro = valor_cobrar, fecha_cobro = fecha_cobrar, inicio_contrato = inicioContrato, fin_contrato = finalContrato, tipo_contrato = tipoContrato, obs = observ, usuarios_id_id = usuarios_id)
        modelo.save()
    print("modelo usuario y Arrendatario, se guardan con éxito!")
    return redirect('personas_inquilinos')

def individuo_propietario(request, id):
    objetoPropietarios = propietario.objects.filter(id = id).first()
    objetoUser = usuarios.objects.filter( id = objetoPropietarios.usuarios_id_id).first()
    print(objetoUser.nombre)
    return render(request, 'personas/propietarios/individuo_propietario.html', {'id':id})