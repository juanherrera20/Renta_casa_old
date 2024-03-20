from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import superuser, usuarios, arrendatario, propietario
from cryptography.fernet import Fernet


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
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def index(request):
    
    return render(request, 'index.html')

def close(request):
    return redirect('index')


def register(request):
    return render(request,'register.html')

def dash(request):
    if request.method == 'POST': #Condicional para saber si los datos si se enviarón
        button1 = request.POST.get('entrar')
        button2 = request.POST.get('registrar')
        button3 = request.POST.get('registro')
        if(button1 == "1"):
                #Logica Login
            
            return render(request, 'dash.html')
        elif(button2 == "2"):
            return redirect('register')
        elif(button3 == "3"):
            if request.method == "POST":
                
                name = request.POST.get('nombre', None)
                lastname = request.POST.get('apellido', None)
                phone = request.POST.get('telefono', None)
                ide = request.POST.get('documento',None)
                passw = request.POST.get('pass',None)
                #Encript de documento y password
                clave_encript = Fernet.generate_key()
                cifrado = Fernet(clave_encript)


                encrypt_ide = cifrado.encrypt(ide.encode())
                encrypt_passw = cifrado.encrypt(passw.encode())

                model = superuser(nombre = name, apellido = lastname, documento = encrypt_ide, password = encrypt_passw, telefono = phone, habilitar = 1)
                model.save()
            return redirect('index')
        

def inicio(request):
    return render(request, 'dash.html')

def inmu(request):
    return render(request, 'inmuebles/inmueble.html')


def personas_propietarios(request):
    return render(request, 'personas/propietarios/personas_propietarios.html')


def personas_inquilinos(request):
    return render(request, 'personas/inquilinos/personas_inquilinos.html')


def analisis_propietarios(request):
    return render(request, 'analisis/propietarios/analisis_propietarios.html')


def analisis_inquilinos(request):
    return render(request, 'analisis/inquilinos/analisis_inquilinos.html')

def tarea(request):
    return render(request, 'tareas.html')    

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