# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, ModelMultipleChoiceField, ModelChoiceField
from django.contrib import admin as admin_module
from django.forms.util import ErrorList
from conciliacion.bancos.models import MovimientoBanco, MovimientoLibro,\
    CuentaBancaria
from decimal import Decimal
from conciliacion.bancos.templatetags.porcentaje import moneyfmt

class MovimientoLibroForm (ModelForm):            
    movimiento_banco = ModelChoiceField(
                    label='Lineas de Estado Bancario',
                    queryset=MovimientoBanco.objects.filter(conciliado=False,
                                                                movimiento__isnull=True
                                                                ),
                    required=False)            
    

    depositos = ModelMultipleChoiceField(
                    label='Depositos',
                    queryset=MovimientoBanco.objects.filter(conciliado=False,
                                                                movimiento__isnull=True,
                                                                descripcion__in=["DP","TF"]
                                                                ),
                    required=False)
    validar = forms.BooleanField(required=False,initial=True)
    
    class Meta:
        model = MovimientoLibro
        
    def clean(self):
        cleaned_data = super(MovimientoLibroForm,self).clean()
        
        if cleaned_data["validar"] and "depositos" in cleaned_data and len(cleaned_data['depositos']) > 0:
            depositos = cleaned_data['depositos']
            monto = Decimal("0.00")
            for d in depositos:
                monto += d.monto
            if monto != cleaned_data["monto"]:
                raise forms.ValidationError("Los depositos no coinciden, depositos:%s, diferencia: %s"%(moneyfmt(monto), moneyfmt(cleaned_data["monto"]- monto)))
            
        return cleaned_data        

class ReporteForm (forms.Form):
    ESTADOS = (
              ("","Todas"),
              ("True","Conciliado"),
              ("False","No conciliado")
              
              )
    conciliado = forms.ChoiceField(choices=ESTADOS,required=False)
    cuentas = forms.ModelMultipleChoiceField(queryset=CuentaBancaria.objects.all(),required=False)  