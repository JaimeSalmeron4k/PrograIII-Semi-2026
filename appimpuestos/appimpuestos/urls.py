from django.contrib import admin
from django.urls import path
from clientes.views import hola_mundo, saludoNombre, index, vistas, guardar_cliente, buscar_clientes


urlpatterns = [
    path('admin/', admin.site.urls),
    path('saludo/', hola_mundo),
    path('saludo/<str:nombre>/<int:edad>', saludoNombre),
    path('', index),
    path('vistas/<str:form>/', vistas),
    path('guardar_cliente/', guardar_cliente),
    path('buscar_clientes/<str:buscar>', buscar_clientes),
    
]
