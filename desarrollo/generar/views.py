from datetime import date, datetime, timedelta
from io import BytesIO
import re, math
from dateutil.relativedelta import relativedelta
from django.templatetags.static import static
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponse
import uuid
from django.db.models import Q, Max
from django.shortcuts import render, redirect, get_object_or_404
from .models import superuser, usuarios, arrendatario, propietario, tareas, inmueble, Documentos, Imagenes, DocsPersonas, Docdescuentos, Consecutivo
from werkzeug.security import generate_password_hash, check_password_hash
from .functions import autenticado_required, actualizar_estados_propietarios,actualizar_estados_arrendatarios, actualizar_tareas, extract_numbers, convert_time, jerarquia_estadoPago_propietario, render_pdf, render_pdf_arr, calcular_monto_atraso, delete_imagenes, parse_date #Importo las funciones desde functions.py
from .functions import diccionarioTareaEstado, diccionarioTareaEtiqueta, diccionarioHabilitar, diccionarioPago, diccionarioInmueble, diccionarioBancos, diccionarioPorcentajeDescuento, diccionarioTipoInmueble
import json
import zipfile
from django.urls import reverse


#Librerias Weasyprint para generar pdfs

# from django.conf import settings
# from django.templatetags.static import static

# Creations the views.
def index(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    
    username_form = request.POST.get('documento')
    password_form = request.POST.get('password')
    try:
        user = superuser.objects.get(documento=username_form)
    except superuser.DoesNotExist:
        messages.error(request, "EL usuario no exise, intentelo nuevamente por favor.")
        return redirect('index')
    if not check_password_hash(user.password, password_form):
        messages.error(request, "Contraseña incorrecta, intentelo nuevamente por favor.")
        return redirect('index')
     # Estas son variables de sesión
    request.session["estado_sesion"] = True
    request.session["id_usuario"] = user.id
    request.session["email"] = user.email
    return redirect('dash')

def close(request):
    try: #Elimino las variables de sesion
        del request.session["estado_sesion"] 
        del request.session["id_usuario"] 
        del request.session["email"] 
        return redirect('index') 
    except: #En caso de que lo anterior no se pueda, redirige a index directamente
        return redirect('index')
#----------------------------------------------------------------Función para registrar los usuarios administrativos---------------------------------------------------------
def register(request):
    if request.method == 'POST':# Procesar el formulario cuando se envíe
        form_data = {
            'nombre': request.POST.get('nombre', None),
            'apellido': request.POST.get('apellido', None),
            'telefono': request.POST.get('telefono', None),
            'email': request.POST.get('email', None),
            'documento': request.POST.get('documento', None),
            'pass': request.POST.get('pass', None)
        }
        encrypt_passw = generate_password_hash(form_data['pass'])# Encriptar la contraseña
        try:
            model = superuser(
                nombre=form_data['nombre'],
                apellido=form_data['apellido'],
                documento=form_data['documento'],
                password=encrypt_passw,
                telefono=form_data['telefono'],
                email=form_data['email']
            )
            model.save()
            return redirect('index')
        except Exception as e:
            # Manejar el error adecuadamente, por ejemplo, mostrando un mensaje de error al usuario
            return render(request, 'register.html', {'error': "Hubo un problema al registrarte."})
    else:
        return render(request, 'register.html')# Renderizar el formulario vacío cuando la solicitud es GET
    
#-------------------------------------------------------------------------Logica del Dashboard------------------------------------------------------------------------------------------------
@autenticado_required #Decorador personalizado 
def dash(request):
    actualizar_estados_propietarios() #Llamamos a la función
    actualizar_estados_arrendatarios()
    actualizar_tareas()
    
    objetoPropietario = usuarios.objects.filter(propie_client=1).order_by('-id')[:5] #Propietarios
    contadorPropietario = usuarios.objects.filter(propie_client=1)
    num_propietarios = contadorPropietario.count()

    objetoArrendatario = usuarios.objects.filter(propie_client=2).order_by('-id')[:5] #Clientes
    contadorArrendatario = usuarios.objects.filter(propie_client=2)
    num_arrendatario = contadorArrendatario.count()

    objetoInmueble = inmueble.objects.all()
    num_inmueble = objetoInmueble.count()

    tareas_pendientes = tareas.objects.filter(estado='Pendiente').select_related('superuser_id').order_by('-id')[:4]
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
        direccion = propietario.propietario.first().direccion if propietario.propietario.exists() else None
        for objeto in propietario.propietario.all():
            estadosDiccionario = jerarquia_estadoPago_propietario(objeto)
            estados = diccionarioPago[str(estadosDiccionario)]
            estados_espacio = estados.lower().replace(' ', '')
            usuarios_propietarios.append((propietario, direccion, estados, estados_espacio))

    usuarios_arrendatarios = []
    for arrendatario in objetoArrendatario:
        direccionArrendatario = arrendatario.arrendatario.first().direccion if arrendatario.arrendatario.exists() else None
        estadosDiccionarioArrendatario = arrendatario.arrendatario.first().habilitarPago if arrendatario.arrendatario.exists() else None
        estadosArrendatario = diccionarioPago[str(estadosDiccionarioArrendatario)]
        estados_espacioA = estadosArrendatario.lower().replace(' ', '')
        usuarios_arrendatarios.append((arrendatario, direccionArrendatario, estadosArrendatario, estados_espacioA))
    
    objetoInmuebles = inmueble.objects.select_related('propietario_id__usuarios_id').order_by('-id')[:5]

    objetoTipo = inmueble.objects.values_list('tipo', flat=True)
    tipoInmueble = [diccionarioTipoInmueble[str(values)]for values in objetoTipo ]

    objetoEstado = inmueble.objects.values_list('habilitada', flat=True)
    habilitada = [diccionarioInmueble[str(values)]for values in objetoEstado ]
    habilitada_espacio = [item.lower().replace(' ', '') for item in habilitada]
    All = list(zip(objetoInmuebles, tipoInmueble, habilitada, habilitada_espacio))

    return render(request, 'dash.html',{'context':context, 'propietarios': usuarios_propietarios, 'arrendatarios': usuarios_arrendatarios, 'inmuebles': All})
#------------------------------------------------------------------------------Vistas para inmuebles-----------------------------------------------------------------------------
@autenticado_required
def inmu(request): #Visualizar los inmuebles (Tabla)
    objetoInmuebles = inmueble.objects.select_related('propietario_id__usuarios_id').all()
    num_inmueble = objetoInmuebles.count()

    objetoTipo = inmueble.objects.values_list('tipo', flat=True)
    tipoInmueble = [diccionarioTipoInmueble[str(values)]for values in objetoTipo]

    objetoEstado = inmueble.objects.values_list('habilitada', flat=True)
    habilitada = [diccionarioInmueble[str(values)]for values in objetoEstado]
    habilitada_espacio = [item.lower().replace(' ', '') for item in habilitada]
    All = list(zip(objetoInmuebles, tipoInmueble, habilitada, habilitada_espacio))

    return render(request, 'inmuebles/inmueble.html', {'inmuebles': All, 'number':num_inmueble})

@autenticado_required
def add_inmueble(request): #ayuda a la Vista para añadir inmueble
    objetoUsuarioPropietarios = propietario.objects.select_related('usuarios_id').all()
    objetoUsuarioArrendatarios = arrendatario.objects.select_related('usuarios_id').exclude(Q(inmueble__isnull=False))
    return render(request, 'inmuebles/add_inmueble.html', {'UsuarioPropietarios': objetoUsuarioPropietarios, 'UsuariosArrendatarios':objetoUsuarioArrendatarios})

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

            ultimo_inmueble = inmueble.objects.order_by('-id').first()
            ultimo_ref = int(ultimo_inmueble.ref)
            
            # Incrementar el número
            nuevo_ref = ultimo_ref + 1
            #-------------------------------------------------------------------
            id_arrendatario = request.POST.get('arrendatario', None)
            
            if id_arrendatario == '':
                id_arrendatario = None
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
                #El siguiente codigo es para darle un nombre aleatorio a cada imagen
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
    delete_imagenes(objetoInmueble)
    documentos = objetoInmueble.documentos.all()
    imagenes = objetoInmueble.imagenes.all()[:10]
    
    clave_tipo = diccionarioTipoInmueble.get(str(objetoInmueble.tipo))
    clave_estado = diccionarioInmueble.get(str(objetoInmueble.habilitada))
    clave_porcentaje = diccionarioPorcentajeDescuento.get(str(objetoInmueble.porcentaje))
    
    servicios = [servicio.strip() for servicio in objetoInmueble.servicios.split(',')] if objetoInmueble.servicios else []
    newServicios = extract_numbers(servicios)
    matriculas = [numero if numero!= 0 else 'No existe' for numero in newServicios]

    All = [(objetoInmueble, clave_tipo,clave_estado,clave_porcentaje,servicios)]
    objetoArrendatario = usuarios.objects.filter(propie_client=2).exclude(Q(arrendatario__inmueble__isnull=False)) #El Q permite anidar condiciones para el filtro
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
    
    documentos_delet = request.POST.getlist("eliminar_documentos", None)#Logica para guardar y/o eliminar imagenes y documentos
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
#----------------------------------------------------------------Logica para Propietarios----------------------------------------------------------
@autenticado_required
def personas_propietarios(request): #Tabla en vista de personas propietarios
    objetoUsuario = usuarios.objects.filter(propie_client=1) #Se filtra para saber si son propietarios o clientes
    num_inmueble = objetoUsuario.count()
    habilitar = usuarios.objects.filter(propie_client=1).values_list('habilitar', flat=True) #Se filtra solo el campo de 'habilitar'
    estados = [diccionarioHabilitar[str(habilitar_value)] for habilitar_value in habilitar] # Se implementa el diciconarioHabilitar
    
    usuarios_con_estados = []
    for usuario, estado in zip(objetoUsuario, estados): #Enpaquetando variables para que quede en una sola y poder iteraralas
        banco = usuario.propietario.first().bancos if usuario.propietario.exists() else None
        bancoLink = [diccionarioBancos[str(banco)]] 
        usuarios_con_estados.append((usuario, estado, banco, bancoLink))

    return render(request, 'personas/propietarios/personas_propietarios.html',{'datosUsuario':usuarios_con_estados, 'contador':num_inmueble})

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
        num_banco = request.POST.get('num_cuenta', None)
        observ = request.POST.get('obs', None)
        
        modelo = propietario(direccion = direc, fecha_pago = fecha_pagar, bancos = tipo_banco, num_banco = num_banco, obs = observ, usuarios_id_id = usuarios_id)
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
    banco = request.POST.get('banco')
    numero_banco = request.POST.get('num_banco')
    fecha_pago = request.POST.get('fecha_pago')
    respaldo_fecha = request.POST.get('respaldo_fecha') 

    try:
        if fecha_pago:
            fechaPago = fecha_pago
        else:
            fechaPago = parse_date(respaldo_fecha)
    except ValueError as e:
        return HttpResponse(f"Error en el inicio del contrato: {e}", status=400)
    
    obs = request.POST.get('obs')

    guardar2 = propietario.objects.get(id=idPropietario)
    guardar2.direccion = direccion
    guardar2.bancos = banco
    guardar2.num_banco = numero_banco
    guardar2.fecha_pago = fechaPago
    guardar2.obs = obs
    guardar2.save()
    
    documentos_delet = request.POST.getlist("eliminar_documentos", None)#Logica para guardar y/o eliminar documentos
    for doc_id in documentos_delet :
        document = DocsPersonas.objects.get(id = doc_id)
        document.delete()
    
    documentos_nuevos = request.FILES.getlist("documentos_nuevos", None)
    for doc in documentos_nuevos :
        DocsPersonas.objects.create( documento = doc, propietario_id = idPropietario)

    return redirect('personas_propietarios')

@autenticado_required
def individuo_propietario(request, id):
    objetoPropietarios = propietario.objects.get(usuarios_id_id = id)
    cantidad_inmuebles = objetoPropietarios.inmueble.count()# Calcular la cantidad de inmuebles solo para este propietario
    pago = diccionarioPago[str(jerarquia_estadoPago_propietario(objetoPropietarios))]  #Solo muestra un estado en caso de que tenga mas
    objetoUser = usuarios.objects.get( id = objetoPropietarios.usuarios_id_id)
    documentos = objetoPropietarios.DocsPersona.all()
    return render(request, 'personas/propietarios/individuo_propietario.html', {'usuario':objetoUser, 'propietario':objetoPropietarios, 'pago': pago, 'documentos':documentos, 'cantidad_inmuebles': cantidad_inmuebles})

@autenticado_required
def analisis_propietarios(request):
    actualizar_estados_propietarios() #Llamamos a la función
    
    #Logica para la tabla de propietarios
    objetoInmuebles = inmueble.objects.select_related('propietario_id__usuarios_id').filter(arrendatario_id__isnull=False) #Aquí filtro para que solo aparezcan los inmuebles con arrendatario
    num_inmueble = objetoInmuebles.count()
    objetoTipo = inmueble.objects.values_list('tipo', flat=True).filter(arrendatario_id__isnull=False)
    tipoInmueble = [diccionarioTipoInmueble[str(values)]for values in objetoTipo ]
    objetoPorcentaje = inmueble.objects.values_list('porcentaje', flat=True).filter(arrendatario_id__isnull=False)
    descuento = [diccionarioPorcentajeDescuento[str(values)]for values in objetoPorcentaje ]

    objetoEstado = inmueble.objects.values_list('habilitada', flat=True).filter(arrendatario_id__isnull=False)
    habilitada = [diccionarioInmueble[str(values)]for values in objetoEstado]
    
    # Obtener los estados de habilitación de pago y bancos de los propietarios
    estadoPropietario = []
    bancoLink = []         
    
    for objeto in objetoInmuebles: #De esta manera obtengo los valores especificos para cada inmueble directamente desde el
        estadoPropietario.append(diccionarioPago[str(objeto.estadoPago)])
        bancoLink.append(diccionarioBancos[str(objeto.propietario_id.bancos)])
                                                                                       
    
    estados_espacio = [valor.lower().replace(' ', '') for valor in estadoPropietario]
    objetoCanon = inmueble.objects.values_list('canon', flat=True).filter(arrendatario_id__isnull=False)
    totales = []

    for canon, des in zip(objetoCanon,descuento):
        totalDescuento = ((canon * des)/ 100)
        totalPago = (canon - totalDescuento)
        totales.append({ 'totalDescuento': totalDescuento, 'totalPago': totalPago})
    All = list(zip(objetoInmuebles, tipoInmueble, habilitada, estados_espacio, estadoPropietario, descuento, totales, bancoLink))

    return render(request, 'analisis/propietarios/analisis_propietarios.html',{ 'all': All, 'contador':num_inmueble})

#-------------------------------------------------------------------Logica para inquilinos/Arrendatarios----------------------------------------------------------------

@autenticado_required
def personas_inquilinos(request): #Logica para la tabla de Inquilinos-Personas
    objetoArrendatario = arrendatario.objects.values_list('usuarios_id_id')
    objetoUsuario = usuarios.objects.filter(id__in = objetoArrendatario) # Se filtra para saber si son propietarios o clientes
    num_inmueble = objetoUsuario.count()
    habilitar = usuarios.objects.filter(propie_client=2).values_list('habilitar', flat=True) # Se filtra solo el campo de 'habilitar'
    estados = [diccionarioHabilitar[str(habilitar_value)] for habilitar_value in habilitar] # Se implementa el diccionarioHabilitar
    usuarios_con_estados = []
    for usuario, estado in zip(objetoUsuario, estados): #Enpaquetando variables para que quede en una sola y poder iteraralas
        direccion = usuario.arrendatario.first().direccion if usuario.arrendatario.exists() else None
        usuarios_con_estados.append((usuario, estado, direccion))
    return render(request, 'personas/inquilinos/personas_inquilinos.html', {'datosUsuario': usuarios_con_estados, 'contador': num_inmueble})

@autenticado_required
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
        
        direc = request.POST.get('direccion', None)
        fecha_cobrar = request.POST.get('inicio_cobro', None)

        #Logica para agregarle los 5 días de plazo para el pago.
        fechaObjeto = datetime.strptime(fecha_cobrar, "%Y-%m-%d")
        fecha_limite = fechaObjeto + timedelta(days=4)

        inicioContrato = request.POST.get('inicioContrato', None)
        fecha_inicio_contrato = datetime.strptime(inicioContrato, "%Y-%m-%d")
        
        tipo_contrato = request.POST.get('tipo_contrato', None)
        finalContrato =""
        
        if tipo_contrato == "Trimestral":
            fechaSuma = fecha_inicio_contrato
            finalContrato = fechaSuma + relativedelta(months=3, days=-1)
      
        elif tipo_contrato == "Semestral":
            fechaSuma = fecha_inicio_contrato
            finalContrato = fechaSuma + relativedelta(months=6, days=-1)
            
        elif tipo_contrato == "Anual":
            fechaSuma = fecha_inicio_contrato
            finalContrato = fechaSuma + relativedelta(years = 1, days=-1)

        observ = request.POST.get('obs', None)
        modelo = arrendatario(direccion = direc, fecha_inicio_cobro= fecha_cobrar, fecha_fin_cobro = fecha_limite, inicio_contrato = inicioContrato, fin_contrato = finalContrato, tipo_contrato = tipo_contrato, obs = observ, usuarios_id_id = usuarios_id)
        modelo.update()
        
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

@autenticado_required
def individuo_inquilino(request, id):
    objetoArrendatario= arrendatario.objects.get(usuarios_id_id = id)
    objetoUser = usuarios.objects.get( id = objetoArrendatario.usuarios_id_id)
    documentos = objetoArrendatario.DocsPersona.all()
    obj_inmueble = objetoArrendatario.inmueble.first()
    
    estados = diccionarioPago[str(objetoArrendatario.habilitarPago)]
    return render(request, 'personas/inquilinos/individuo_inquilino.html', {'usuario':objetoUser, 'arrendatario':objetoArrendatario, 'estado':estados, 'documentos':documentos, 'inmueble':obj_inmueble})


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
    
    try:
        if fecha_cobro:  #Compruebo si se modifico la fecha
            date_cobro = fecha_cobro
            fechaCobro = parse_date(date_cobro)
        else:
            fechaCobro = parse_date(fecha_cobroRes)
    except ValueError as e:
        return HttpResponse(f"Error en el inicio del contrato: {e}", status=400)
    
    fecha_limite = fechaCobro + timedelta(days=4)
  
    inicio_contrato = request.POST.get('inicio_contrato')
    inicio_contratoRes = request.POST.get('inicio_contratoRes')
   
    try:
        if inicio_contrato:
            inicioContrato = parse_date(inicio_contrato)
        else:
            inicioContrato = parse_date(inicio_contratoRes)
    except ValueError as e:
        return HttpResponse(f"Error en el inicio del contrato: {e}", status=400)
    
    tipo_contrato = request.POST.get('tipo_contrato')
    finalContrato =""

    if tipo_contrato == "Trimestral":
        fechaSuma = inicioContrato
        finalContrato = fechaSuma + relativedelta(months=3, days=-1)
      
    elif tipo_contrato == "Semestral":
        fechaSuma = inicioContrato
        finalContrato = fechaSuma + relativedelta(months=6, days=-1)
        
    elif tipo_contrato == "Anual":
        fechaSuma = inicioContrato
        finalContrato = fechaSuma + relativedelta(years = 1, days=-1)

    obs = request.POST.get('obs')
    
    guardar2 = arrendatario.objects.get(id=idA)
    guardar2.direccion = direccion
    guardar2.fecha_inicio_cobro = fechaCobro
    guardar2.fecha_fin_cobro = fecha_limite
    guardar2.inicio_contrato = inicioContrato
    guardar2.fin_contrato = finalContrato
    guardar2.tipo_contrato = tipo_contrato
    guardar2.obs = obs
    guardar2.update()
    
    #Logica para guardar y/o eliminar documentos
    documentos_delet = request.POST.getlist("eliminar_documentos", None)
    for doc_id in documentos_delet :
        document = DocsPersonas.objects.get(id = doc_id)
        document.delete()
    
    documentos_nuevos = request.FILES.getlist("documentos_nuevos", None)
    for doc in documentos_nuevos :
        DocsPersonas.objects.create( documento = doc, arrendatario_id = idA)
        
    return redirect('personas_inquilinos')

@autenticado_required
def analisis_inquilinos(request): #Logica para la tabla de Inquilinos - Analisis
    actualizar_estados_arrendatarios()
    
    objetoInmuebles = inmueble.objects.select_related('arrendatario_id__usuarios_id').filter(arrendatario_id__isnull=False) #Solo para arrendatarios que estan vinculados a un inmueble
    num_inmueble = objetoInmuebles.count()
    # Obtener los tipos de inmuebles y estados de habilitación de pago de los arrendatarios
    tipoInmueble = []
    estadoArrendatario = []
    montos = []
    totales = []

    for objeto in objetoInmuebles:  #De esta manera obtengo los valores especificos para cada inmueble directamente desde el
        #Llamo a la función para calcular el monto de atraso y los días si aplica
        monto, dias_atrasado, meses = calcular_monto_atraso(objeto)
        total = objeto.canon * meses + monto
        
        montos.append(monto)    
        totales.append(total)
        tipoInmueble.append(diccionarioTipoInmueble[str(objeto.tipo)])
        estadoArrendatario.append(diccionarioPago[str(objeto.arrendatario_id.habilitarPago)])
        
    estados_espacio = [valor.lower().replace(' ', '') for valor in estadoArrendatario]
    All = list(zip(objetoInmuebles, tipoInmueble, estadoArrendatario, estados_espacio, montos, totales))
    
    return render(request, 'analisis/inquilinos/analisis_inquilinos.html',{'datosUsuario': All, 'contador':num_inmueble})

#----------------------------------------------------------------Logica para las tareas--------------------------------------------------------------------------------

@autenticado_required
def tarea(request): #Visualizar las tareas
    actualizar_tareas()
    
    tareas_completas = tareas.objects.filter(estado='Completa').select_related('superuser_id')#Filtrar tareas Completas
    tareas_incompletas = tareas.objects.filter(estado='Incompleta').select_related('superuser_id')#Filtrar tareas incompletas
    tareas_pendientes = tareas.objects.filter(estado='Pendiente').select_related('superuser_id')#Filtrar tareas pendientes

    contexto = { #Con el contexto se pueden pasar QuerySet's independientes
        'completas': tareas_completas,
        'incompletas': tareas_incompletas,
        'pendientes': tareas_pendientes,
    }
    return render(request, 'tareas/dash_tareas.html',{'context': contexto})    

@autenticado_required
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

@autenticado_required
def modal_ver_tarea(request, id): #Modal para ver más información de cada tarea
    template_path = 'tareas/modal_ver_tarea.html'
    objetoTarea = tareas.objects.filter(id = id).first()
    nombre = superuser.objects.values_list('nombre', flat=True)
    apellido = superuser.objects.values_list('apellido', flat=True)
    idSuperuser = superuser.objects.values_list('id', flat=True)
    nombres_usuario = list(zip(nombre, apellido, idSuperuser))
    return render(request, template_path, {'nombres_usuario': nombres_usuario, 'objetoTarea': objetoTarea})

def actualizar_estado(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('taskId')
            new_status = data.get('newStatus')
            task = tareas.objects.get(id=task_id)# Busca la tarea por ID y actualiza su estado
            task.estado = new_status
            task.save()
            return redirect('tareas')# Redirige al usuario a la página de tareas
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)# Si algo sale mal, devuelve un mensaje de error

def actualizar_modal(request): #Logica para actualizar cada modal o tarea
    id = request.POST.get('idTarea')
    titulo = request.POST.get('titulo')
    fechaInicio = request.POST.get('fechaInicio')
    inicioRes = request.POST.get('inicioRes')

    if fechaInicio:
        fecha_inicio = parse_date(fechaInicio)
    else:
        fecha_inicio = parse_date(inicioRes)

    fechaFin = request.POST.get('fechaFin')
    finRes = request.POST.get('finRes')
    

    if fechaFin:
        fecha_fin = parse_date(fechaFin)
    else:
        fecha_fin = parse_date(finRes)    

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

def eliminar_tarea(request, task_id):
    try:
        tarea = tareas.objects.get(id=task_id)
        tarea.delete()
        return redirect('tareas')
    except tareas.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

#------------------------------------------------------------------------------Logica para las notificaciones-----------------------------------------------------------------------------------------  

@autenticado_required
def noti(request):
    fecha = date.today()  # Calculo fecha del día
    objetoInmuebles = inmueble.objects.select_related('arrendatario_id__usuarios_id').filter(arrendatario_id__isnull=False)
    
    if request.method == 'GET':
        arrendatarios_contrato = []
        arrendatarios_anio = []
        
        for objeto in objetoInmuebles:
            obj_arrendatario = objeto.arrendatario_id  # Obtengo el objeto arrendatario
            obj_usuario = obj_arrendatario.usuarios_id
            estado = diccionarioPago[str(obj_arrendatario.habilitarPago)]
            
            #Los campos necesarios para los calculos
            inicio = obj_arrendatario.anual
            fecha_final_contrato = obj_arrendatario.fin_contrato
            
            resta = (fecha_final_contrato - fecha).days  # Calcular días restantes para el fin del contrato
            
            # Mirar quienes están próximos a vencerse el contrato
            if (fecha <= fecha_final_contrato and resta <= 30) or fecha >= fecha_final_contrato:
                arrendatarios_contrato.append({
                    'arrendatario': obj_arrendatario,
                    'usuario': obj_usuario,
                    'estados': estado
                })
            
            # Mirar quienes ya cumplieron el año para aumentar porcentaje
            if fecha >= inicio:
                arrendatarios_anio.append({
                    'arrendatario': obj_arrendatario,
                    'usuario': obj_usuario,
                    'inmueble': objeto,
                    'estados': estado
                })
        
        return render(request, 'noti.html', {
            'arrendatarios_contrato': arrendatarios_contrato,
            'arrendatarios_anio': arrendatarios_anio
        })
        
    if request.method == 'POST':
        action = request.POST.get('action')
        arrendatario_id = request.POST.get('arrendatario_id')
        
        try:
            obj_arrendatario = arrendatario.objects.get(id=arrendatario_id)
            obj_inmueble = obj_arrendatario.inmueble.first()
        except obj_arrendatario.DoesNotExist:
            return redirect('noti')

        if action == 'denegar':
            obj_inmueble.arrendatario_id = None
            obj_inmueble.save()
        
        if action == 'actualizar_anio':
            obj_arrendatario.anual = obj_arrendatario.anual + relativedelta(years=1)
            obj_arrendatario.save()

            return redirect('IndividuoInmueble', obj_inmueble.id)
        
        return redirect('noti')

#-----------------------------------------------------------------Logica para visualizar todos los datos (en analisis)--------------------------------------------------

@autenticado_required
def all_values_pro(request, id): #Vista exclusivamente para los propietarios
    
    #------------------------------------------------------Individuo_inmueble----------------------------------------------------
    objetoInmueble = inmueble.objects.filter(id=id).first()
    documentos = objetoInmueble.documentos.all()
    imagenes = objetoInmueble.imagenes.all()[:10]
    clave_tipo = diccionarioTipoInmueble.get(str(objetoInmueble.tipo))
    clave_estado = diccionarioInmueble.get(str(objetoInmueble.habilitada))
    clave_porcentaje = diccionarioPorcentajeDescuento.get(str(objetoInmueble.porcentaje))
    servicios = [servicio.strip() for servicio in objetoInmueble.servicios.split(',')] if objetoInmueble.servicios else []
    newServicios = extract_numbers(servicios)
    matriculas = [numero if numero!= 0 else 'No existe' for numero in newServicios]
    All = [(objetoInmueble, clave_tipo,clave_estado,clave_porcentaje,servicios)]
    
    #obtengo los descuentos del inmueble
    objs_DocDescuentos = objetoInmueble.Docdescuento.all()
    
    #------------------------------------------------------Individuo_Propietario----------------------------------------------------
    objetoPropietario = propietario.objects.filter(id=objetoInmueble.propietario_id_id).first()
    pago = diccionarioPago[str(objetoInmueble.estadoPago)]
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
    return render(request, 'analisis/all_values_pro.html', {'inmueble': All, 'matricula':matriculas, 'documentos':documentos, 'imagenes':imagenes,
                                                        'usuario':objetoUser, 'propietario':objetoPropietario, 'pago': pago, 'documentos':documentos, 'total':totalPago,
                                                        'usuario2':objetoUser2, 'arrendatario':objetoArrendatario, 'estado':estados, 'respaldo':respaldo, 'Docdescuentos': objs_DocDescuentos})


@autenticado_required
def agregar_descuento(request, id):
    obj_inmueble = inmueble.objects.get(id=id)
    obj_propietario = obj_inmueble.propietario_id
    obj_usuario = obj_propietario.usuarios_id

    if request.method == "GET":
        # Procesa el formulario aquí, si es necesario
        objs_DocDescuentos = obj_inmueble.Docdescuento.all()
        context = {
            'inmueble': obj_inmueble,
            'DocDescuentos': objs_DocDescuentos,
            'usuario': obj_usuario
        }
        return render(request, 'analisis/propietarios/agregar_descuento.html', context)
    else:
        # Manejar eliminación de descuentos
        eliminados = request.POST.getlist('eliminar')  # Obtener lista de IDs de descuentos eliminados
        if eliminados:
            for descuento_id in eliminados:
                try:
                    descuento = Docdescuentos.objects.get(id=descuento_id)
                    descuento.delete()
                except Docdescuentos.DoesNotExist:
                    continue  # Si no existe, continuar
                
                
        descuentos = []
        index = 0
        
        while True:
            valor = request.POST.get(f'descuentos[{index}][valor]')
            descripcion = request.POST.get(f'descuentos[{index}][descripcion]')
            documento = request.FILES.get(f'descuentos[{index}][documento]')
            
            if valor is None and descripcion is None and documento is None:
                break  # Salir del bucle si no hay más datos
            
            descuento_data = {
                'valor': valor,
                'descripcion': descripcion,
                'documento': documento
            }
            descuentos.append(descuento_data)
            index += 1

        # Definir la ubicación para guardar los documentos
        fs = FileSystemStorage(location=f"../media/Inmuebles/{obj_inmueble.direccion}/Documentos")

        for descuento_data in descuentos:
            valor = descuento_data.get('valor')
            descripcion = descuento_data.get('descripcion')
            documento = descuento_data.get('documento')
           
            urls = []
            if documento:
                filename = fs.save(documento.name, documento)
                url = fs.url(filename)
                urls.append(url)

            # Crear y guardar el descuento
            guardar = Docdescuentos(
                inmueble_id=id,
                valor=valor,
                descrip=descripcion,
                documento=','.join(urls),  # Guardar las URLs como una cadena separada por comas
                fecha=date.today()
            )
            guardar.save()

        # Devolver la URL a la que redirigir
        return JsonResponse({'status': 'success', 'redirect_url': reverse('AllValuesPro', args=[id])})
        #return redirect('AllValuesPro', id=obj_inmueble.id)
    
    
@autenticado_required
def redireccion_pro(request): #Redirección solo para los propietarios
    btn = request.POST.get('btn')
    idInmueble = request.POST.get('idInmueble')
    idp = request.POST.get('idP')
    idUsuario = request.POST.get('idUser')
    idArrendatario = request.POST.get('idArrendatario')

    if btn == '1':
        resultado = individuo_propietario(request, idUsuario)
        return HttpResponse(resultado)
    elif btn == '2':
        resultado = individuo_inmueble(request, idInmueble)
        return HttpResponse(resultado)
    elif btn == '3':
        resultado = individuo_inquilino(request, idArrendatario)
        return HttpResponse(resultado)
    
    return redirect('analisis_propietarios') #Este return se puede cambiar para el control de errores.

@autenticado_required
def confirmar_pago (request, id):
    template_path = "analisis/modal_pago.html"
    obj_propietario = propietario.objects.get(id = id)
    objs_inmuebles = obj_propietario.inmueble.exclude(estadoPago = 1).filter(arrendatario_id__isnull=False) #filtrar los que no se han pagado
    print(f"Inmuebles no pagados {objs_inmuebles}")
    objeto_usuario = obj_propietario.usuarios_id
    
    if request.method == 'GET':
        print("Entro metodo get")
        total_pago = []
        list_DocDescuentos = []  #Array para almacenar listas de documentos
        for obj_inmueble in objs_inmuebles:
            descuento = diccionarioPorcentajeDescuento[str(obj_inmueble.porcentaje)]
            total_pago.append( obj_inmueble.canon * (100 - descuento)/100)
            
            objs_DocDescuentos = obj_inmueble.Docdescuento.all() #Obtengo los descuentos por cada inmueble
            list_DocDescuentos.append(objs_DocDescuentos) #La lista de descuentos por cada inmueble, lo agrego a la lista de descuentos por todos los inmuebles
        inmuebles = zip(objs_inmuebles, total_pago, list_DocDescuentos)
        return render(request, template_path, {"propietario": obj_propietario, "inmuebles": inmuebles})
    
    else:
        # Captura de datos enviados en el formulario
        id_inmuebles = request.POST.getlist('inmueblesId') #Hay varuis inmuebles en el formulario
        objs_inmuebles = inmueble.objects.filter(id__in=id_inmuebles) #De esta manera traigo todos los objetos de los ids 
        print(f"EStos son los inmubles: {objs_inmuebles}")
        
        #Creo arrays para mandar datos a la factura
        totalPagar = []
        descuento = []
        descripcion = []
        ids_inmuebles = []

        # Iterar sobre los inmuebles seleccionados
        for obj_inmueble in objs_inmuebles:
            print(f"El id del objeto en el ciclo {obj_inmueble.id}")
            inmueble_id = str(obj_inmueble.id)
            
            #Obtengo los descuentos
            descuentos_aplicados = int(request.POST.get('descuentosAplicados_' + inmueble_id, 0))
            ids_descuentos_aplicados = request.POST.get('idsDescuentos_' + inmueble_id, '').split(',')
            total = request.POST.get(f'totalPagar_{inmueble_id}')
            print(f"Descutnos aplicados: {descuentos_aplicados}")
            print(f"ids de los descuentos {ids_descuentos_aplicados}")
            
            descrip = ""
            valor = descuentos_aplicados
            
            if ids_descuentos_aplicados and any(id_descuento.strip() for id_descuento in ids_descuentos_aplicados): #verifica que al menos uno de los elementos en ids_descuentos_aplicados no sea una cadena vacía después de eliminar espacios en blanco.
                print("Entro en existen descuentos aplicados")
                objs_DocDescuentos = obj_inmueble.Docdescuento.all()
                for obj_DocDescuento in objs_DocDescuentos:
                    descrip += "\n" + obj_DocDescuento.descrip
                    #obj_DocDescuento.delete() #Elimino el descuento
                    print(descrip)
            else:
                valor = 0
                descrip = "No aplica ningún descuento"
                    
            print(f"Descripción definitiva: {descrip}")
            print(f"Valor total: {valor}")
            print(f"Total {total}")
            #Se actualiza las listas para la generación de facturas
            totalPagar.append(total)
            descuento.append(valor)
            descripcion.append(descrip)
            ids_inmuebles.append(inmueble_id)
            
            # #Actualizar Fechas y estados por cada inmueble
            # estado_pago = 1
            # fechaPago = obj_inmueble.fechaPago
            
            # estadoPago = estado_pago 
            # nuevaFecha = fechaPago + relativedelta(months = 1)
            
            # obj_inmueble.estadoPago = estadoPago
            # obj_inmueble.fechaPago = nuevaFecha
            # obj_inmueble.save()
            
            # #Actualizar el propietario si todos los inmuebles ya estan pagos
            # pagado = jerarquia_estadoPago_propietario(obj_propietario) 
            
            # if pagado == 1: #Comprobar que todos los estados esten en "Pagado" para aumentar la fecha
            #     max_fecha_pago = obj_propietario.inmueble.aggregate(Max('fechaPago'))['fechaPago__max']
            #     obj_propietario.fecha_pago = max_fecha_pago
            #     obj_propietario.save()                
            
        propietarios = {
            'id': obj_propietario.id,
            'banco': obj_propietario.bancos,
            'num_cuenta': obj_propietario.num_banco,
        }
        propietario_user_id = objeto_usuario.id
        
        request.session['totalPagar'] = totalPagar
        request.session['descuentos'] = descuento
        request.session['descripcion'] = descripcion
        request.session['ids_inmuebles'] = ids_inmuebles
        request.session['obj_propietario'] = propietarios
        request.session['obj_usuario'] = propietario_user_id


        #return redirect('analisis_propietarios')
        return redirect("factura")
        
#------------------------------------------------------------------ Función para las facturas de Propietarios ----------------------------------------------------------
def factura(request):
    totalPagar = request.session.get('totalPagar', [])
    descuentos = request.session.get('descuentos', [])
    descripcion = request.session.get('descripcion', [])
    ids_inmuebles = request.session.get('ids_inmuebles', [])
    objeto_inmueblef = inmueble.objects.filter(id__in=ids_inmuebles)
    obj_propietario = request.session.get('obj_propietario')
    obj_usuario = usuarios.objects.get(id = request.session.get('obj_usuario'))
    fecha = date.today()
    fecha_actual= fecha.strftime("%d/%m/%Y")
    
    #Valor del recibo consecutivo
    consecutivo, creado = Consecutivo.objects.get_or_create(id=1) #Asegura que solo haya una instancia del objeto y si no existe crea una
    
    logo_rentacasa_url = request.build_absolute_uri(static('image/Logo RENTACASA.png'))
    logo_datacredito_url = request.build_absolute_uri(static('image/Logo-Datacredito.png'))
    pdf_files = []
    for i, data in enumerate(objeto_inmueblef):
        descuento = descuentos[i] if descuentos[i] is not None else 0
        descrip = descripcion[i] if descripcion[i] is not None else "No hay observaciones."
        direccion = data.direccion
        valor_inicial = int(float(totalPagar[i]))
        total = valor_inicial - int(descuento)
        value ={
            'direccion': direccion,
            'valor_inicial': valor_inicial,
            'descuento': descuento,
            'total': total,
            'descripcion': descrip,
            'propietario': obj_propietario, 
            'usuario': obj_usuario, 
            'fecha': fecha_actual,
            'consecutivo':f'{consecutivo.factura_pro:04d}', # '04d' significa que debe tener 4 dígitos con ceros a la izquierda,
            'logo_rentacasa_url': logo_rentacasa_url,
            'logo_datacredito_url': logo_datacredito_url,
        }
        
        #Aumento el numero para la proxima factura y actualizo
        consecutivo.factura_pro += 1
        consecutivo.save()
        
        pdf = render_pdf('factura.html', value)
        pdf_files.append((f'factura_{i+1}.pdf', pdf))

    zip_buffer = BytesIO() #Empaqueta cada pdf para luego descargar solo un .ZIP
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for filename, pdf in pdf_files:
            zip_file.writestr(filename, pdf.getvalue())
    zip_buffer.seek(0)
    nombre_zip = f"{obj_usuario.nombre.upper()}_{obj_usuario.apellido.upper()}.zip"
    
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{nombre_zip}"'
    return response


@autenticado_required
def all_values_arr(request, id): #Vista exclusivamente para los arrendatarios
    
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
    objetoPropietario = propietario.objects.filter(id=objetoInmueble.propietario_id_id).first()  #se puede optimizar 
    pago = diccionarioPago[str(objetoInmueble.estadoPago)]
    objetoUser = usuarios.objects.get( id = objetoPropietario.usuarios_id_id)
    documentos = objetoPropietario.DocsPersona.all()
    canon = objetoInmueble.canon
    objetoPorcentaje = objetoInmueble.porcentaje
    descuento_porcentaje = diccionarioPorcentajeDescuento[str(objetoPorcentaje)]
    descuento = float(descuento_porcentaje)
    totalDescuento = ((canon * descuento)/ 100)
    totalPago = (canon - totalDescuento)
    #------------------------------------------------------Individuo_Arrendatario----------------------------------------------------
    monto, dias_atrasado, meses = calcular_monto_atraso(objetoInmueble)
        
    valor_total = monto + canon * meses #si completo mas de un mes se aumenta el canon
        
    if objetoInmueble.arrendatario_id_id:
        respaldo = 1
        objetoArrendatario = arrendatario.objects.filter(id=objetoInmueble.arrendatario_id_id).first()
        objetoUser2 = usuarios.objects.filter( id = objetoArrendatario.usuarios_id_id).first()
        estados = diccionarioPago[str(objetoArrendatario.habilitarPago)]
    else: 
        respaldo = 2

    return render(request, 'analisis/all_values_arr.html', {'inmueble': All, 'canon': canon, 'matricula':matriculas, 'documentos':documentos, 'imagenes':imagenes,
                                                        'usuario':objetoUser, 'propietario':objetoPropietario, 'pago': pago, 'documentos':documentos, 'total':totalPago,
                                                        'usuario2':objetoUser2, 'arrendatario':objetoArrendatario, 'monto': monto, 'dias':dias_atrasado, 'valor_total': valor_total, 
                                                        'estado':estados, 'respaldo':respaldo, 'meses':meses})

@autenticado_required
def redireccion_arr(request):  # Redirección solo para los arrendatarios
    btn = request.POST.get('btn')
    btnPago = request.POST.get('btnRespaldoPago')
    idInmueble = request.POST.get('idInmueble')
    idUsuario = request.POST.get('idUser')
    idArrendatario = request.POST.get('idArrendatario')
    idA = request.POST.get('idA')  # Extraigo el id arrendatario para actualizar valores
    
    
    if btn == '1':
        resultado = individuo_propietario(request, idUsuario)
        return HttpResponse(resultado)
    elif btn == '2':
        resultado = individuo_inmueble(request, idInmueble)
        return HttpResponse(resultado)
    elif btn == '3':
        resultado = individuo_inquilino(request, idArrendatario)
        return HttpResponse(resultado)
    elif btnPago == '4':
        #obtengo los valores del html
        meses = int(request.POST.get('meses_acumulados'))
        documento = request.FILES.getlist('docRespaldo', None)
        descuento = request.POST.get('descuento', None)
        observaciones1 = request.POST.get('descripcionDescuento', None)
        observaciones2 = request.POST.get('descripcionOtroValor', None)
        
        print(f"EStos son los documentos: {documento}")
        print(f"ESte es el valor del descuento: {descuento}")
        print(f"Las increibles observaciones: {observaciones1}")
        print(f"Las increibles observaciones2: {observaciones2}")
        
        print(f"Los meses acumulados: {meses}")
        
        guardar = arrendatario.objects.get(id=idA)
        obj_inmueble = guardar.inmueble.first()
        
        fechaCobro = guardar.fecha_inicio_cobro
        print(f"esta es la fecha de pago inicila {fechaCobro}")
        nuevaFecha = fechaCobro + relativedelta(months= meses)
        print(f"esta es la fecha de pago aumentada un mes{nuevaFecha}")
        fecha_limite = nuevaFecha + timedelta(days=4)
        habilitarPago = 1
        urls=[]
        
        if descuento  or observaciones1:  #controlar si se apreto el boton descuento o no
            print("Entro al if")
            fs = FileSystemStorage(location=f"../media/Inmuebles/{obj_inmueble.direccion}/Documentos") #Guardo una carpeta afuera de la carpeta principal
            
            if documento: #Si se adjuntaron documentos
                print("Entro al if documentos")
                for doc in documento:
                    filename = fs.save(doc.name, doc)
                    url = fs.url(filename)
                    urls.append(url)
            doc_descuentos = Docdescuentos(inmueble_id = idInmueble, valor = descuento, descrip = observaciones1, fecha = date.today() ,documento =','.join(urls))
            doc_descuentos.save()
        else: 
            descuento = 0
            observaciones1 = "No aplica ningún descuento"

        #concatenar texto
        if observaciones2:
            observaciones = observaciones1 + ".\n" + observaciones2
            otro_valor = request.POST.get('otroValor')
        else:
            otro_valor = 0
            observaciones = observaciones1
        
        print(f"Texto final: {observaciones}")
        
        request.session['mesPagado1'] = fechaCobro.strftime("%d/%m/%Y")
        request.session['mesPagado2'] = nuevaFecha.strftime("%d/%m/%Y") #Fecha hasta donde pago, en caso de llevar meses de atraso
        request.session['monto'] = request.POST.get('monto')
        request.session['valor_total'] = request.POST.get('valor_total')
        request.session['OtroValor']= otro_valor
        request.session['valor_descuento'] = descuento
        request.session['observaciones'] = observaciones
        
        print(f"El monto de mora: {request.POST.get('monto')}")
        print(f"El valor total a pagar: {request.POST.get('valor_total')}")
        
        # Actualizar los campos
        guardar.habilitarPago = habilitarPago
        guardar.fecha_inicio_cobro = nuevaFecha  # Guardar el objeto datetime directamente
        guardar.fecha_fin_cobro = fecha_limite   # Guardar el objeto datetime directamente
        guardar.save()
        
        resultado = factura_Arr(request, idInmueble, idArrendatario)
        return resultado #Aquí se redirecciona al html de la factura para arrendatarios
    
    #return redirect('dash')  # Este return se puede cambiar para el control de errores

#------------------------------------------------------------------Función para la factura de Arrendatario----------------------------------------------------------
def factura_Arr(request, idInmueble, idArrendatario):
    
    obj_inmueble = inmueble.objects.get(id=idInmueble)
    obj_usuario = usuarios.objects.get(id=idArrendatario)
    
    #fechas
    fecha = date.today()
    fecha_actual= fecha.strftime("%d/%m/%Y")
    fecha_pago = request.session.get('mesPagado1', '')
    fecha_pago2 = request.session.get('mesPagado2', '')
    
    meses_pagados = f"{fecha_pago} al {fecha_pago2}"
    
    logo_rentacasa_url = request.build_absolute_uri(static('image/Logo RENTACASA.png'))
    logo_datacredito_url = request.build_absolute_uri(static('image/Logo-Datacredito.png'))

    otro_valor_str = str(request.session.get('OtroValor', ''))
    monto_str = str(request.session.get('monto', ''))
    valor_total_str = str(request.session.get('valor_total', ''))
    valor_descuento_srt = str(request.session.get('valor_descuento',''))
    
    #Valor del recibo consecutivo
    consecutivo, creado = Consecutivo.objects.get_or_create(id=1) #Asegura que solo haya una instancia del objeto y si no existe crea una
    
    if not valor_descuento_srt.strip():
        valor_descuento_srt = '0'
    
    otro_valor_clean = re.findall(r'\d+\.?\d*', otro_valor_str)[0] if otro_valor_str else '0'
    monto_clean = re.findall(r'\d+\.?\d*', monto_str)[0] if monto_str else '0'
    valor_total_clean = re.findall(r'\d+\.?\d*', valor_total_str)[0] if valor_total_str else '0'
    valor_descuento_clean = re.findall(r'\d+\.?\d*', valor_descuento_srt)[0] if valor_descuento_srt else '0'

    monto = float(monto_clean)
    valor_total = float(valor_total_clean)
    valor_descuento = float(valor_descuento_clean)
    descripcion = request.session.get('observaciones', [])
    descrip = descripcion if descripcion  is not None else "No hay observaciones."
        
    data = {
        'usuario': obj_usuario,
        'inmueble': obj_inmueble,
        'monto': monto,
        'valor_descuento': valor_descuento,
        'otro_valor': otro_valor_clean,
        'totalPagar': valor_total,
        'fecha_actual': fecha_actual,
        'meses_pagados':meses_pagados,
        'logo_rentacasa_url': logo_rentacasa_url,
        'logo_datacredito_url': logo_datacredito_url,
        'obs':descrip,
        'consecutivo':f'{consecutivo.factura_arr:04d}'  # '04d' significa que debe tener 4 dígitos con ceros a la izquierda,
    }
    
    #Aumento el numero para la proxima factura y actualizo
    consecutivo.factura_arr += 1
    consecutivo.save()
    
    #Nombre del archivo
    nombre_pdf = f"{obj_usuario.nombre.upper()}_{obj_usuario.apellido.upper()}.pdf"
    
    pdf = render_pdf_arr('factura_arr.html', nombre_pdf, data)
    return pdf