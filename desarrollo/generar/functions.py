#--------------------------------------------------------------------------------------------------------------------------------s
#En este archivo se registran todas las funciones y diccionarios que usamos para manejar la logica del backend.
#--------------------------------------------------------------------------------------------------------------------------------s

from datetime import datetime,timedelta, date
import re
from django.shortcuts import redirect
from .models import superuser, usuarios, arrendatario, propietario, tareas, inmueble, Documentos, Imagenes, DocsPersonas, Docdescuentos
from werkzeug.security import generate_password_hash, check_password_hash

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Creación de diccionarios que se van a utilizar en la app.
diccionarioContrato = { #Mapeo para guardar el tipo de contrato
            '1': 'Trimestral',
            '2': 'Semestral',
            '3': 'Anual',
            '4': 'Indefinido'
        }
diccionarioTareaEstado = { 
            '1': 'Pendiente',
            '2': 'Completa',
            '3': 'Incompleta',
}
diccionarioTareaEtiqueta = { 
            '1': 'Presentar',
            '2': 'Visitar',
            '3': 'Mantenimiento',
            '4': 'Urgente',
            #'5': 'Finalizar',
            #'6': 'Cancelar',
            #'7': 'Finalizar',
            #'8': 'Cancelar',
}
diccionarioHabilitar ={
    '1': 'Activo',
    '2': 'Inactivo',
    '3': 'Vacaciones',
    '4': 'Indefinido', 
}
diccionarioPago ={ #Va realcionado a tabla Propietarios y Arrendatarios- Campo habilitarPago
    '1': 'Pagado',
    '2': 'Debe',
    '3': 'No pago',
    '4': 'Pagado',
    'None': 'Revisar'
}

diccionarioInmueble={
    '1':'Activo',
    '2':'No utilizado',
    '3':'En proceso',
    '4':'Indefinido'
}

diccionarioTipoInmueble={
    '1':'Casa',
    '2':'Apartamento',
    '3':'Local',
    '4':'Aparta-estudio'
}

diccionarioPorcentajeDescuento = { # Relacionado al porcentaje de descuento por cada inmueble al valor a pagar de arrendatario
    '1' : 13,
    '2' : 12,
    '3' : 12.5,
    '4' : 10,
    '5' : 9,
    '6' : 8,
}

diccionarioBancos = {
    'None': 'None',
    'Bancolombia':'https://www.bancolombia.com/personas',
    'Davivienda':'https://www.davivienda.com/wps/portal/personas/nuevo',
    'Bogotá':'https://digital.bancodebogota.co/credito/index.html?&&gad_source=1&gclid=Cj0KCQjw_-GxBhC1ARIsADGgDjs2iaREWFvmN9HHQwW1XP2FedHJAy8UbC0GZaPn_b9V-Su31VwBI_caAn_AEALw_wcB',
    'Popular': 'https://www.bancopopular.com.co/wps/portal/bancopopular/inicio/para-ti/productos-ahorro-inversion/cuentas-ahorro/cuenta-para-ahorrar?utm_source=google&utm_medium=CAH-PRS&utm_campaign=renovacionkvabril-performance-performancemx-CPA-2024-mayo&utm_content=cuentaahorrar&gad_source=1&gclid=Cj0KCQjw_-GxBhC1ARIsADGgDjvLTm4_cc8X9j7ChblFhEoHOwu1j0sc1JTJajH6hwOp1cDvbmODYpMaArT1EALw_wcB',
    'Colpatria':'https://www.scotiabankcolpatria.com',
    'Agrario':'https://www.bancoagrario.gov.co',
    'Social':'https://www.bancocajasocial.com',
    'Falabella':'https://www.bancofalabella.com.co/page/banco-de-los-gennials?utm_source=sem&utm_medium=cpc&utm_campaign=INI_search_branding&utm_content=text-ad-N1-kw-banco&gad_source=1&gclid=Cj0KCQjw_-GxBhC1ARIsADGgDjunqRYs2JELpJfa9_v_RrPH9frzUCvdf3yhn068F_0q63ztlYWOqUwaArTOEALw_wcB&gclsrc=aw.ds',
    'BBVA':'https://www.bbva.com.co',
    'Nequi':'https://www.nequi.com.co',
    'Daviplata':'https://comunicaciones.davivienda.com/meter-plata?elqTrackId=9cdb82949cfe47d38761d16836421ae4',
    'Movii':'https://www.movii.com.co',
    'Tpaga':'https://tpaga.co',
    'Nubank':'https://nu.com.co/cf/cuenta/',
    'PayPal':'https://www.paypal.com/co/home',
}
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Creación de funciones que se van a usar en la app.

#------------Creo el decorador para restringir las vistas sin haber autenticado el usuario----------------------------------------------s
def autenticado_required(view_func):
    def verificacion(request, *args, **kwargs):
        if not request.session.get("estado_sesion"):
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return verificacion
#---------------------------------------------------------------------------------------------------------------------------------------


#------------Función para actualizar los estados de pago de propietarios e inquilinos automaticamente-----------------------------------
fecha = datetime.now()
def  actualizar_estados():
    global fecha
    fechaFormateada = fecha.strftime("%Y-%m-%d")
    ObjetoPago = inmueble.objects.filter(arrendatario_id__isnull=False)
    days = 365
    for objeto in ObjetoPago:
        #-----------------------Propietario-----------------------
        idPropietario = objeto.propietario_id.id
        EstadoPropietario = objeto.propietario_id.habilitarPago
        fechaPago = objeto.propietario_id.fecha_pago
        fechaPagoFormateada = fechaPago.strftime("%Y-%m-%d")

        fechaObjeto1 = datetime.strptime(fechaFormateada, "%Y-%m-%d")
        fechaObjeto2 = datetime.strptime(fechaPagoFormateada, "%Y-%m-%d")

        fechaResta = (fechaObjeto2 - fechaObjeto1).days
        # print(objeto.propietario_id.usuarios_id.nombre)
        # print("fecha 1: " + str(fechaObjeto1))
        # print("fecha 2: " + str(fechaObjeto2))
        # print("resta: " + str(fechaResta))
        guardar = propietario.objects.get(id=idPropietario)

        if fechaObjeto2 > fechaObjeto1: 
            if EstadoPropietario == 4 and fechaResta <=7:
                guardar.habilitarPago = 2
                guardar.save()
        elif fechaObjeto1 >= fechaObjeto2:
            guardar.habilitarPago = 3
            guardar.save()
        #-----------------------Arrendatario-----------------------
        idArrendatario = objeto.arrendatario_id.id
        EstadoArrendatario = objeto.arrendatario_id.habilitarPago
        inicio = objeto.arrendatario_id.inicio

        nuevaFecha = inicio + timedelta(days=days)
        fechaInicio = nuevaFecha.strftime('%Y-%m-%d') #mirar como se puede manejar una alerta o una vista, donde se visualice los arrendatarios que estan proximos a cumplir el año (Esta variable ya calcula cuando cumple el año.)

        fechaInicioCobro = objeto.arrendatario_id.fecha_inicio_cobro
        fechaInicioCobroFormateada = fechaInicioCobro.strftime("%Y-%m-%d")
        fechaFinCobro = objeto.arrendatario_id.fecha_fin_cobro
        fechaFinCobroFormateada = fechaFinCobro.strftime("%Y-%m-%d")

        fechaObjeto3 = datetime.strptime(fechaInicioCobroFormateada, "%Y-%m-%d")
        fechaObjeto4 = datetime.strptime(fechaFinCobroFormateada, "%Y-%m-%d")

        objetoArrendatario = arrendatario.objects.get(id=idArrendatario)
        if fechaObjeto1 >= fechaObjeto3 and fechaObjeto1 <= fechaObjeto4:
            objetoArrendatario.habilitarPago = 2
            print(objetoArrendatario.usuarios_id.nombre + objetoArrendatario.usuarios_id.apellido)
            print("fechaa en debe")
            objetoArrendatario.save()
        elif fechaObjeto1 > fechaObjeto4:
            objetoArrendatario.habilitarPago = 3
            print(objetoArrendatario.usuarios_id.nombre + objetoArrendatario.usuarios_id.apellido )
            print("fechaa no pago")
            objetoArrendatario.save()

    inicioContrato = objeto.arrendatario_id.inicio_contrato
    finContrato = objeto.arrendatario_id.fin_contrato
    return print(fechaFormateada)
#---------------------------------------------------------------------------------------------------------------------------------------


#-------------------------------------------Función para sacar los números de una lista mixta.------------------------------------------s
def extract_numbers(lst): #
    pattern = re.compile(r'\d+')# Compila un patrón de expresión regular para coincidir con dígitos
    extracted_numbers = [pattern.findall(s) for s in lst]# Usa el patrón para extraer todos los dígitos de cada cadena en la lista
    return [int(x) for sublist in extracted_numbers for x in sublist]# Convierte los números extraídos de strings a enteros
#---------------------------------------------------------------------------------------------------------------------------------------s


#-------------------------------------------Función para transformar la hora (No lo se muy bien)----------------------------------------s
def convert_time(horaRes):
    horaRes = horaRes.strip().replace(".","")
    try:
        hour = datetime.strptime(horaRes, "%I:%M %p")
    except ValueError:
        hour = datetime.strptime(horaRes, "%I:%M %p.")
    hora = hour.strftime("%H:%M")
    return hora
#---------------------------------------------------------------------------------------------------------------------------------------s

