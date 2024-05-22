from datetime import date, datetime, timedelta
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
import re, uuid
from django.db.models import Max, Count
from django.shortcuts import render, redirect
from .models import superuser, usuarios, arrendatario, propietario, tareas, inmueble, Documentos, Imagenes, DocsPersonas, Docdescuentos
from werkzeug.security import generate_password_hash, check_password_hash
from .functions import autenticado_required, actualizar_estados, extract_numbers, convert_time #Importo las funciones desde functions.py
from .functions import diccionarioContrato, diccionarioTareaEstado, diccionarioTareaEtiqueta, diccionarioHabilitar, diccionarioPago, diccionarioInmueble, diccionarioBancos, diccionarioPorcentajeDescuento, diccionarioTipoInmueble

#Librerias y paquetes posbilemente utiles
# from cryptography.fernet import Fernet
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth import authenticate

# Creations the views.

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
    objetoPropietario = usuarios.objects.filter(propie_client=1).order_by('-id')[:5] #Propietarios
    contadorPropietario = usuarios.objects.filter(propie_client=1)
    num_propietarios = contadorPropietario.count()

    objetoArrendatario = usuarios.objects.filter(propie_client=2).order_by('-id')[:5] #Clientes
    contadorArrendatario = usuarios.objects.filter(propie_client=2)
    num_arrendatario = contadorArrendatario.count()

    objetoInmueble = inmueble.objects.all()
    num_inmueble = objetoInmueble.count()

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
        usuarios_propietarios.append((propietario, direccion, estados))

    usuarios_arrendatarios = []
    for arrendatario in objetoArrendatario:
        direccionArrendatario = arrendatario.arrendatario_set.first().direccion if arrendatario.arrendatario_set.exists() else None
        estadosDiccionarioArrendatario = arrendatario.arrendatario_set.first().habilitarPago if arrendatario.arrendatario_set.exists() else None
        estadosArrendatario = diccionarioPago[str(estadosDiccionarioArrendatario)]
        usuarios_arrendatarios.append((arrendatario, direccionArrendatario, estadosArrendatario))
    
    objetoInmuebles = inmueble.objects.select_related('propietario_id__usuarios_id').order_by('-id')[:5]

    objetoTipo = inmueble.objects.values_list('tipo', flat=True)
    tipoInmueble = [diccionarioTipoInmueble[str(values)]for values in objetoTipo ]

    objetoEstado = inmueble.objects.values_list('habilitada', flat=True)
    habilitada = [diccionarioInmueble[str(values)]for values in objetoEstado ]
    All = list(zip(objetoInmuebles, tipoInmueble, habilitada))
    actualizar_estados()

    return render(request, 'dash.html',{'context':context, 'propietarios': usuarios_propietarios, 'arrendatarios': usuarios_arrendatarios, 'inmuebles': All})

actualizar_estados() #Llamamos a la función

#------------------------------------------------------------------------------Vistas para inmuebles-----------------------------------------------------------------------------
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
                'nombre_completo': f"{propietario.apellido} {propietario.nombre}" 
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
            porcentaje = request.POST.get('porcentaje_descuento', None)
            descrip = request.POST.get('descrip', None)
            
            opciones_seleccionadas = request.POST.getlist('opciones') #Tomo y creo una lista por todas las opcines elegidas

            agua = request.POST.get('agua') if request.POST.get('agua') else "0000"
            electric = request.POST.get('electric') if request.POST.get('electric') else "0000"
            gas = request.POST.get('gas') if request.POST.get('gas') else "0000"
            internet = request.POST.get('internet') if request.POST.get('internet') else "0000"
                    
            opciones_seleccionadas.extend([agua, electric, gas, internet])
            """
            Antes de combinar los datos en una sola cadena. Se crea una lista con los inputs de las matriculas
            Donde se guardarán de la siguiente manera [agua, electric, gas, internet] y así mismo se pueden rescatar.
            """
            servicios = ",".join(opciones_seleccionadas) #Las combino en una sola cadena de texto seguidas por ","
            
            ultimo_ref = inmueble.objects.all().aggregate(Max('ref'))['ref__max']
            if ultimo_ref is None:
                nuevo_ref = "1"
            else:
                nuevo_ref = str(int(ultimo_ref) + 1)

            id_arrendatario = request.POST.get('arrendatario', None)
            if id_arrendatario:
                estado = 1
            else:
                estado = 2

            model=inmueble(propietario_id_id = id_propietario, arrendatario_id_id = id_arrendatario, ref= nuevo_ref, tipo = tipo_inmueble, canon= canon, descripcion= descrip, habilitada = estado, servicios = servicios, porcentaje = porcentaje, direccion= direc)
            model.save()

            objetoInmueble = model.id 
            #Una vez guardado el modelo, obtengo una lista del formulario para guardar las imagenes y documentos en su respectiva tabla
            imagenes = request.FILES.getlist('imagen',None)
            for imagen in imagenes :
                #El siguiente codigo es para darle un nombre aleatorio a cada imagen (Es opcional, revisar si lo implementamos o no)
                original_filename = imagen.name
                filename_unico = str(uuid.uuid4()) + "_" + original_filename
                imagen.name = filename_unico
                Imagenes.objects.create(imagen = imagen, inmueble_id = objetoInmueble)
            
            documentos = request.FILES.getlist('documento',None)
            for documento in documentos :
                Documentos.objects.create(documento = documento,inmueble_id = objetoInmueble )
                
        return redirect('inmu')

@autenticado_required
def individuo_inmueble(request, id):
    objetoInmueble = inmueble.objects.select_related('propietario_id__usuarios_id').get(id = id) #Get arroja un solo objeto filter un conjutno con n elementos
    documentos = objetoInmueble.documentos.all()
    imagenes = objetoInmueble.imagenes.all()
    
    clave_tipo = diccionarioTipoInmueble.get(str(objetoInmueble.tipo))
    clave_estado = diccionarioInmueble.get(str(objetoInmueble.habilitada))
    clave_porcentaje = diccionarioPorcentajeDescuento.get(str(objetoInmueble.porcentaje))
    
    servicios = [servicio.strip() for servicio in objetoInmueble.servicios.split(',')] if objetoInmueble.servicios else []
    newServicios = extract_numbers(servicios)
    matriculas = [numero if numero!= 0 else 'No existe' for numero in newServicios]

    All = [(objetoInmueble, clave_tipo,clave_estado,clave_porcentaje,servicios)]
    objetoArrendatario = usuarios.objects.filter(propie_client=2)
    objetoPropietario = usuarios.objects.filter(propie_client=1)
    return render(request, 'inmuebles/individuo_inmueble.html', {'inmueble': All, 'arrendatario':objetoArrendatario, 'propietario':objetoPropietario, 'matricula':matriculas, 
                                                                 'documentos':documentos, 'imagenes':imagenes})

@autenticado_required
def actualizar_inmueble(request):
    id_inmueble = request.POST.get('id',None)
    
    id_propietario = int(request.POST.get('addPropietario', None))
    propietario_obj = propietario.objects.get(usuarios_id = id_propietario)
    
    id_arrendatario = request.POST.get('addArrendatario', None)
    estado = request.POST.get('tipo_estado', None)

    if id_arrendatario:
        arrendatario_obj = arrendatario.objects.get(usuarios_id = int(id_arrendatario))
        estado = 1
    else:
        arrendatario_obj = None
        if estado:
            estado = 3
        else:
            estado = 2
    
    direc = request.POST.get('direccion', None)
    tipo_inmueble = request.POST.get('tipo_inmueble', None)
    ref = request.POST.get('ref',None)
    canon = request.POST.get('canon', None)
    porcentaje = request.POST.get('porcentaje_descuento', None)
    descrip = request.POST.get('descrip', None)
    
    opciones_seleccionadas = request.POST.getlist('opciones') #Tomo y creo una lista por todas las opcines elegidas
    agua = request.POST.get('agua') if request.POST.get('agua') else "0000"
    electric = request.POST.get('electric') if request.POST.get('electric') else "0000"
    gas = request.POST.get('gas') if request.POST.get('gas') else "0000"
    internet = request.POST.get('internet') if request.POST.get('internet') else "0000"            
    opciones_seleccionadas.extend([agua, electric, gas, internet])
    servicios = ",".join(opciones_seleccionadas) #Las combino en una sola cadena de texto seguidas por ","
    
    guardar = inmueble.objects.get(id=id_inmueble)
    guardar.propietario_id = propietario_obj
    guardar.arrendatario_id = arrendatario_obj
    guardar.tipo = tipo_inmueble
    guardar.canon = canon
    guardar.porcentaje = porcentaje
    guardar.servicios = servicios
    guardar.direccion = direc
    guardar.descripcion = descrip
    guardar.habilitada = estado
    guardar.ref = ref
    guardar.save()

    #Logica para guardar y/o eliminar imagenes y documentos
    documentos_delet = request.POST.getlist("eliminar_documentos", None)
    for doc_id in documentos_delet :
        document = Documentos.objects.get(id = doc_id)
        document.delete()
    
    documentos_nuevos = request.FILES.getlist("documentos_nuevos", None)
    for doc in documentos_nuevos :
        Documentos.objects.create( documento = doc, inmueble_id = id_inmueble)
        
    imagenes_delet = request.POST.getlist("eliminar_imagenes", None)
    for imag_id in imagenes_delet:
        imagen = Imagenes.objects.get(id = imag_id)
        imagen.delete()
    
    imagenes_nuevas = request.FILES.getlist("imagenes_nuevas",None) 
    for imag in imagenes_nuevas:
        Imagenes.objects.create( imagen = imag, inmueble_id = id_inmueble)
        
        
    return redirect('inmu')
    #Recordar en el tipo de inmueble, invertir el valor que tenga por determinado, utilizando un diccionario inverso.

#----------------------------------------------------------------Logica para Propietarios----------------------------------------------------------
@autenticado_required
def personas_propietarios(request): #Tabla en vista de personas propietarios
    objetoUsuario = usuarios.objects.filter(propie_client=1) #Se filtra para saber si son propietarios o clientes
    habilitar = usuarios.objects.filter(propie_client=1).values_list('habilitar', flat=True) #Se filtra solo el campo de 'habilitar'
    estados = [diccionarioHabilitar[str(habilitar_value)] for habilitar_value in habilitar] # Se implementa el diciconarioHabilitar
    
    usuarios_con_estados = []
    for usuario, estado in zip(objetoUsuario, estados): #Enpaquetando variables para que quede en una sola y poder iteraralas
        banco = usuario.propietario_set.first().bancos if usuario.propietario_set.exists() else None
        bancoLink = [diccionarioBancos[str(banco)]] 
        usuarios_con_estados.append((usuario, estado, banco, bancoLink))

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
        
        direc = request.POST.get('direc', None)
        fecha_pagar = request.POST.get('fecha_pagar', None)
        tipo_banco = request.POST.get('tipo_banco', None)
        observ = request.POST.get('obs', None)
        
        modelo = propietario(direccion = direc, fecha_pago = fecha_pagar, bancos = tipo_banco, obs = observ, usuarios_id_id = usuarios_id)
        modelo.save()
        
        IdObjetoPropietario = modelo.id
        #Una vez guardado el modelo, obtengo una lista del formulario para guardar los documentos en su respectiva tabla
        documentos = request.FILES.getlist('documento',None)
        for documento in documentos :
            DocsPersonas.objects.create(documento = documento, propietario_id = IdObjetoPropietario)
        
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
    obs = request.POST.get('obs')

    guardar2 = propietario.objects.get(id=idPropietario)
    guardar2.direccion = direccion
    guardar2.fecha_pago = fechaPago
    guardar2.obs = obs
    guardar2.save()
    
    #Logica para guardar y/o eliminar documentos
    documentos_delet = request.POST.getlist("eliminar_documentos", None)
    for doc_id in documentos_delet :
        document = DocsPersonas.objects.get(id = doc_id)
        document.delete()
    
    documentos_nuevos = request.FILES.getlist("documentos_nuevos", None)
    for doc in documentos_nuevos :
        DocsPersonas.objects.create( documento = doc, propietario_id = idPropietario)

    return redirect('personas_propietarios')

def individuo_propietario(request, id):
    objetoPropietarios = propietario.objects.get(usuarios_id_id = id)
    cantidad_inmuebles = objetoPropietarios.inmueble_set.count()# Calcular la cantidad de inmuebles solo para este propietario
    pago = diccionarioPago[str(objetoPropietarios.habilitarPago)]
    objetoUser = usuarios.objects.get( id = objetoPropietarios.usuarios_id_id)
    documentos = objetoPropietarios.DocsPersona.all()
    return render(request, 'personas/propietarios/individuo_propietario.html', {'usuario':objetoUser, 'propietario':objetoPropietarios, 'pago': pago, 'documentos':documentos, 'cantidad_inmuebles': cantidad_inmuebles})

def analisis_propietarios(request):
    #Logica para la tabla de propietarios
    objetoInmuebles = inmueble.objects.select_related('propietario_id__usuarios_id').filter(arrendatario_id__isnull=False) #Aquí filtro para que solo aparezcan los inmuebles con arrendatario

    objetoTipo = inmueble.objects.values_list('tipo', flat=True).filter(arrendatario_id__isnull=False)
    tipoInmueble = [diccionarioTipoInmueble[str(values)]for values in objetoTipo ]

    objetoPorcentaje = inmueble.objects.values_list('porcentaje', flat=True).filter(arrendatario_id__isnull=False)
    descuento = [diccionarioPorcentajeDescuento[str(values)]for values in objetoPorcentaje ]

    objetoEstado = inmueble.objects.values_list('habilitada', flat=True).filter(arrendatario_id__isnull=False)
    habilitada = [diccionarioInmueble[str(values)]for values in objetoEstado]
                                                                                                    #REvisar Revisar
    objetoEstadoPropietario = inmueble.objects.values_list('propietario_id__habilitarPago', flat=True).filter(arrendatario_id__isnull=False) #Aquí puede estar el error de porque se mezclan los estados en analisis
    estadoPropietario = [diccionarioPago[str(values)]for values in objetoEstadoPropietario]

    objetoCanon = inmueble.objects.values_list('canon', flat=True).filter(arrendatario_id__isnull=False)

    ObjetoBancos = inmueble.objects.values_list('propietario_id__bancos', flat=True).filter(arrendatario_id__isnull=False)
    bancoLink = [diccionarioBancos[str(values)]for values in ObjetoBancos]
    totales = []

    for canon, des in zip(objetoCanon,descuento):
        totalDescuento = ((canon * des)/ 100)
        totalPago = (canon - totalDescuento)
        totales.append({ 'totalDescuento': totalDescuento, 'totalPago': totalPago})

    All = list(zip(objetoInmuebles, tipoInmueble, habilitada, estadoPropietario, descuento, totales, bancoLink))

    #Es necesario hacer la logica para saber cuantos inmuebles tiene el propietario?
    return render(request, 'analisis/propietarios/analisis_propietarios.html',{ 'all': All})

#-------------------------------------------------------------------Logica para inquilinos/Arrendatarios----------------------------------------------------------------

def personas_inquilinos(request): #Logica para la tabla de Inquilinos-Personas
    objetoUsuario = usuarios.objects.filter(propie_client=2) # Se filtra para saber si son propietarios o clientes
    habilitar = usuarios.objects.filter(propie_client=2).values_list('habilitar', flat=True) # Se filtra solo el campo de 'habilitar'
    estados = [diccionarioHabilitar[str(habilitar_value)] for habilitar_value in habilitar] # Se implementa el diccionarioHabilitar
    usuarios_con_estados = []
    for usuario, estado in zip(objetoUsuario, estados): #Enpaquetando variables para que quede en una sola y poder iteraralas
        direccion = usuario.arrendatario_set.first().direccion if usuario.arrendatario_set.exists() else None
        usuarios_con_estados.append((usuario, estado, direccion))
    return render(request, 'personas/inquilinos/personas_inquilinos.html', {'datosUsuario': usuarios_con_estados})

def add_inquilino(request): #Vista para añadir inquilinos
    objetoInmueble = inmueble.objects.filter(arrendatario_id_id = None)
    return render(request, 'personas/inquilinos/add_inquilino.html',{'inmuebles': objetoInmueble})

def guardar_inquilino(request): #Función para guardar inquilinos
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
        
        direc = request.POST.get('direc', None)
        fecha_cobrar = request.POST.get('inicio_cobro', None)

        #Logica para agregarle los 5 días de plazo para el pago.
        fechaObjeto = datetime.strptime(fecha_cobrar, "%Y-%m-%d")
        newDate = fechaObjeto + timedelta(days=5)
        fecha_limite = newDate.strftime('%Y-%m-%d')

        inicioContrato = request.POST.get('inicioContrato', None)
        tipo_contrato = request.POST.get('tipo_contrato', None)
        finalContrato =""
        if tipo_contrato == "Trimestral":
            days = 3 * 30.67
            fechaSuma = datetime.strptime(inicioContrato, "%Y-%m-%d")
            nuevaFecha = fechaSuma + timedelta(days=days)
            finalContrato = nuevaFecha.strftime('%Y-%m-%d')
        elif tipo_contrato == "Semestral":
            days = 3 * 61.34
            fechaSuma = datetime.strptime(inicioContrato, "%Y-%m-%d")
            nuevaFecha = fechaSuma + timedelta(days=days)
            finalContrato = nuevaFecha.strftime('%Y-%m-%d')
        elif tipo_contrato == "Anual":
            days = 365
            fechaSuma = datetime.strptime(inicioContrato, "%Y-%m-%d")
            nuevaFecha = fechaSuma + timedelta(days=days)
            finalContrato = nuevaFecha.strftime('%Y-%m-%d')

        observ = request.POST.get('obs', None)
        modelo = arrendatario(direccion = direc, fecha_inicio_cobro= fecha_cobrar, fecha_fin_cobro = fecha_limite, inicio_contrato = inicioContrato, fin_contrato = finalContrato, tipo_contrato = tipo_contrato, obs = observ, usuarios_id_id = usuarios_id)
        modelo.save()
        
        #Guardar documentos
        IdObjetoArrendatario = modelo.id
        documentos = request.FILES.getlist('documento',None) #Obtengo una lista del formulario para guardar documentos
        for documento in documentos :
            DocsPersonas.objects.create(documento = documento, arrendatario_id = IdObjetoArrendatario)
        
        idInmu = request.POST.get('inmueble', None)
        if idInmu:
            objetoArrendatario = arrendatario.objects.last()
            arrendatario_id = objetoArrendatario.id
            guardar = inmueble.objects.get(id=idInmu)
            guardar.arrendatario_id_id = arrendatario_id
            guardar.save()
            
    return redirect('personas_inquilinos')

def individuo_inquilino(request, id):
    objetoArrendatario= arrendatario.objects.get(usuarios_id_id = id)
    objetoUser = usuarios.objects.get( id = objetoArrendatario.usuarios_id_id)
    documentos = objetoArrendatario.DocsPersona.all()
    print(documentos)
    
    estados = diccionarioPago[str(objetoArrendatario.habilitarPago)]
    return render(request, 'personas/inquilinos/individuo_inquilino.html', {'usuario':objetoUser, 'propietario':objetoArrendatario, 'estado':estados, 'documentos':documentos})

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
    habilitarPago = request.POST.get('estado')
    
    if fecha_cobro: #Compruebo si se modifico la fecha
        fechaCobro = fecha_cobro
    else:
        date =  datetime.strptime(fecha_cobroRes, "%B %d, %Y")
        fechaCobro = date.strftime("%Y-%m-%d")
        
    if habilitarPago == '1':
        date = datetime.strptime(fechaCobro, "%Y-%m-%d")
        nuevaFecha = date + timedelta(days=30)
        fechaCobro = nuevaFecha.strftime("%Y-%m-%d")

    fechaObjeto = datetime.strptime(fechaCobro, "%Y-%m-%d")
    newDate = fechaObjeto + timedelta(days=5)
    fecha_limite = newDate.strftime('%Y-%m-%d')

    inicio_contrato = request.POST.get('inicio_contrato')
    inicio_contratoRes = request.POST.get('inicio_contratoRes')
    if inicio_contrato:
        inicioContrato = inicio_contrato
    else:
        date =  datetime.strptime(inicio_contratoRes, "%B %d, %Y")
        inicioContrato = date.strftime("%Y-%m-%d")

    tipo_contrato = request.POST.get('tipo_contrato')

    finalContrato =""
    if tipo_contrato == "Trimestral":
        days = 3 * 30.67
        fechaSuma = datetime.strptime(inicioContrato, "%Y-%m-%d")
        nuevaFecha = fechaSuma + timedelta(days=days)
        finalContrato = nuevaFecha.strftime('%Y-%m-%d')
    elif tipo_contrato == "Semestral":
        days = 3 * 61.34
        fechaSuma = datetime.strptime(inicioContrato, "%Y-%m-%d")
        nuevaFecha = fechaSuma + timedelta(days=days)
        finalContrato = nuevaFecha.strftime('%Y-%m-%d')
    elif tipo_contrato == "Anual":
        days = 365
        fechaSuma = datetime.strptime(inicioContrato, "%Y-%m-%d")
        nuevaFecha = fechaSuma + timedelta(days=days)
        finalContrato = nuevaFecha.strftime('%Y-%m-%d')

    obs = request.POST.get('obs')
    
    guardar2 = arrendatario.objects.get(id=idA)
    guardar2.direccion = direccion
    guardar2.fecha_inicio_cobro = fechaCobro
    guardar2.fecha_fin_cobro = fecha_limite
    guardar2.inicio_contrato = inicioContrato
    guardar2.fin_contrato = finalContrato
    guardar2.tipo_contrato = tipo_contrato
    guardar2.habilitarPago = habilitarPago
    guardar2.obs = obs
    guardar2.save()
    
    #Logica para guardar y/o eliminar documentos
    documentos_delet = request.POST.getlist("eliminar_documentos", None)
    for doc_id in documentos_delet :
        document = DocsPersonas.objects.get(id = doc_id)
        document.delete()
    
    documentos_nuevos = request.FILES.getlist("documentos_nuevos", None)
    for doc in documentos_nuevos :
        DocsPersonas.objects.create( documento = doc, arrendatario_id = idA)
        
    return redirect('personas_inquilinos')

def analisis_inquilinos(request): #Logica para la tabla de Inquilinos - Analisis

    objetoInmuebles = inmueble.objects.select_related('arrendatario_id__usuarios_id').all()

    objetoTipo = inmueble.objects.values_list('tipo', flat=True)
    tipoInmueble = [diccionarioTipoInmueble[str(values)]for values in objetoTipo ]

    objetoEstadoArrendatario = inmueble.objects.values_list('arrendatario_id__habilitarPago', flat=True)
    estadoArrendatario = [diccionarioPago[str(values)]for values in objetoEstadoArrendatario]

    All = list(zip(objetoInmuebles, tipoInmueble, estadoArrendatario))

    return render(request, 'analisis/inquilinos/analisis_inquilinos.html',{'datosUsuario': All})

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
    hora =None
    if hora_inicio:
        hora = hora_inicio
    else:
        hora = convert_time(horaRes)
        
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
    #------------------------------------------------------Individuo_inmueble----------------------------------------------------
    objetoInmueble = inmueble.objects.filter(id=id).first()

    documentos = objetoInmueble.documentos.all()
    imagenes = objetoInmueble.imagenes.all()
    
    clave_tipo = diccionarioTipoInmueble.get(str(objetoInmueble.tipo))
    clave_estado = diccionarioInmueble.get(str(objetoInmueble.habilitada))
    clave_porcentaje = diccionarioPorcentajeDescuento.get(str(objetoInmueble.porcentaje))
    
    servicios = [servicio.strip() for servicio in objetoInmueble.servicios.split(',')] if objetoInmueble.servicios else []
    newServicios = extract_numbers(servicios)
    matriculas = [numero if numero!= 0 else 'No existe' for numero in newServicios]

    All = [(objetoInmueble, clave_tipo,clave_estado,clave_porcentaje,servicios)]
    #------------------------------------------------------Individuo_Propietario----------------------------------------------------

    objetoPropietario = propietario.objects.filter(id=objetoInmueble.propietario_id_id).first()
    pago = diccionarioPago[str(objetoPropietario.habilitarPago)]
    objetoUser = usuarios.objects.get( id = objetoPropietario.usuarios_id_id)
    documentos = objetoPropietario.DocsPersona.all()

    canon = objetoInmueble.canon
    objetoPorcentaje = objetoInmueble.porcentaje

    descuento_porcentaje = diccionarioPorcentajeDescuento[str(objetoPorcentaje)]
    descuento = float(descuento_porcentaje)
    totalDescuento = ((canon * descuento)/ 100)
    totalPago = (canon - totalDescuento)

    #------------------------------------------------------Individuo_Arrendatario----------------------------------------------------
    if objetoInmueble.arrendatario_id_id:
        respaldo = 1
        objetoArrendatario = arrendatario.objects.filter(id=objetoInmueble.arrendatario_id_id).first()
        objetoUser2 = usuarios.objects.filter( id = objetoArrendatario.usuarios_id_id).first()
        estados = diccionarioPago[str(objetoArrendatario.habilitarPago)]
    else: 
        respaldo = 2

    return render(request, 'analisis/all_values.html', {'inmueble': All, 'matricula':matriculas, 'documentos':documentos, 'imagenes':imagenes,
                                                        'usuario':objetoUser, 'propietario':objetoPropietario, 'pago': pago, 'documentos':documentos, 'total':totalPago,
                                                        'usuario2':objetoUser2, 'arrendatario':objetoArrendatario, 'estado':estados, 'respaldo':respaldo})

def redireccion(request):
    btn = request.POST.get('btn')
    btnPagar = request.POST.get('btnRespaldoPagar')
    idInmueble = request.POST.get('idInmueble')
    idp = request.POST.get('idP')
    idUsuario = request.POST.get('idUser')
    idArrendatario = request.POST.get('idArrendatario')
    btnConfirmar = request.POST.get('btnRespaldoConfirmar')
    if btn == '1':
        resultado = individuo_propietario(request, idUsuario)
        return HttpResponse(resultado)
    elif btn == '2':
        resultado = individuo_inmueble(request, idInmueble)
        return HttpResponse(resultado)
    elif btn == '3':
        resultado = individuo_inquilino(request, idArrendatario)
        return HttpResponse(resultado)
    elif btnPagar == '4':
        fechaPago = request.POST.get('fecha_pago')
        dat = datetime.strptime(fechaPago, "%B %d, %Y")
        nuevaFecha = dat + timedelta(days=30)
        fechaPago = nuevaFecha.strftime("%Y-%m-%d")
        habilitarPago = 4
        resultado = analisis_propietarios(request)
        save = propietario.objects.get(id=idp)
        save.habilitarPago = habilitarPago
        save.fecha_pago = fechaPago
        save.save()
        return HttpResponse(resultado)
    elif btnConfirmar == '5':
        documento = request.FILES.getlist('docRespaldo')
        valor = request.POST.get('descuento')
        descrip = request.POST.get('descripcionDescuento')
        today = str(date.today())
        fs = FileSystemStorage(location='media/documents/'+ today)

        urls=[]
        for doc in documento:
            filename = fs.save(doc.name, doc)
            url = fs.url(filename)
            urls.append(url)
        guardar = Docdescuentos(inmueble_id =idInmueble, valor = valor, descrip = descrip ,documento =','.join(urls))
        guardar.save()
        return redirect('analisis_propietarios')
    return redirect('analisis_propietarios') #Este return se puede cambiar para el control de errores.