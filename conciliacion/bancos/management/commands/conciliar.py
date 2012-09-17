# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
import logging
from conciliacion.bancos.models import MovimientoBanco, CuentaBancaria,\
    MovimientoLibro
from decimal import Decimal
import datetime

FORMAT = '%(levelname)s:%(asctime)s:%(message)s'
logging.basicConfig(filename='logs/conciliacion.log',level=logging.INFO,format = FORMAT)

def limpiar_monto(monto):
    monto = monto.replace(",","")
    monto = monto.replace(" ","")
    return Decimal(monto)

class Command(BaseCommand):
    @transaction.commit_manually
    def handle(self, *args, **options):        
        try:
            logging.info('>>>>>>>>>>>>>>>>>>>>>>>>')
            for mov in MovimientoLibro.objects.filter(conciliado=False):
                lineas = MovimientoBanco.objects.filter(
                       cuenta=mov.cuenta,
                       documento=mov.documento,
                       movimiento__isnull=True,
                       fecha__month=mov.fecha.month,
                       fecha__year=mov.fecha.year,
                       monto=mov.monto
                       )
                logging.info("Movimiento por documento")
                logging.info(mov)       
                logging.info(lineas)
                print(lineas)           
                     
                lineas.update(conciliado=True,movimiento=mov)
                
                
                lineas = MovimientoBanco.objects.filter(
                       cuenta=mov.cuenta,
                       descripcion=mov.descripcion,
                       fecha__month=mov.fecha.month,
                       fecha__year=mov.fecha.year,
                       movimiento__isnull=True,
                       monto=mov.monto
                       )
                
                logging.info("Movimiento por descripcion y fecha")
                logging.info(mov)       
                logging.info(lineas)
                print(lineas)
                lineas.update(conciliado=True,movimiento=mov)
                
                
                mov.conciliado = len(mov.movimientobanco_set.all()) >0
                mov.save()
                                
                                                                               
        except Exception as e:
            logging.exception(e)            
            transaction.rollback()
        else:
            transaction.commit()
            logging.info("conciliacion finalizada exitosamente")
            print ("conciliacion finalizada exitosamente")
            logging.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                    
            
            