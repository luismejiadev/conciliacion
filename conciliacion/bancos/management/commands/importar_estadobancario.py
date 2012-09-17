# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
import logging
from conciliacion.bancos.models import MovimientoBanco, CuentaBancaria
from decimal import Decimal
import datetime

FORMAT = '%(levelname)s:%(asctime)s:%(message)s'
logging.basicConfig(filename='logs/estados_bancarios.log',level=logging.INFO,format = FORMAT)

def limpiar_monto(monto):
    monto = monto.replace(",","")
    monto = monto.replace(" ","")
    return Decimal(monto)

class Command(BaseCommand):
    @transaction.commit_manually
    def handle(self, file_path, cuenta, tipo, *args, **options):        
        try:
            logging.info('>>>>>>>>>>>>>>>>>>>>>>>>')

            with open(file_path, 'r') as file_handle:
                lines = file_handle.readlines()
            
            cuenta = CuentaBancaria.objects.get(pk=cuenta)
            if tipo =="BAC":
                for line in lines:
                    values = line.split("|")
                    if "/" in values[0]: 
                        MovimientoBanco(
                                                fecha=datetime.datetime.strptime(values[0],'%d/%m/%Y'),
                                                documento=values[1],
                                                tipo=values[2], 
                                                descripcion = values[3],
                                                monto=limpiar_monto(values[4]) * -1 if values[4] != '0' else limpiar_monto(values[5]),
                                                saldo = limpiar_monto(values[6]),
                                                cuenta = cuenta
                                                ).save()
                        logging.info(line)                
                        print line
            else:                            
                for line in lines:
                    fecha, documento,descripcion,monto,saldo= line.split("|")
                    if "Saldo" not in fecha:
                        MovimientoBanco(
                                            fecha=datetime.datetime.strptime(fecha,'%d/%m/%Y'),
                                            documento=documento,
                                            descripcion=descripcion,
                                            monto=limpiar_monto(monto),
                                            saldo = limpiar_monto(saldo),
                                            cuenta = cuenta
                                            ).save()
                                    
                        logging.info(line)
                        print line
                
                                                    
        except Exception as e:
            logging.exception(e)            
            transaction.rollback()
            print "ocurrio un error"
        else:
            transaction.commit()
            logging.info("Movimientos creados exitosamente")
            print ("Movimientos creados exitosamente")
            logging.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                    
            
            