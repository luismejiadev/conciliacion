# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from conciliacion.bancos.models import CuentaBancaria, MovimientoLibro,\
    MovimientoBanco
from django.db.models.query_utils import Q
from conciliacion.bancos.forms import ReporteForm
from conciliacion.bancos.utils import get_row
from decimal import Decimal


def home(request,pk=""):
    
    cuentas = CuentaBancaria.objects.all().order_by("id")
    if request.POST:
        form = ReporteForm(request.POST) 
        q = Q()
        print request.POST
        if request.POST["conciliado"]=="False":
            q = Q(conciliado = False)
        elif request.POST["conciliado"]=="True":
            q = Q(conciliado = True)
            
        if "cuentas" in request.POST:        
            cuentas = cuentas.filter(pk__in=request.POST.getlist("cuentas"))
            q.add(Q(cuenta__in=cuentas), Q.AND)
        lineas = MovimientoLibro.objects.filter(q).order_by("fecha")        
    else:
        form = ReporteForm()  
        lineas = MovimientoLibro.objects.none()                      
    context = {
               'form':form,
                   'cuentas':cuentas,
                   'lineas':lineas
               }
    return render_to_response('index.html',context, RequestContext(request))

def flotantes(request,pk=""):
    
    cuentas = CuentaBancaria.objects.all().order_by("id")
    if request.POST:
        form = ReporteForm(request.POST) 
        q = Q(conciliado=False)
        print request.POST            
        if "cuentas" in request.POST:        
            cuentas = cuentas.filter(pk__in=request.POST.getlist("cuentas"))
            q.add(Q(cuenta__in=cuentas), Q.AND)
        lineas = []
        for r in MovimientoLibro.objects.exclude(
                                                   Q(beneficiario__contains="anulad") |
                                                   Q(monto=0)
                                                                                                      
                                                   ).filter(q):  
            lineas.append(get_row(r))
            
        for r in MovimientoBanco.objects.filter(q):  
            lineas.append(get_row(r))                  
    else:
        form = ReporteForm()  
        lineas = MovimientoLibro.objects.none()                      
    context = {
               'form':form,
                   'cuentas':CuentaBancaria.objects.all().order_by("id"),
                   'lineas':lineas
               }
    return render_to_response('flotantes.html',context, RequestContext(request))