from datetime import datetime, timedelta
from django.db.models import Max
from django.shortcuts import render, redirect
from .models import superuser, usuarios, arrendatario, propietario, tareas, inmueble, documentos
from werkzeug.security import generate_password_hash, check_password_hash
from django.db.models import F 
from django.contrib.auth import logout, login #Inicio y fin de sesión


#Librerias y paquetes posbilemente utiles
# from cryptography.fernet import Fernet
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth import authenticate

# Creations the views.

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Creación de diccionarios que se van a utilizar en la app.
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
diccionarioPago ={ #Va realcionado a tabla Propietarios - Campo habilitarPago
    '1': 'Pagado',
    '2': 'Debe',
    '3': 'No pago',
    '4': 'Indefinido', 
}

diccionarioInmueble={
    '1':'Activo',
    '2':'No utilizado',
    '3':'En proceso',
    '4':'Indefinido'
}

diccionarioTipoInmueble={
    '1':'Casa',
    '2':'Apartamento',
    '3':'Local',
    '4':'Aparta-estudio'
}

diccionarioPorcentajeDescuento = { # Relacionado al porcentaje de descuento por cada inmueble al valor a pagar de arrendatario
    '1' : 0.13,
    '2' : 0.14,
    '3' : 0.15,
    '4' : 0.16,
    '5' : 0.17, 
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
                #Estas son variables de sesión
                request.session["estado_sesion"] = True
                request.session["id_usuario"] = user.id
                request.session["email"] = user.email
                #----- poner mas variables de sesión en base a lo que necesitemos
                
                datos = { 'nombre' : user.nombre, 'apellido' : user.apellido} #Usar los datos a nivel de template
                return redirect('dash')
            else:
                return render(request, 'index.html', {"error": "Contraseña incorrecta"})
        else:
            return render(request, 'index.html', {"error": "Usuario no encontrado en la base de datos"})

#------------Creo el decorador para restringir las vistas sin haber autenticado el usuario--------------------------------------------s
def autenticado_required(view_func):
    def verificacion(request, *args, **kwargs):
        if not request.session.get("estado_sesion"):
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return verificacion
#---------------------------------------------------------------------------------------------------------------------------------------s

def close(request):
    try: #Elimino las variables de sesion
        del request.session["estado_sesion"] 
        del request.session["id_usuario"] 
        del request.session["email"] 
        return redirect('index') 
    except: #En caso de que lo anterior no se pueda, redirige a index directamente
        return redirect('index')

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
#-------------------------------------------------------------------------Logica del Dashboard------------------------------------------------------------------------------------------------s

@autenticado_required #Decorador personalizado 
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
    
    objetoInmuebles = inmueble.objects.select_related('propietario_id__usuarios_id').all()

    objetoTipo = inmueble.objects.values_list('tipo', flat=True)
    tipoInmueble = [diccionarioTipoInmueble[str(values)]for values in objetoTipo ]

    objetoEstado = inmueble.objects.values_list('habilitada', flat=True)
    habilitada = [diccionarioInmueble[str(values)]for values in objetoEstado ]
    All = list(zip(objetoInmuebles, tipoInmueble, habilitada))

    return render(request, 'dash.html',{'context':context, 'propietarios': usuarios_propietarios, 'arrendatarios': usuarios_arrendatarios, 'inmuebles': All})

#------------------------------------------------------------------------------Funciones para inmuebles-----------------------------------------------------------------------------
@autenticado_required
def inmu(request): #Visualizar los inmuebles (Tabla)
    objetoInmuebles = inmueble.objects.select_related('propietario_id__usuarios_id').all()

    objetoTipo = inmueble.objects.values_list('tipo', flat=True)
    tipoInmueble = [diccionarioTipoInmueble[str(values)]for values in objetoTipo ]

    objetoEstado = inmueble.objects.values_list('habilitada', flat=True)
    habilitada = [diccionarioInmueble[str(values)]for values in objetoEstado ]
    All = list(zip(objetoInmuebles, tipoInmueble, habilitada))

    return render(request, 'inmuebles/inmueble.html', {'inmuebles': All})

@autenticado_required
def add_inmueble(request): #ayuda a la Vista para añadir inmueble
    objetoPropietario = usuarios.objects.filter(propie_client=1)
    objetoArrendatario = usuarios.objects.filter(propie_client=2)
    propietarios_info = []
    for propietario in objetoPropietario:
        primer_propietario = propietario.propietario_set.first()
        if primer_propietario:
            # Crea un diccionario con el ID y el nombre completo del propietario
            propietarios_info.append({
                'id': primer_propietario.id,
                'nombre_completo': f"{propietario.nombre} {propietario.apellido}" 
            })
    arrendatarios_info = []
    for arrendatario in objetoArrendatario:
        primer_arrendatario = arrendatario.arrendatario_set.first()
        if primer_arrendatario:
            # Crea un diccionario con el ID y el nombre completo del propietario
            arrendatarios_info.append({
                'id': primer_arrendatario.id,
                'nombre_completo': f"{arrendatario.nombre} {arrendatario.apellido}"
            })
    return render(request, 'inmuebles/add_inmueble.html', {'propietarios': objetoPropietario, 'arrendatarios':objetoArrendatario, 'propietarios_info': propietarios_info, 'arrendatarios_info': arrendatarios_info})

@autenticado_required
def guardar_inmueble(request): #Logica para guardar el inmueble en la dB
      if request.method == "POST":
        id_propietario = request.POST.get('propietario', None)
        direc = request.POST.get('direccion', None)
        tipo_inmueble = request.POST.get('tipo_inmueble', None)
        canon = request.POST.get('canon', None)
        estado = request.POST.get('tipo_estado', None)
        porcentaje = request.POST.get('porcentaje_descuento', None)
        descrip = request.POST.get('descrip', None)
        
        opciones_seleccionadas = request.POST.getlist('opciones') #Tomo y creo una lista por todas las opcines elegidas
        servicios = ",".join(opciones_seleccionadas) #Las combino en una sola cadena de texto seguidas por ","
        
        ultimo_ref = inmueble.objects.all().aggregate(Max('ref'))['ref__max']
        if ultimo_ref is None:
            nuevo_ref = "1"
        else:
            nuevo_ref = str(int(ultimo_ref) + 1)

        id_arrendatario = request.POST.get('arrendatario', None)
        model=inmueble(propietario_id_id = id_propietario, arrendatario_id_id = id_arrendatario, ref= nuevo_ref, tipo = tipo_inmueble, canon= canon, descripcion= descrip, habilitada = estado, servicios = servicios, porcentaje = porcentaje, direccion= direc)
        model.save()

      if request.method == "POST":
        objetoInmueble = inmueble.objects.last() #Guarda todo el objeto del último registro
        inmueble_id = objetoInmueble.id
        document = request.FILES.get('documento')
        imagen = request.FILES.get('imagen')
        descuento = 0
        model1 = documentos(propiedad_id_id = inmueble_id, pdf = document, imagen = imagen, descuento = descuento)
        model1.save()
      return redirect('inmu')

@autenticado_required
def individuo_inmueble(request, id):
    objetoInmuebles = inmueble.objects.select_related('propietario_id__usuarios_id').filter(id = id)
    objetoDoc = documentos.objects.filter(propiedad_id_id = id)
    
    objetoTipo = inmueble.objects.values_list('tipo', flat=True)
    tipoInmueble = [diccionarioTipoInmueble[str(values)]for values in objetoTipo ]

    objetoEstado = inmueble.objects.values_list('habilitada', flat=True)
    habilitada = [diccionarioInmueble[str(values)]for values in objetoEstado ]
    
    objetoPorcentaje = inmueble.objects.values_list('porcentaje', flat=True)
    porcentaje = [diccionarioPorcentajeDescuento[str(values)] for values in objetoPorcentaje] 
    
    servicios = [servicio.strip() for servicio in objetoInmuebles[0].servicios.split(',')] if objetoInmuebles else [] #Aun no esta muy bien
    
    All = list(zip(objetoInmuebles, objetoDoc, tipoInmueble, habilitada,porcentaje,servicios))
    objetoArrendatario = usuarios.objects.filter(propie_client=2)
    return render(request, 'inmuebles/individuo_inmueble.html', {'inmueble': All, 'arrendatario':objetoArrendatario})

@autenticado_required
def actualizar_inmueble(request):
    #Recordar en el tipo de inmueble, invertir el valor que tenga por determinado, utilizando un diccionario inverso.
    # porcentaje_descuento = request.POST.get('porcentaje_descuento')
    # servicios_seleccionados = request.POST.getlist('servicios')
    # servicios = ",".join(servicios_seleccionados)
        
    return redirect('inmu')


#----------------------------------------------------------------Logica para Propietarios----------------------------------------------------------
@autenticado_required
def personas_propietarios(request): #Tabla en vista de personas propietarios
    objetoUsuario = usuarios.objects.filter(propie_client=1) #Se filtra para saber si son propietarios o clientes
    habilitar = usuarios.objects.filter(propie_client=1).values_list('habilitar', flat=True) #Se filtra solo el campo de 'habilitar'
    estados = [diccionarioHabilitar[str(habilitar_value)] for habilitar_value in habilitar] # Se implementa el diciconarioHabilitar
    
    usuarios_con_estados = []
    for usuario, estado in zip(objetoUsuario, estados): #Enpaquetando variables para que quede en una sola y poder iteraralas
        banco = usuario.propietario_set.first().bancos if usuario.propietario_set.exists() else None
        usuarios_con_estados.append((usuario, estado, banco))
    
    return render(request, 'personas/propietarios/personas_propietarios.html',{'datosUsuario':usuarios_con_estados})

def add_propietario(request): #Vista para añadir un propietario
    return render(request, 'personas/propietarios/add_propietario.html')

def guardar(request): #Logica para guardar propietarios en dB
    if request.method == "POST":        
        name = request.POST.get('nombre1', None)
        name2 = request.POST.get('nombre2', None)
        apellido = request.POST.get('apellido1', None)
        apellido2 = request.POST.get('apellido2', None)
        tipo = request.POST.get('tipo_documento', None)
        documento = request.POST.get('documento1', None)
        expedida = request.POST.get('expedida', None)
        email = request.POST.get('email', None)
        email2 = request.POST.get('email2', None)
        email3 = request.POST.get('email3', None)
        telefono = request.POST.get('phone', None)
        telefono2 = request.POST.get('phone2', None)
        telefono3 = request.POST.get('phone3', None)
        propieta = request.POST.get('propie_client', None)
        model = usuarios(nombre = name + " " + name2, apellido = apellido +" "+ apellido2, tipo_documento = tipo, documento = documento,expedida = expedida,email = email,email2 = email2,email3 = email3, telefono = telefono, telefono2 = telefono2,telefono3 = telefono3, propie_client = propieta)
        model.save()

    """ Hasta aquí son los datos de usuarios en general. """

    objeto = usuarios.objects.last() #Guarda todo el objeto del último registro
    usuarios_id = objeto.id # id del último registro guardado en la dB
    if request.method == "POST": 
        direc = request.POST.get('direc', None)
        fecha_pagar = request.POST.get('fecha_pagar', None)
        tipo_banco = request.POST.get('tipo_banco', None)
        #Aca se supone que se debe guardar el documento...
        observ = request.POST.get('obs', None)
        modelo = propietario(direccion = direc, fecha_pago = fecha_pagar, bancos = tipo_banco, obs = observ, usuarios_id_id = usuarios_id)
        modelo.save()
    return redirect('personas_propietarios')

def actualizar_propietario(request): #Actualizar propietario.
    idUsuario = request.POST.get('id')
    nombre = request.POST.get('nombre')
    apellido = request.POST.get('apellido')
    tipo_documento = request.POST.get('tipo_documento')
    documento = request.POST.get('documento')
    expedida = request.POST.get('expedida')
    telefono = request.POST.get('telefono')
    telefono2 = request.POST.get('telefono2')
    telefono3 = request.POST.get('telefono3')
    email = request.POST.get('email')
    email2 = request.POST.get('email2')
    email3 = request.POST.get('email3')
    
    guardar = usuarios.objects.get(id=idUsuario)
    guardar.nombre = nombre
    guardar.apellido = apellido
    guardar.tipo_documento = tipo_documento
    guardar.documento = documento
    guardar.expedida = expedida
    guardar.telefono = telefono
    guardar.telefono2 = telefono2
    guardar.telefono3 = telefono3
    guardar.email = email
    guardar.email2 = email2
    guardar.email3 = email3
    guardar.save()

    idPropietario = request.POST.get('idP')
    direccion = request.POST.get('direccion')
    fecha_pago = request.POST.get('fecha_pago')
    respaldo_fecha = request.POST.get('respaldo_fecha') 

    if fecha_pago:
        fechaPago = fecha_pago
    else:
        date =  datetime.strptime(respaldo_fecha, "%B %d, %Y")
        fechaPago = date.strftime("%Y-%m-%d")

    habilitarPago = request.POST.get('habilitarPago')
    obs = request.POST.get('obs')

    guardar2 = propietario.objects.get(id=idPropietario)
    guardar2.direccion = direccion
    guardar2.fecha_pago = fechaPago
    guardar2.habilitarPago = habilitarPago
    guardar2.obs = obs
    guardar2.save()

    return redirect('personas_propietarios')

def individuo_propietario(request, id):
    objetoPropietarios = propietario.objects.filter(usuarios_id_id = id).first()
    pago = diccionarioPago[str(objetoPropietarios.habilitarPago)]
    objetoUser = usuarios.objects.filter( id = objetoPropietarios.usuarios_id_id).first()
    return render(request, 'personas/propietarios/individuo_propietario.html', {'usuario':objetoUser, 'propietario':objetoPropietarios, 'pago': pago})

def analisis_propietarios(request):
    #Logica para la tabla de propietarios
    objetoUsuario = usuarios.objects.filter(propie_client=1) # Se filtra para saber si son propietarios o clientes
    usuarios_con_estados = []
    for usuario in objetoUsuario:
        direccion = usuario.propietario_set.first().direccion if usuario.propietario_set.exists() else None
        fechaPago = usuario.propietario_set.first().fecha_pago if usuario.propietario_set.exists() else None
        bancos = usuario.propietario_set.first().bancos if usuario.propietario_set.exists() else None
        estadosDiccionario = usuario.propietario_set.first().habilitarPago if usuario.propietario_set.exists() else None
        estados = diccionarioPago[str(estadosDiccionario)]
        usuarios_con_estados.append((usuario, direccion, fechaPago, bancos, estados))

    #Se debe hacer la logica para tomar el valor/canon total a pagar a propietario
    #Se debe hacer la logica para tomar el decuento/porcentaje total con respecto a inmuebles y propietarios
    #Se debe hacer la logica para saber cuantos inmuebles tiene el propietario
    return render(request, 'analisis/propietarios/analisis_propietarios.html',{'datosUsuario': usuarios_con_estados})


#-------------------------------------------------------------------Logica para inquilinos/Arrendatarios----------------------------------------------------------------

def personas_inquilinos(request): #Logica para la tabla de Inquilinos-Personas
    objetoUsuario = usuarios.objects.filter(propie_client=2) # Se filtra para saber si son propietarios o clientes
    habilitar = usuarios.objects.filter(propie_client=2).values_list('habilitar', flat=True) # Se filtra solo el campo de 'habilitar'
    estados = [diccionarioHabilitar[str(habilitar_value)] for habilitar_value in habilitar] # Se implementa el diccionarioHabilitar
    usuarios_con_estados = []
    for usuario, estado in zip(objetoUsuario, estados): #Enpaquetando variables para que quede en una sola y poder iteraralas
        direccion = usuario.arrendatario_set.first().direccion if usuario.arrendatario_set.exists() else None
        valorCobro = usuario.arrendatario_set.first().valor_cobro if usuario.arrendatario_set.exists() else None
        usuarios_con_estados.append((usuario, estado, direccion, valorCobro))
    return render(request, 'personas/inquilinos/personas_inquilinos.html', {'datosUsuario': usuarios_con_estados})

def add_inquilino(request): #Vista para añadir inquilinos
    return render(request, 'personas/inquilinos/add_inquilino.html')

def guardar_inquilino(request): #Función para guardar inquilinos
    if request.method == "POST":
        id_inmueble = request.POST.get('inmueble', None) #En este espacio debería de existir el id del inmueble al cual se le va a "asociar"
        name = request.POST.get('nombre1', None)
        name2 = request.POST.get('nombre2', None)
        apellido = request.POST.get('apellido1', None)
        apellido2 = request.POST.get('apellido2', None)
        tipo = request.POST.get('tipo_documento', None)
        documento = request.POST.get('documento1', None)
        expedida = request.POST.get('expedida', None)
        email = request.POST.get('email', None)
        email2 = request.POST.get('email2', None)
        email3 = request.POST.get('email3', None)
        telefono = request.POST.get('phone', None)
        telefono2 = request.POST.get('phone2', None)
        telefono3 = request.POST.get('phone3', None)
        propieta = request.POST.get('propie_client', None)
        model = usuarios(nombre = name + " " + name2, apellido = apellido +" "+ apellido2, tipo_documento = tipo, documento = documento,expedida = expedida,email = email,email2 = email2,email3 = email3, telefono = telefono, telefono2 = telefono2,telefono3 = telefono3, propie_client = propieta)
        model.save()

    """ Hasta aquí son los datos de usuarios en general. """
    
    objeto = usuarios.objects.last() #Guarda todo el objeto del último registro
    usuarios_id = objeto.id # id del último registro guardado en la dB
    if request.method == "POST": 
        direc = request.POST.get('direc', None)
        valor_cobrar = request.POST.get('valor_cobrar', None)
        fecha_cobrar = request.POST.get('inicio_cobro', None)

        #Logica para agregarle los 5 días de plazo para el pago.
        fechaObjeto = datetime.strptime(fecha_cobrar, "%Y-%m-%d")
        newDate = fechaObjeto + timedelta(days=5)
        fecha_limite = newDate.strftime('%Y-%m-%d')

        inicioContrato = request.POST.get('inicioContrato', None)
        finalContrato = request.POST.get('finContrato', None)
        tipo_contrato = request.POST.get('tipo_contrato', None)
        observ = request.POST.get('obs', None)
        modelo = arrendatario(direccion = direc, valor_cobro = valor_cobrar, fecha_inicio_cobro= fecha_cobrar, fecha_fin_cobro = fecha_limite, inicio_contrato = inicioContrato, fin_contrato = finalContrato, tipo_contrato = tipo_contrato, obs = observ, usuarios_id_id = usuarios_id)
        modelo.save()
    print("modelo usuario y Arrendatario, se guardan con éxito!")
    return redirect('personas_inquilinos')

def individuo_inquilino(request, id):
    objetoArrendatario= arrendatario.objects.filter(usuarios_id_id = id).first()
    objetoUser = usuarios.objects.filter( id = objetoArrendatario.usuarios_id_id).first()
    estados = diccionarioPago[str(objetoArrendatario.habilitarPago)]
    return render(request, 'personas/inquilinos/individuo_inquilino.html', {'usuario':objetoUser, 'propietario':objetoArrendatario, 'estado':estados})

def actualizar_inquilino(request): #Se actualizan usuarios y arrendatarios
    idUsuario = request.POST.get('id')
    nombre = request.POST.get('nombre')
    apellido = request.POST.get('apellido')
    tipo_documento = request.POST.get('tipo_documento')
    documento = request.POST.get('documento')
    expedida = request.POST.get('expedida')
    telefono = request.POST.get('telefono')
    telefono2 = request.POST.get('telefono2')
    telefono3 = request.POST.get('telefono3')
    email = request.POST.get('email')
    email2 = request.POST.get('email2')
    email3 = request.POST.get('email3')
    
    guardar = usuarios.objects.get(id=idUsuario)
    guardar.nombre = nombre
    guardar.apellido = apellido
    guardar.tipo_documento = tipo_documento
    guardar.documento = documento
    guardar.expedida = expedida
    guardar.telefono = telefono
    guardar.telefono2 = telefono2
    guardar.telefono3 = telefono3
    guardar.email = email
    guardar.email2 = email2
    guardar.email3 = email3
    guardar.save()

    idA = request.POST.get('idP')
    direccion = request.POST.get('direccion')
    fecha_cobro = request.POST.get('fecha_inicio')
    fecha_cobroRes = request.POST.get('fecha_inicioRes')
    
    if fecha_cobro:
        fechaCobro = fecha_cobro
    else:
        date =  datetime.strptime(fecha_cobroRes, "%B %d, %Y")
        fechaCobro = date.strftime("%Y-%m-%d")

    fechaObjeto = datetime.strptime(fechaCobro, "%Y-%m-%d")
    newDate = fechaObjeto + timedelta(days=5)
    fecha_limite = newDate.strftime('%Y-%m-%d')

    valor_cobro = request.POST.get('valor')
    
    inicio_contrato = request.POST.get('inicio_contrato')
    inicio_contratoRes = request.POST.get('inicio_contratoRes')
    if inicio_contrato:
        inicioContrato = inicio_contrato
    else:
        date =  datetime.strptime(inicio_contratoRes, "%B %d, %Y")
        inicioContrato = date.strftime("%Y-%m-%d")

    fin_contrato = request.POST.get('fin_contrato')
    fin_contratoRes = request.POST.get('fin_contratoRes')
    if fin_contrato:
        finContrato = fin_contrato
    else:
        date =  datetime.strptime(fin_contratoRes, "%B %d, %Y")
        finContrato = date.strftime("%Y-%m-%d")

    habilitarPago = request.POST.get('estado')
    tipo_contrato = request.POST.get('tipo_contrato')
    obs = request.POST.get('obs')
    
    guardar2 = arrendatario.objects.get(id=idA)
    guardar2.direccion = direccion
    guardar2.valor_cobro = valor_cobro
    guardar2.fecha_inicio_cobro = fechaCobro
    guardar2.fecha_fin_cobro = fecha_limite
    guardar2.inicio_contrato = inicioContrato
    guardar2.fin_contrato = finContrato
    guardar2.tipo_contrato = tipo_contrato
    guardar2.habilitarPago = habilitarPago
    guardar2.obs = obs
    guardar2.save()

    return redirect('personas_inquilinos')

def analisis_inquilinos(request): #Logica para la tabla de Inquilinos - Analisis
    objetoUsuario = usuarios.objects.filter(propie_client=2) # Se filtra para saber si son propietarios o clientes
    usuarios_con_estados = []
    for usuario in objetoUsuario:
        direccion = usuario.arrendatario_set.first().direccion if usuario.arrendatario_set.exists() else None
        fechaPago = usuario.arrendatario_set.first().fecha_inicio_cobro if usuario.arrendatario_set.exists() else None
        limitePago = usuario.arrendatario_set.first().fecha_fin_cobro if usuario.arrendatario_set.exists() else None
        valorPago = usuario.arrendatario_set.first().valor_cobro if usuario.arrendatario_set.exists() else None
        inicioContrato = usuario.arrendatario_set.first().inicio_contrato if usuario.arrendatario_set.exists() else None
        finContrato = usuario.arrendatario_set.first().fin_contrato if usuario.arrendatario_set.exists() else None
        tipoContrato = usuario.arrendatario_set.first().tipo_contrato if usuario.arrendatario_set.exists() else None
        estadosDiccionario = usuario.arrendatario_set.first().habilitarPago if usuario.arrendatario_set.exists() else None
        estados = diccionarioPago[str(estadosDiccionario)]
        usuarios_con_estados.append((usuario, direccion, fechaPago, limitePago, valorPago, inicioContrato, finContrato, tipoContrato, estados))
    return render(request, 'analisis/inquilinos/analisis_inquilinos.html',{'datosUsuario': usuarios_con_estados})

#----------------------------------------------------------------Logica para las tareas--------------------------------------------------------------------------------

def tarea(request): #Visualizar las tareas
    tareas_completas = tareas.objects.filter(estado='Completa').select_related('superuser_id')#Filtrar tareas Completas
    tareas_incompletas = tareas.objects.filter(estado='Incompleta').select_related('superuser_id')#Filtrar tareas incompletas
    tareas_pendientes = tareas.objects.filter(estado='Pendiente').select_related('superuser_id')#Filtrar tareas pendientes

    contexto = { #Con el contexto se pueden pasar QuerySet's independientes
        'completas': tareas_completas,
        'incompletas': tareas_incompletas,
        'pendientes': tareas_pendientes,
    }
    return render(request, 'tareas/dash_tareas.html',{'context': contexto})    

def add_tarea(request): #Poder añadir las tareas
    id = superuser.objects.values_list('id', flat=True)
    nombre = superuser.objects.values_list('nombre', flat=True)
    apellido = superuser.objects.values_list('apellido', flat=True)
    nombres_usuario = list(zip(nombre, apellido, id))
    return render(request, 'tareas/add_tarea.html',{'nombres_usuario': nombres_usuario})

def guardar_tarea(request): #Logica para guardar las tareas
    if request.method == "POST":        
        titulo = request.POST.get('titulo', None)
        descrip = request.POST.get('descrip', None)
        tipo_estado = request.POST.get('estado', None)
        tipoEstado = diccionarioTareaEstado[tipo_estado]
        fecha_fin = request.POST.get('fecha_fin', None)
        tipo_etiqueta = request.POST.get('etiqueta', None)
        tipoEtiqueta = diccionarioTareaEtiqueta[tipo_etiqueta]
        hora_inicio = request.POST.get('hora_programada', None)
        superUser=request.POST.get('usuario', None)
        model = tareas(titulo = titulo, descrip =descrip, estado = tipoEstado, fecha_fin = fecha_fin, etiqueta = tipoEtiqueta, hora_inicio = hora_inicio, superuser_id_id = superUser)
        model.save()

    return redirect('tareas')

def modal_ver_tarea(request, id): #Modal para ver más información de cada tarea
    template_path = 'tareas/modal_ver_tarea.html'
    objetoTarea = tareas.objects.filter(id = id).first()
    nombre = superuser.objects.values_list('nombre', flat=True)
    apellido = superuser.objects.values_list('apellido', flat=True)
    idSuperuser = superuser.objects.values_list('id', flat=True)
    nombres_usuario = list(zip(nombre, apellido, idSuperuser))
    return render(request, template_path, {'nombres_usuario': nombres_usuario, 'objetoTarea': objetoTarea})

def actualizar_modal(request): #Logica para actualizar cada modal o tarea
    id = request.POST.get('idTarea')
    titulo = request.POST.get('titulo')

    fechaInicio = request.POST.get('fechaInicio')
    inicioRes = request.POST.get('inicioRes')
    if fechaInicio:
        fecha_inicio = fechaInicio
    else:
        date = datetime.strptime(inicioRes, "%B %d, %Y")
        fecha_inicio = date.strftime("%Y-%m-%d")

    fechaFin = request.POST.get('fechaFin')
    finRes = request.POST.get('finRes')
    if fechaFin:
        fecha_fin = fechaFin
    else:
        date2 = datetime.strptime(finRes, "%B %d, %Y")
        fecha_fin = date2.strftime("%Y-%m-%d")    

    hora_inicio = request.POST.get('hora_inicio')
    horaRes = request.POST.get('horaRes')
    if hora_inicio:
        hora = hora_inicio
    else: 
        horaRes = horaRes.strip()
        hour = datetime.strptime(horaRes, "%I:%M %p")
        hora = hour.strftime("%H:%M")
    
    descrip = request.POST.get('descrip')
    etiqueta = request.POST.get('etiqueta')
    responsable = request.POST.get('usuario')

    guardarT = tareas.objects.get(id=id)
    guardarT.titulo = titulo
    guardarT.descrip = descrip
    guardarT.fecha_inicio = fecha_inicio
    guardarT.fecha_fin = fecha_fin
    guardarT.hora_inicio = hora
    guardarT.etiqueta = etiqueta
    guardarT.superuser_id_id = responsable
    guardarT.save()
    return redirect('tareas')


#------------------------------------------------------------------------------Logica para las notificaciones-----------------------------------------------------------------------------------------  

def noti(request):
    return render(request, 'noti.html')

#-----------------------------------------------------------------Logica para visualizar todos los datos (en analisis)--------------------------------------------------

def all_values(request, id):
    ObjetoUsuario = usuarios.objects.filter( id = id ).first()
    objetoPropietario =  propietario.objects.filter(usuarios_id_id = id).first()
    objetoArrendatario =  arrendatario.objects.filter(usuarios_id_id = id).first()
    return render(request, 'analisis/all_values.html', )