# -*- coding: UTF-8 -*-
from django.contrib import admin
from models import CuentaBancaria, MovimientoBanco
from conciliacion.bancos.models import MovimientoLibro
from conciliacion.bancos.forms import MovimientoLibroForm
from decimal import Decimal
from django.db.models.query_utils import Q
from django.db import transaction

def marcar_conciliado(modeladmin, request, queryset):
    queryset.update(conciliado=True)
    
marcar_conciliado.short_description = "Marcar como conciliados"

@transaction.commit_manually
def conciliar_por_movimiento(modeladmin, request, queryset):
    for obj in queryset:
        mov = MovimientoBanco.objects.filter(
                             conciliado=False,
                            movimiento__isnull=True,
                            cuenta = obj.cuenta,
                            fecha__month=obj.fecha.month,
                            fecha__year=obj.fecha.year,
                            monto = obj.monto
                            )
        if len(mov) == 1:
            movimiento_banco = mov[0]
            movimiento_banco.movimiento=obj
            movimiento_banco.conciliado=True
            movimiento_banco.save()
                        
            obj.conciliado = True
            obj.save()
            
    transaction.commit()

            
    
     
conciliar_por_movimiento.short_description = "Conciliar por 1 movimiento"     

class CuentaBancariaAdmin (admin.ModelAdmin):
    fields = ['id','banco','numero','moneda','saldo_inicial']
    list_display = ['id','__unicode__','saldo_inicial']

class MovimientoBancoInLine (admin.TabularInline):
    model = MovimientoBanco
    exclude = ['cuenta','conciliado','descripcion','documento']
    readonly_fields = ['monto',]
    extra = 1

    

class MovimientoBancoAdmin (admin.ModelAdmin):
    date_hierarchy = 'fecha'
    list_display = ['fecha','movimiento','documento','cuenta','descripcion','monto','saldo','tipo']
    list_filter = ['cuenta','conciliado','tipo']
    actions = [marcar_conciliado]

class MovimientoLibroAdmin (admin.ModelAdmin):
    date_hierarchy = 'fecha'
    list_display = ['fecha','documento','cuenta','descripcion','monto','tipo']
    list_filter = ['cuenta','conciliado']
    inlines = [MovimientoBancoInLine,]
    form = MovimientoLibroForm
    actions = [marcar_conciliado,conciliar_por_movimiento]    
    
    def get_form(self, request, obj=None, **kwargs):

        cleaned_data = request.POST        
        if "documento" in cleaned_data and cleaned_data["documento"] == "" and \
            "descripcion" in cleaned_data and cleaned_data["descripcion"] == "" and \
            "cuenta" in cleaned_data and cleaned_data["cuenta"] == "" and \
            "monto" in cleaned_data and cleaned_data["monto"] == "" and \
            "movimiento_banco" in cleaned_data and cleaned_data["movimiento_banco"] != "" :
                linea =  MovimientoBanco.objects.get(pk=cleaned_data["movimiento_banco"])               
                request.POST.update({
                                     "documento": linea.documento,
                                     "descripcion": linea.descripcion,
                                     "cuenta": linea.cuenta.pk,
                                     "monto": linea.monto, 
                                     
                                     })
                        
        form = super(MovimientoLibroAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            form.base_fields['movimiento_banco'].queryset=MovimientoBanco.objects.filter(
                                                                 conciliado=False,
                                                                movimiento__isnull=True,
                                                                cuenta = obj.cuenta,
                                                                fecha__month=obj.fecha.month,
                                                                fecha__year=obj.fecha.year,
                                                                monto = obj.monto
                                                                )
            qs = MovimientoBanco.objects.filter(    
                                                    (Q(movimiento=obj) |
                                                                (Q(conciliado=False)&
                                                                Q(movimiento__isnull=True))) &
                                                                Q(cuenta = obj.cuenta) &
                                                                Q(fecha__month=obj.fecha.month) &
                                                                Q(fecha__year=obj.fecha.year) &
                                                                Q(monto__lt=15000 if obj.cuenta.moneda == "US$" else 1500) &
                                                                (
                                                                 Q(tipo__contains="DP") | 
                                                                 Q(tipo__contains="DC") |
                                                                 Q(tipo__contains="TF"
                                                                     ))                                               
                                                                )
            form.base_fields['depositos'].queryset=qs
            form.base_fields['depositos'].initial = [l.pk for l in MovimientoBanco.objects.filter(movimiento=obj)]
            
        else:
            form.base_fields['movimiento_banco'].queryset=MovimientoBanco.objects.filter(conciliado=False,
                                                                movimiento__isnull=True,
                                                                )                    
        return form
    
    @transaction.commit_manually    
    def save_model(self, request, obj, form, change):
        try:                
            super(MovimientoLibroAdmin, self).save_model(request, obj, form, change)
            if form.cleaned_data['movimiento_banco'] != None:
                movimiento_banco = form.cleaned_data['movimiento_banco']
                movimiento_banco.movimiento=obj
                movimiento_banco.conciliado=True
                movimiento_banco.save()
                obj.conciliado=True
                obj.save()
                
            if "depositos" in form.cleaned_data and len(form.cleaned_data['depositos']) > 0:
                depositos = form.cleaned_data['depositos']
                monto = Decimal('0.00')
                for d in depositos:
                    monto += d.monto
                    d.movimiento=obj
                    d.conciliado=True
                    d.save()
                    
                if monto == d.monto:
                    obj.conciliado=True
                    obj.save()
        except Exception as e:            
            transaction.rollback()
            raise e
        else:
            transaction.commit()

                    
                        
    

admin.site.register(CuentaBancaria,CuentaBancariaAdmin)
admin.site.register(MovimientoBanco,MovimientoBancoAdmin)
admin.site.register(MovimientoLibro,MovimientoLibroAdmin)
