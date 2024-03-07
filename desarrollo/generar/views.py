from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import superuser


# Creations the views.
def index(request):
    return render(request, 'index.html')

def register(request):
    return render(request,'register.html')

def dash(request):
    if request.method == 'POST': #Condicional para saber si los datos si se enviarón
        button1 = request.POST.get('entrar')
        button2 = request.POST.get('registrar')
        button3 = request.POST.get('registro')
        if(button1 == "1"):
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
                model = superuser(nombre = name, apellido = lastname, documento = ide, password = passw, telefono = phone, habilitar = 1)
                model.save()
                """ print(nombre, apellido, telefono, password, documento) """
            return render(request, 'dash.html')

    
