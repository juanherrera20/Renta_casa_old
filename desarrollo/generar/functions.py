#--------------------------------------------------------------------------------------------------------------------------------s
#En este archivo se registran todas las funciones y diccionarios que usamos para manejar la logica del backend.
#--------------------------------------------------------------------------------------------------------------------------------s

from datetime import date,timedelta, datetime
from dateutil.relativedelta import relativedelta
import re, math
from django.shortcuts import redirect
from .models import  tareas, inmueble, arrendatario, propietario
from xhtml2pdf import pisa
from io import BytesIO
from django.http import FileResponse
from django.template.loader import get_template


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

#-----------------------------------------------------Variables Globales para los calculos----------------------------------------------s
#Variables Globales para los calculos
fecha = date.today()
#---------------------------------------------------------------------------------------------------------------------------------------

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Creación de funciones que se van a usar en la app.

#------------Creo el decorador para restringir las vistas sin haber autenticado el usuario----------------------------------------------s
def autenticado_required(view_func):
    def verificacion(request, *args, **kwargs):
        if not request.session.get("estado_sesion"):
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return verificacion
#---------------------------------------------------------------------------------------------------------------------------------------s


#------------Función para actualizar los estados de pago de propietarios e inquilinos automaticamente-----------------------------------s

#No uso variable datetime.datetime si no una datetime.date que solo da el día y no las horas y segundos, esto permite poder hacer comparaciones con las fechas de la base de datos
def  actualizar_estados_propietarios():
    global fecha
    ObjetoPago = inmueble.objects.filter(arrendatario_id__isnull=False)
    fechaObjeto1 = fecha  #Fecha actual
    for objeto in ObjetoPago:
        #-----------------------Propietario-----------------------
        propietario = objeto.propietario_id  #Obtener los objetos con las relaciones Ahorra busquedas
        EstadoPago = objeto.estadoPago
        fecha_propietario = propietario.fecha_pago
        fecha_inmueble = objeto.fechaPago

        fechaResta = (fecha_inmueble - fechaObjeto1).days
        
        if fecha_inmueble >= fechaObjeto1: 
            if (EstadoPago in [1, 4]) and fechaResta <=7: #La fecha de pago es el ultimo día habil para pagar
                objeto.estadoPago = 2
                objeto.save()
                
        elif fechaObjeto1 > fecha_propietario and EstadoPago not in [1,3]: #Si el estado es pagado no debería cambiarse a no pago
            objeto.estadoPago = 3
            objeto.save()
    return None 

def  actualizar_estados_arrendatarios():
    global fecha
    ObjetoPago = inmueble.objects.filter(arrendatario_id__isnull=False)
    fechaObjeto1 = fecha  #Fecha actual
    for objeto in ObjetoPago:
        #-----------------------Arrendatario-----------------------
        objetoArrendatario = objeto.arrendatario_id #Obtener los objetos con las relaciones
        EstadoArrendatario = objeto.arrendatario_id.habilitarPago
        
        fechaInicioCobro = objeto.arrendatario_id.fecha_inicio_cobro
        fechaFinCobro = objeto.arrendatario_id.fecha_fin_cobro
        
        if fechaObjeto1 >= fechaInicioCobro and fechaObjeto1 <= fechaFinCobro and (EstadoArrendatario in [1, 4]): #De esta manera compruebo que no actualice el estado si es el mismo
            objetoArrendatario.habilitarPago = 2
            objetoArrendatario.save()  #Se usa pagar() que no se actualicen las fechas de inmuebles

        elif fechaObjeto1 > fechaFinCobro and (EstadoArrendatario not in [1,3]) : #De esta manera compruebo que no actualice el estado si es el mismo
            objetoArrendatario.habilitarPago = 3
            objetoArrendatario.save()
        
    return None

#Calcular por día el atraso de un pago para incrementar el valor (Faltan cosas)
def calcular_monto_atraso(objeto):
    global fecha
    porcentaje_penalizacion = 0.05  #Este es el porcentaje definido para el mora (Puede cambiar)
    
    #Saco los datos necesarios
    obj_arrendatario = objeto.arrendatario_id
    fecha_limite = obj_arrendatario.fecha_fin_cobro
    canon = objeto.canon
    
    if obj_arrendatario.habilitarPago == 3:
        #El monto y día de atraso se calculan desde la primera fecha de atraso, así luego se acumulen meses completos estos valores siempre se deberan calcular
        dias_atraso = (fecha - fecha_limite).days
        monto_atraso = canon / 30 * porcentaje_penalizacion * dias_atraso  
        
        for i in range(1,7): #un rango de 6 meses que representa la cantidad de meses posiblemente maximos para un atraso
            fecha_limitex = fecha_limite + relativedelta(months = i) #Calculo las fechas hipoteticas donde debería volver a pagar el siguiente mes
            fecha_iniciox = fecha_limitex - relativedelta(days= 5)
            
            if fecha <= fecha_limitex:  #Si la fecha hipotetica es menor significa que no a excedido el siguiente mes de pago, por ende no es necesario seguir ejecutando el for
                
                if fecha >= fecha_iniciox: #Si esta en las fechas de pago del mes hipotetico, el canon debe ser uno mas
                    meses = i + 1
                else: 
                    meses = i
                break #Rompo el ciclo
            
            dias_atrasox = (fecha - fecha_limitex).days  #Calculo dias de atraso basados en las nuevas fechas hipoteticas, para un mora extra por otro mes de atraso
            monto_atrasox = canon / 30 * porcentaje_penalizacion * dias_atrasox

            monto_atraso += monto_atrasox
           
    else:
        monto_atraso = 0
        dias_atraso = 0
        meses = 1

    monto_atraso = round(monto_atraso,0)
    
    return monto_atraso, dias_atraso, meses

#---------------------------------------------------------------------------------------------------------------------------------------s

#------------------Actualizar las tareas(Cuando estan en Pendiente y se pasan de la fecha, se pasan a incompletas)----------------------s
def actualizar_tareas():
    fechaObjeto1 = fecha
    tareas_pendientes = tareas.objects.filter(estado='Pendiente', fecha_fin__lte=fechaObjeto1)
    updates = [(obj.id, 'Incompleta') for obj in tareas_pendientes]
    if updates:
        instances_to_update = [tareas(id=id, estado=new_state) for id, new_state in updates]
        tareas.objects.bulk_update(instances_to_update, ['estado'])
    return None
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


#-------------------------------------------Función para transformar la hora------------------------------------------------
def convert_time(horaRes):
    horaRes = horaRes.strip().replace(".","")
    try:
        hour = datetime.strptime(horaRes, "%I:%M %p")
    except ValueError:
        hour = datetime.strptime(horaRes, "%I:%M %p.")
    hora = hour.strftime("%H:%M")
    return hora
#---------------------------------------------------------------------------------------------------------------------------------------s

#--------------------------------------------Función para renderizar los pdf de propietario-------------------------------------------------------------------------------------------s
def render_pdf( template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), dest=result)
    if not pdf.err:
        result.seek(0)
        return result
    return None
#---------------------------------------------------------------------------------------------------------------------------------------s

#-----------------------------------------------Función para renderizar el pdf de Arrendatario----------------------------------------------------------------------
def render_pdf_arr( template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), dest=result)
    if not pdf.err:
        result.seek(0)
        return FileResponse(result, as_attachment=True, filename='Factura-Arrendatario.pdf')
    return None
#---------------------------------------------------------------------------------------------------------------------------------------s