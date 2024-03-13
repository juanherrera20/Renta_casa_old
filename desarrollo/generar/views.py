from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import superuser, usuarios
from cryptography.fernet import Fernet


# Creations the views.
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

def guardar(request):
    """ if request.method == "POST":        
        name = request.POST.get('nombre1', None)
        name2 = request.POST.get('nombre2', None)
        apellido = request.POST.get('apellido1', None)
        apellido2 = request.POST.get('apellido2', None)

        tipo = request.POST.get('tipo_documento', None)
        diccionarioTipo = { #Se hace un mapeo para su facil modificación e implementación.
            '1': 'Cedula',
            '2': 'Pasaporte',
            '3': 'Tarjeta de Identidad'
        }
        tipoDocumento = diccionarioTipo[tipo]
        documento = request.POST.get('documento1', None)
        email = request.POST.get('email', None)
        telefono = request.POST.get('phone', None)
        propietario = request.POST.get('propie_client', None)
        model = usuarios(nombre = name + " " + name2, apellido = apellido +" "+ apellido2, tipo_documento = tipoDocumento, documento = documento,email = email, telefono = telefono, propie_client = propietario)
        model.save() """

    """ Hasta aquí son los datos de usuarios en general. """
    
    objeto = usuarios.objects.last()
    ide_propie = objeto.id
    """ objeto.nombre -> es una forma de acceder a los datos de forma individual """
    """ for atributo in objeto._meta.fields: #Forma de iterarar los datos para mostrarlos tipo Lista.
        print(atributo.name, getattr(objeto, atributo.name)) """

    return redirect('personas_propietarios')
