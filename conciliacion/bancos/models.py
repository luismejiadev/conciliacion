# -*- coding: UTF-8 -*-
from django.db import models

class CuentaBancaria(models.Model):
    MONEDAS = (
               ('C$','Cordobas'),
               ('US$','Dolares')
               )
    id = models.IntegerField(primary_key=True)
    banco = models.CharField(max_length=30)
    numero = models.CharField(max_length=100)
    moneda = models.CharField(choices = MONEDAS,max_length=3)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
            
    def __unicode__(self):
        return u"{0} {1} ( {2} )".format(self.banco,self.moneda,self.numero)
    


class Movimiento(models.Model):
    cuenta = models.ForeignKey(CuentaBancaria)
    fecha = models.DateField()
    documento = models.CharField(null=False, blank=False, max_length=100)
    descripcion = models.TextField(null=False, blank=False)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    conciliado = models.BooleanField(default=False)
    tipo = models.CharField(null=True, blank=True, max_length=4)
    @property
    def monto_cordobizado(self):
        if self.cuenta.moneda == "C$":
            monto = abs(self.monto)
        else:
            try:
                monto = abs(self.monto) * self.tc
            except Exception as e:
                monto = "" 
        return monto
    
    def flotante(self):
        return -self.monto
    
    class Meta:
        abstract=True
    
        
class MovimientoLibro(Movimiento):
    beneficiario = models.CharField(null=False, blank=False, max_length=100)
    tc = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __unicode__(self):
        return u"fecha: %s | doc: %s | monto: %s | %s"%(self.fecha, self.documento,self.monto,self.descripcion.replace("\n"," ")[:40])
    
    class Meta:
        ordering = ['fecha','id']
        verbose_name_plural=" Movimientos Segun Libro"

    
class MovimientoBanco(Movimiento):
    saldo = models.DecimalField(max_digits=12, decimal_places=2)    
    movimiento = models.ForeignKey(MovimientoLibro,null=True,blank=True)
    
    def __unicode__(self):
        return u"fecha: %s | doc: %s | monto: %s | %s"%(self.fecha, self.documento,self.monto,self.descripcion.replace("\n"," ")[:40])
    
    class Meta:
        ordering = ['fecha','id']
        verbose_name_plural=" Movimientos Segun Banco"

    @property
    def beneficiario(self):
        return ""

    @property
    def tc(self):
        return ""
        
    def save(self, force_insert=False, force_update=False, using=None):
        if self.movimiento is not None and self.monto is None:
            self.cuenta = self.movimiento.cuenta
            self.conciliado = True
            self.monto = self.movimiento.monto
            self.descripcion = self.movimiento.descripcion
            self.documento = self.movimiento.documento
                        
        super(MovimientoBanco,self).save(force_insert=False, force_update=False, using=None)

    def flotante(self):
        return self.monto        