from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import superuser
#from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth import authenticate

# #Genero clave de encriptación global
# clave_encript = Fernet.generate_key()
# cifrado = Fernet(clave_encript)

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
        ide = request.POST.get('documento', None)
        passw = request.POST.get('pass', None)
        
        # Encriptar el documento y contraseña
        encrypt_ide = generate_password_hash(ide)
        encrypt_passw = generate_password_hash(passw)
        
        # Crear y guardar el objeto superuser
        model = superuser(nombre=name, apellido=lastname, documento=ide, password=encrypt_passw, telefono=phone, habilitar=1)
        model.save()
        
        # Redireccionar a la página de inicio de sesión después del registro
        return redirect('index')
    
    else:
        # Renderizar el formulario vacío cuando la solicitud es GET
        return render(request, 'register.html')
      
def dash(request):
    # if request.method == 'POST': #Condicional para saber si los datos si se enviarón
    #     button1 = request.POST.get('entrar')
    #     button2 = request.POST.get('registrar')
    #     button3 = request.POST.get('registro')
    #     if(button1 == "1"):
    #             #Logica Login
            
    #         return render(request, 'dash.html')
    #     elif(button2 == "2"):
    #         return redirect('register')
    #     elif(button3 == "3"):
    #         if request.method == "POST":
                
    #             name = request.POST.get('nombre', None)
    #             lastname = request.POST.get('apellido', None)
    #             phone = request.POST.get('telefono', None)
    #             ide = request.POST.get('documento',None)
    #             passw = request.POST.get('pass',None)
    #             #Encript de documento y password
    #             clave_encript = Fernet.generate_key()
    #             cifrado = Fernet(clave_encript)


    #             encrypt_ide = cifrado.encrypt(ide.encode())
    #             encrypt_passw = cifrado.encrypt(passw.encode())

    #             model = superuser(nombre = name, apellido = lastname, documento = encrypt_ide, password = encrypt_passw, telefono = phone, habilitar = 1)
    #             model.save()
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
