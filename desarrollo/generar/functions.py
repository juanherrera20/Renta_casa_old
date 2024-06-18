#--------------------------------------------------------------------------------------------------------------------------------s
#En este archivo se registran todas las funciones y diccionarios que usamos para manejar la logica del backend.
#--------------------------------------------------------------------------------------------------------------------------------s

from datetime import date,timedelta, datetime
from dateutil.relativedelta import relativedelta
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
    '4': 'Indefinido',
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
    'Efectivo':'Pago en efectivo'
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

#Calcular por día el atraso de un pago para incrementar el valor (Faltan cosas)
def calcular_monto_atraso(fecha_pago, porcentaje_penalizacion):
    fecha_actual = date.today()
    dias_atraso = (fecha_actual - fecha_pago).days
    if dias_atraso > 0:
        monto_atraso = porcentaje_penalizacion * dias_atraso
    else:
        monto_atraso = 0
    return monto_atraso

fecha = date.today()  
#No uso variable datetime.datetime si no una datetime.date que solo da el día y no las horas y segundos, esto permite poder hacer comparaciones con las fechas de la base de datos
def  actualizar_estados():
    global fecha
    ObjetoPago = inmueble.objects.filter(arrendatario_id__isnull=False)
    days = 365
    fechaObjeto1 = fecha  #Fecha actual
    for objeto in ObjetoPago:
        #-----------------------Propietario-----------------------
        propietario = objeto.propietario_id
        EstadoPago1 = jerarquia_estadoPago_propietario(propietario) #Equivalente al obtenido a la jerarquia
        EstadoPago2 = objeto.estadoPago
        # print(f"Estado propietario: {EstadoPago1}")
        # print(f"Estado propietario: {EstadoPago1}")
        fechaPago = objeto.propietario_id.fecha_pago
        
        if isinstance(fechaPago, date):
            fechaObjeto2 = fechaPago
        else:
            fecha_str = datetime.strptime(fechaPago, '%Y-%m-%d').date()
            fechaObjeto2 = fecha_str

        fechaResta = (fechaObjeto2 - fechaObjeto1).days

        if fechaObjeto2 >= fechaObjeto1: 
            
            """ Uso EstadoPago1 para evitar que mi estado de pago se cambie de "Pagado" a "debe" ya que si no se ha pagado todos los inmuebles de un propietario
                la fecha no aumenta y el siguiente condicional se cumpliría, y nos interesa que se cumpla solo cuando todo este pago"""
            if (EstadoPago1 == 1 or EstadoPago1 == 4) and fechaResta <=7: #La fecha de pago es el ultimo día habil para pagar
                objeto.estadoPago = 2
                objeto.save()
                
            """Aquí uso el EstadoPago2 ya que si uso el 1 los ya pagados se marcaran como "No pagos" si no se han pagado todos, de esta manera 
                el programa tomara el estado unico y no el ponderado de varios que siempre tiende a ser el peor"""
        elif fechaObjeto1 > fechaObjeto2 and EstadoPago2 != 1: #Si el estado es pagado no debería cambiarse a no pago
            objeto.estadoPago = 3
            objeto.save()
            
        #-----------------------Arrendatario-----------------------
        idArrendatario = objeto.arrendatario_id.id
        EstadoArrendatario = objeto.arrendatario_id.habilitarPago
        inicio = objeto.arrendatario_id.inicio
        
        #Esto es para verificar cuando cumple el año el arrendatarios
        nuevaFecha = inicio + timedelta(days=days)
        fechaInicio = nuevaFecha.strftime('%Y-%m-%d') #mirar como se puede manejar una alerta o una vista, donde se visualice los arrendatarios que estan proximos a cumplir el año (Esta variable ya calcula cuando cumple el año.)

        fechaInicioCobro = objeto.arrendatario_id.fecha_inicio_cobro
        fechaFinCobro = objeto.arrendatario_id.fecha_fin_cobro

        objetoArrendatario = arrendatario.objects.get(id=idArrendatario)  #Obtengo el objeto arrendatario 
        if fechaObjeto1 >= fechaInicioCobro and fechaObjeto1 <= fechaFinCobro and (EstadoArrendatario == 1 or EstadoArrendatario == 4):
            objetoArrendatario.habilitarPago = 2
            objetoArrendatario.save()
        
        elif fechaObjeto1 > fechaFinCobro and EstadoArrendatario != 1:
            objetoArrendatario.habilitarPago = 3
            objetoArrendatario.save()
            
        #print(objetoArrendatario.usuarios_id.nombre + objetoArrendatario.usuarios_id.apellido)
        
    # Calcular monto por atraso y aplicar lógica
    # porcentaje_penalizacion = 0.05
    # fecha_pago_arrendatario = objeto.arrendatario_id.fecha_fin_cobro
    # monto_atraso = calcular_monto_atraso(fecha_pago_arrendatario, porcentaje_penalizacion)

    # if monto_atraso > 0:
    #     # Aquí se tratara el tema de notificaciones y guardar el canon modificado en la base de datos o algo
    #     pass
        
    inicioContrato = objeto.arrendatario_id.inicio_contrato
    finContrato = objeto.arrendatario_id.fin_contrato
    #-----------------------Tareas-----------------------
    tareas_pendientes = tareas.objects.filter(estado='Pendiente', fecha_fin__lte=fechaObjeto1)
    updates = [(obj.id, 'Incompleta') for obj in tareas_pendientes]
    if updates:
        instances_to_update = [tareas(id=id, estado=new_state) for id, new_state in updates]
        tareas.objects.bulk_update(instances_to_update, ['estado'])
    return print(fecha)
#---------------------------------------------------------------------------------------------------------------------------------------


#-------------------------------------------Función para sacar los números de una lista mixta.------------------------------------------s
def extract_numbers(lst): #
    pattern = re.compile(r'\d+')# Compila un patrón de expresión regular para coincidir con dígitos
    extracted_numbers = [pattern.findall(s) for s in lst]# Usa el patrón para extraer todos los dígitos de cada cadena en la lista
    return [int(x) for sublist in extracted_numbers for x in sublist]# Convierte los números extraídos de strings a enteros
#---------------------------------------------------------------------------------------------------------------------------------------s

#-------------------------------------------Función para establecer la Jerarquia de los estados propietario.------------------------------------------s
def jerarquia_estadoPago_propietario(propietario):
    try:
        estado_no_pagado = propietario.inmueble.filter(estadoPago=3).exists()
        if estado_no_pagado:
            return 3  # 'No pago'
        
        estado_debe = propietario.inmueble.filter(estadoPago=2).exists()
        if estado_debe:
            return 2  # 'Debe'
        
        estado_pagado = propietario.inmueble.filter(estadoPago=1).exists()
        if estado_pagado:
            return 1  # 'Pagado'
        
        return 4  # 'Indefinido' u otro estado por defecto
    except Exception as e:
        print(f"Error al obtener el estado prioritario: {e}")
        return 4  # En caso de error, devolver 'Indefinido'
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

