from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def hola_mundo(request):
    return HttpResponse("Hola Mundo, Bienvenidos a Progra III")


def saludoNombre(request, nombre, edad):
    return HttpResponse(f"Hola {nombre}, tu edad es {edad}, Bienvenidos a Progra III")

def index(request):
    return render(request, 'index.html')