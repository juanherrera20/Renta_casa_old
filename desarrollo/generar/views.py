from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import superuser


# Creations the views.
def index(request):
    return render(request, 'index.html')

def register(request):
    model = superuser
    return render(request,'register.html')

def dash(request):
    if request.method == 'GET': #Condicional para saber si los datos si se enviarón
        docuemnto = request.GET.get('docuemnto', None) #Recopilación de los datos del formulario
        password = request.GET.get('password', None)
        button1 = request.GET.get('entrar')
        button2 = request.GET.get('registrar')
        if(button1 == "1"):
            return render(request, 'dash.html')
        elif(button2 == "2"):
             return redirect('register')

    
