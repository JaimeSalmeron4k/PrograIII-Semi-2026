from django.contrib import admin
from django.urls import path
from clientes.views import hola_mundo, saludoNombre, index


urlpatterns = [
    path('admin/', admin.site.urls),
    path('saludo/', hola_mundo),
    path('saludo/<str:nombre>/<int:edad>', saludoNombre),
    path('', index),
]
