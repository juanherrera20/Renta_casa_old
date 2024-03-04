from django.shortcuts import render
from django.http import HttpResponse
from .models import superuser


# Creations the views.
def index(request):
    return render(request, 'index.html')

def register(request):
    model = superuser
    return render(request,'register.html')

def dash(request):
    return render(request, 'dash.html')
