from django.shortcuts import render
from django.http import HttpResponse


# Creations the views.
def index(request):
    return render(request, 'index.html')

def register(request):
    return render(request,'register.html')

def dash(request):
    return render(request, 'dash.html')
