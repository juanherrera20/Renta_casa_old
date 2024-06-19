from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponse
import uuid
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import superuser, usuarios, arrendatario, propietario, tareas, inmueble, Documentos, Imagenes, DocsPersonas, Docdescuentos
from werkzeug.security import generate_password_hash, check_password_hash
from .functions import autenticado_required, actualizar_estados, extract_numbers, convert_time, jerarquia_estadoPago_propietario #Importo las funciones desde functions.py
from .functions import diccionarioTareaEstado, diccionarioTareaEtiqueta, diccionarioHabilitar, diccionarioPago, diccionarioInmueble, diccionarioBancos, diccionarioPorcentajeDescuento, diccionarioTipoInmueble
import json
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

#Librerias y paquetes posbilemente utiles
# from cryptography.fernet import Fernet
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth import authenticate

# Creations the views.
def nav(request):
    return render(request,'barra_navegacion.html') #Esta vista es solo una prueba "ayuda" para el diseño de la barra de navegación
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
                messages.error(request, "Contraseña incorrecta") 
        else:
            messages.error(request, "Usuario no encontrado en la base de datos")

        return redirect('index')

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
    actualizar_estados() #Llamamos a la función
    
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
            print(f"Propietario: {objeto}")
            estadosDiccionario = jerarquia_estadoPago_propietario(objeto)
            print(f"estado pago: {estadosDiccionario}")
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
    actualizar_estados()

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
            
            #----------------------REvisar esta parte--------------------------s
            ultimo_inmueble = inmueble.objects.order_by('-id').first()
            ultimo_ref = ultimo_inmueble.ref
            
            # Incrementar el número
            nuevo_ref = ultimo_ref + 1
            #-------------------------------------------------------------------s
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
    
    # Crear Paginacion para las imagenes y no mostrarlas todas
    # paginator = Paginator(imagenes, 8)  # Mostrar 5 imágenes por página
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    return render(request, 'inmuebles/individuo_inmueble.html', {'inmueble': All, 'arrendatario':objetoArrendatario, 'propietario':objetoPropietario, 'matricula':matriculas, 
                                                                 'documentos':documentos, 'imagenes':imagenes}) #Si se usa Añadir esto para paginacion 'page_obj': page_obj

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
        #print(f"Fecha: {fecha_pagar}")
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
    # print(f"Fecha cambiada: {fecha_pago}")
    # print(f"Fecha respaldo: {respaldo_fecha}")

    if fecha_pago:
        fechaPago = fecha_pago
    else:
        try:
            fechaPago =  datetime.strptime(respaldo_fecha, "%b. %d, %Y")
        except:
            fechaPago =  datetime.strptime(respaldo_fecha, "%B %d, %Y")
    obs = request.POST.get('obs')

    guardar2 = propietario.objects.get(id=idPropietario)
    guardar2.direccion = direccion
    guardar2.bancos = banco
    guardar2.num_banco = numero_banco
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
    cantidad_inmuebles = objetoPropietarios.inmueble.count()# Calcular la cantidad de inmuebles solo para este propietario
    pago = diccionarioPago[str(jerarquia_estadoPago_propietario(objetoPropietarios))]  #Solo muestra un estado en caso de que tenga mas
    objetoUser = usuarios.objects.get( id = objetoPropietarios.usuarios_id_id)
    documentos = objetoPropietarios.DocsPersona.all()
    return render(request, 'personas/propietarios/individuo_propietario.html', {'usuario':objetoUser, 'propietario':objetoPropietarios, 'pago': pago, 'documentos':documentos, 'cantidad_inmuebles': cantidad_inmuebles})

def analisis_propietarios(request):
    actualizar_estados() #Llamamos a la función
    
    #Logica para la tabla de propietarios
    objetoInmuebles = inmueble.objects.select_related('propietario_id__usuarios_id').filter(arrendatario_id__isnull=False) #Aquí filtro para que solo aparezcan los inmuebles con arrendatario

    #print(f"Inmuebles: {objetoInmuebles}")
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
    # print(f"habilitar: {estadoPropietario}")
    # print(f"Bancos: {bancoLink}")
    
    objetoCanon = inmueble.objects.values_list('canon', flat=True).filter(arrendatario_id__isnull=False)
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
    objetoArrendatario = arrendatario.objects.values_list('usuarios_id_id')
    objetoUsuario = usuarios.objects.filter(id__in = objetoArrendatario) # Se filtra para saber si son propietarios o clientes
    habilitar = usuarios.objects.filter(propie_client=2).values_list('habilitar', flat=True) # Se filtra solo el campo de 'habilitar'
    estados = [diccionarioHabilitar[str(habilitar_value)] for habilitar_value in habilitar] # Se implementa el diccionarioHabilitar
    usuarios_con_estados = []
    for usuario, estado in zip(objetoUsuario, estados): #Enpaquetando variables para que quede en una sola y poder iteraralas
        direccion = usuario.arrendatario.first().direccion if usuario.arrendatario.exists() else None
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
        fecha_limite = fechaObjeto + timedelta(days=5)

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
    return render(request, 'personas/inquilinos/individuo_inquilino.html', {'usuario':objetoUser, 'arrendatario':objetoArrendatario, 'estado':estados, 'documentos':documentos})

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
    
    if fecha_cobro: #Compruebo si se modifico la fecha
        date_cobro = fecha_cobro
        fechaCobro = datetime.strptime(date_cobro, '%Y-%m-%d')
    
    else:
        try:
            fechaCobro =  datetime.strptime(fecha_cobroRes, "%B %d, %Y")
        except:
            fechaCobro =  datetime.strptime(fecha_cobroRes, "%b. %d, %Y")
      
    fecha_limite = fechaCobro + timedelta(days=5)
  
    inicio_contrato = request.POST.get('inicio_contrato')
    inicio_contratoRes = request.POST.get('inicio_contratoRes')
   
    if inicio_contrato:
        date_contrato = inicio_contrato
        inicioContrato = datetime.strptime(date_contrato, '%Y-%m-%d')
    else:
        try:
            inicioContrato =  datetime.strptime(inicio_contratoRes, "%B %d, %Y")
        except:
            inicioContrato =  datetime.strptime(inicio_contratoRes, "%b. %d, %Y")

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
    actualizar_estados() #Llamamos a la función

    objetoInmuebles = inmueble.objects.select_related('arrendatario_id__usuarios_id').filter(arrendatario_id__isnull=False) #Solo para arrendatarios que estan vinculados a un inmueble
    
    # Obtener los tipos de inmuebles y estados de habilitación de pago de los arrendatarios
    tipoInmueble = []
    estadoArrendatario = []

    for objeto in objetoInmuebles:  #De esta manera obtengo los valores especificos para cada inmueble directamente desde el
        tipoInmueble.append(diccionarioTipoInmueble[str(objeto.tipo)])
        estadoArrendatario.append(diccionarioPago[str(objeto.arrendatario_id.habilitarPago)])
        print(f"id inmueble: {objeto.id}")
        print(f"id arendatario: {objeto.arrendatario_id}")
   
    print(f"ESto es los habilitar: {estadoArrendatario}")
    
    All = list(zip(objetoInmuebles, tipoInmueble, estadoArrendatario))
    
    return render(request, 'analisis/inquilinos/analisis_inquilinos.html',{'datosUsuario': All})

#----------------------------------------------------------------Logica para las tareas--------------------------------------------------------------------------------

def tarea(request): #Visualizar las tareas
    actualizar_estados() #Llamamos a la función
    
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

def actualizar_estado(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('taskId')
            new_status = data.get('newStatus')
            # Busca la tarea por ID y actualiza su estado
            task = tareas.objects.get(id=task_id)
            task.estado = new_status
            task.save()
            # Redirige al usuario a la página de tareas
            return redirect('tareas')
        except Exception as e:
            # Si algo sale mal, devuelve un mensaje de error
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

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
    actualizar_estados() #Llamamos a la función
    
    return render(request, 'noti.html')

#-----------------------------------------------------------------Logica para visualizar todos los datos (en analisis)--------------------------------------------------

def all_values_pro(request, id): #Vista exclusivamente para los propietarios
    actualizar_estados() #Llamamos a la función
    
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
                                                        'usuario2':objetoUser2, 'arrendatario':objetoArrendatario, 'estado':estados, 'respaldo':respaldo})

def redireccion_pro(request): #Redirección solo para los propietarios
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
        savepropietario = propietario.objects.get(id=idp) #Obtengo el propietario
        saveinmueble = inmueble.objects.get(id = idInmueble)  #Obtengo el inmueble
        fechaPago = savepropietario.fecha_pago
        antespagado = jerarquia_estadoPago_propietario(savepropietario)
        print(f"estado antes: {antespagado}")
        estadoPago = 1
       
        #Guardo el inmueble
        saveinmueble.estadoPago = estadoPago
        saveinmueble.save()
        
        pagado = jerarquia_estadoPago_propietario(savepropietario)
        print(f"jerarquia despues: {pagado}")
        if pagado == 1: #Comprobar que todos los estados esten en "Pagado" para aumentar la fecha
            nuevaFecha = fechaPago + relativedelta(months = 1)
            print("paso el filtro")
            #Guardo el propietario
            savepropietario.fecha_pago = nuevaFecha
            savepropietario.save()
            
        print("siempre se ve")
        for inmueblex in savepropietario.inmueble.all():
            print(f"estados inmuebles despues:{inmueblex.estadoPago} ")
            
        resultado = analisis_propietarios(request)
        return HttpResponse(resultado)
    
    return redirect('analisis_propietarios') #Este return se puede cambiar para el control de errores.

def confirmar_pago (request, id):
    template_path = "analisis/modal_pago.html"
    obj_propietario = propietario.objects.get(id = id)
    objs_inmuebles = obj_propietario.inmueble.exclude(estadoPago = 1) #filtrar los que no se han pagado
    objeto_usuario = usuarios.objects.filter(id = obj_propietario.id)
    if request.method == 'GET':
        total_pago = []
        for inmueble in objs_inmuebles:
            descuento = diccionarioPorcentajeDescuento[str(inmueble.porcentaje)]
            print(descuento)
            total_pago.append( inmueble.canon * (100 - descuento)/100)
            
        inmuebles = zip(objs_inmuebles, total_pago)
        print(total_pago)
        print(objs_inmuebles)
        return render(request, template_path, {"propietario": obj_propietario, "inmuebles": inmuebles})
    
    else:
       
        #Guardar los documentos de descuento y toda su información
        id_inmuebles = request.POST.getlist('inmueblesId') #Hay varios inmuebles en el formulario
        descuento=[]
        descripcion=[]
        ids_inmuebles=[]
        for id_inmueble in id_inmuebles:
            documento = request.FILES.getlist(f'docRespaldo_{id_inmueble}') #Los imputs estan en relación al inmueble
            valor = request.POST.get(f'descuento_{id_inmueble}')
            descrip = request.POST.get(f'descripcionDescuento_{id_inmueble}')
            descuento.append(valor)
            descripcion.append(descrip)
            ids_inmuebles.append(id_inmueble)
            today = str(date.today())
            fs = FileSystemStorage(location='../media/documents/'+ today) #Guardo una carpeta afuera de la carpeta principal

            urls=[]
            for doc in documento:
                filename = fs.save(doc.name, doc)
                url = fs.url(filename)
                urls.append(url)
            guardar = Docdescuentos(inmueble_id =id_inmueble, valor = valor, descrip = descrip ,documento =','.join(urls))
            """ guardar.save()  """
        propietarios = {
            'id': obj_propietario.id,
            'banco': obj_propietario.bancos,
            'num_cuenta': obj_propietario.num_banco,
        }
        propietario_user = {
            'id': objeto_usuario[0].id,
            'nombre': objeto_usuario[0].nombre,
            'apellido': objeto_usuario[0].apellido,
            'documento': objeto_usuario[0].documento,
        }
        request.session['descuentos'] = descuento
        request.session['descripcion'] = descripcion
        request.session['ids_inmuebles'] = ids_inmuebles
        request.session['obj_propietario'] = propietarios
        request.session['obj_usuario'] = propietario_user

        return redirect("factura") #Aquí se puede redireccionar al html de la factura, creo
    
#logica para facturación:
def factura(request):
    descuentos = request.session.get('descuentos', [])
    descripcion = request.session.get('descripcion', [])
    ids_inmuebles = request.session.get('ids_inmuebles', [])
    objeto_inmueblef = inmueble.objects.filter(id__in=ids_inmuebles)

    obj_propietario = request.session.get('obj_propietario')
    obj_usuario = request.session.get('obj_usuario')
    values_inmueble =[]
    i = 0
    for data in objeto_inmueblef:
        descuento = descuentos[i]
        descrip = descripcion[i]
        direccion = data.direccion
        valor_inicial = data.canon
        total = valor_inicial - int(descuento)
        values_inmueble.append([direccion, valor_inicial, descuento, total, descrip])
        i += 1
    values = list(zip(values_inmueble))
    fecha = date.today()
    fecha_actual= fecha.strftime("%d/%m/%Y")
    data = {
        'values': values,
        'propietario': obj_propietario, 
        'usuario': obj_usuario, 
        'fecha': fecha_actual
    }
    pdf = render_pdf('factura.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

def render_pdf(template_src, context_dict={}): #Cuando funcione bien, toca moverla al archivo de funciones
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), dest=result)
    if not pdf.err:
        result.seek(0)
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None

def all_values_arr(request, id): #Vista exclusivamente para los arrendatarios
    actualizar_estados() #Llamamos a la función
    
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
    pago = diccionarioPago[str(objetoPropietario.inmueble.estadoPago)]
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

    return render(request, 'analisis/all_values_arr.html', {'inmueble': All, 'matricula':matriculas, 'documentos':documentos, 'imagenes':imagenes,
                                                        'usuario':objetoUser, 'propietario':objetoPropietario, 'pago': pago, 'documentos':documentos, 'total':totalPago,
                                                        'usuario2':objetoUser2, 'arrendatario':objetoArrendatario, 'estado':estados, 'respaldo':respaldo})

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
        guardar = arrendatario.objects.get(id=idA)
        fechaCobro = guardar.fecha_inicio_cobro
        
        nuevaFecha = fechaCobro + relativedelta(months=1)
        
        fecha_limite = nuevaFecha + timedelta(days=5)
        
        habilitarPago = 1
        
        # Actualizar los campos
        guardar.habilitarPago = habilitarPago
        guardar.fecha_inicio_cobro = nuevaFecha  # Guardar el objeto datetime directamente
        guardar.fecha_fin_cobro = fecha_limite   # Guardar el objeto datetime directamente
        guardar.save()
        
        resultado = analisis_inquilinos(request)
        return HttpResponse(resultado)
    
    return redirect('dash')  # Este return se puede cambiar para el control de errores