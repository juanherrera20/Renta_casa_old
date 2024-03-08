from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import superuser
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
            return render(request, 'dash.html')
        

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
