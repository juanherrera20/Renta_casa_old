from django.shortcuts import render
from django.http import HttpResponse


# Creations the views.
def index(request):
    return render(request, 'index.html')
