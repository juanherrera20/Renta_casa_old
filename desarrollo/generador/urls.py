"""
URL configuration for generador project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
#Se importan las vistas que se deseen ver en la página
from generar.views import index, register, dash, inmu, personas_propietarios, personas_inquilinos, analisis_propietarios, analisis_inquilinos, close
from generar.views import  tarea, noti, add_propietario, guardar, add_inquilino, guardar_inquilino,  add_tarea, guardar_tarea, modal_ver_tarea
from generar.views import individuo_propietario, individuo_inquilino,all_values_pro, add_inmueble, guardar_inmueble, individuo_inmueble, actualizar_propietario, actualizar_inquilino
from generar.views import actualizar_modal, actualizar_inmueble, redireccion_pro, redireccion_arr, all_values_arr, nav, confirmar_pago

urlpatterns = [

    path('prueba/', nav, name="navegacion"),#Esta vista es solo una prueba "ayuda" para el diseño de la barra de navegación

    path('',index, name="index"), #Se indica que nombre a url se le agrega para la facilidad de rutas.
    path('Register/', register, name="register"),
    path('Inicio/', dash, name="inicio"),
    path('Dashboard/', dash, name="dash"),
    path('Inmuebles/', inmu, name="inmu"),
    #añadir inmuebles
    path('AddInmuebles/', add_inmueble, name="addInmu"),
    path('GuardarInmueble/', guardar_inmueble, name="guardarInmueble"),
    path('Inmuebles/Code/<int:id>', individuo_inmueble, name="IndividuoInmueble"),
    path('ActualizarInmueble/', actualizar_inmueble, name="actualizarInmueble"),

    path('Personas/Propietarios/', personas_propietarios, name="personas_propietarios"),
    path('Personas/Inquilinos/', personas_inquilinos, name="personas_inquilinos"),
    path('Analisis/Propietarios/', analisis_propietarios, name="analisis_propietarios"),
    path('Analisis/Inquilinos/', analisis_inquilinos, name="analisis_inquilinos"),
    path('CloseSession/', close, name="close_session"), #URL para cerrar sesión
    path('Tareas/', tarea, name="tareas"),
    #Ver modales de tareas y de dashboard
    path('Tareas/Modal/<int:id>', modal_ver_tarea, name="modal_ver_tarea"),
    path('Inicio/Modal/<int:id>', modal_ver_tarea, name="modal_ver_tarea"),
    path('Dashboard/Modal/<int:id>', modal_ver_tarea, name="modal_ver_tarea"),
    path('Tareas/Modal/Actualizado', actualizar_modal, name="actualizarModal"),

    path('Notificaciones/', noti, name="noti"),
    #Añadir propietarios.
    path('AddPropietario/', add_propietario, name="addPropietario"),
    path('GuardarPropietario/', guardar, name="guardar"),
    path('ActualizarPropietario/', actualizar_propietario, name="ActualizarPropietario"),
    #Añadir Inquilinos.
    path('AddInquilinos/', add_inquilino, name="AddInquilinos"),
    path('GuardarInquilino/', guardar_inquilino, name="guardar_inquilino"),
    path('ActualizarInquilino/', actualizar_inquilino, name="ActualizarInquilino"),
    #Añadir tareas.
    path('AddTarea/', add_tarea, name="AddTarea"),
    path('GuardarTarea/', guardar_tarea, name="GuardarTarea"),
    path('Personas/Propietarios/Code/<int:id>', individuo_propietario, name="IndividuoPropietario"),
    path('Personas/inquilinos/Code/<int:id>', individuo_inquilino, name="IndividuoInquilino"),
    #Visualizar todos los datos
    #---------Propietarios-----------------
    path('Analisis/All/ValuesPro/<int:id>', all_values_pro, name="AllValuesPro"),
    path('Analisis/RedireccionPro/',redireccion_pro, name="redirecPro"),
    path('ConfirmarPago/', confirmar_pago, name = "confirmarPago"),
    #---------Arrendatarios-----------------
    path('Analisis/All/ValuesArr/<int:id>', all_values_arr, name="AllValuesArr"),
    path('Analisis/RedireccionArr/',redireccion_arr, name="redirecArr")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)