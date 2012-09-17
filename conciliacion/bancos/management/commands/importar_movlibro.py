# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
import logging
from conciliacion.bancos.models import CuentaBancaria,\
    MovimientoLibro
from decimal import Decimal
import datetime

FORMAT = '%(levelname)s:%(asctime)s:%(message)s'
logging.basicConfig(filename='logs/movimientos.log',level=logging.INFO,format = FORMAT)

def limpiar_monto(monto):
    monto = monto.replace(",","")
    monto = monto.replace(" ","")
    return Decimal(monto)

class Command(BaseCommand):
    @transaction.commit_manually
    def handle(self, file_path, *args, **options):        
        try:
            logging.info('>>>>>>>>>>>>>>>>>>>>>>>>')
            
            with open(file_path, mode='r') as file_handle:
                lines = file_handle.readlines()
                
            logging.info('Abierto archivo %s',file_path)
            
            for line in lines:
                logging.info("procesando %s"%line)
                values = line.split(",")
                cuenta = None                
                if "/" in values[0]:
                    
                    logging.info(values)
                    fecha = datetime.datetime.strptime(values[0],'%d/%m/%Y')
                    #values[1] vacio , correspondel al # de cuenta
                    documento = values[2]
                    estado = values[3]
                    beneficiario = u"%s"%values[4].encode('UTF-8')
                    descripcion =u"%s"% values[5].encode('UTF-8')
                    montoC = Decimal(values[6]) if values[6] != "" or values[6] == "\n" else Decimal('0.00')
                     
                    montoD = Decimal(values[7]) if values[7] != "" or values[7] == "\n"  else Decimal('0.00')
                    tc = Decimal(values[8]) if values[8] != "" or values[8] == "\n"  else Decimal('0.00')
        
                    valor_cuenta = ""  
                    this = None                 
                    for pos in range(10,len(values)):
                        if values[pos] != "" or values[pos] == "\n":
                            i =pos - 9
                            try:                             
                                valor_cuenta = Decimal(values[pos])
                            except:
                                valor_cuenta = ""

                            if valor_cuenta != "":
                                cuenta = CuentaBancaria.objects.get(pk=i)                            
                                this=MovimientoLibro(
                                    fecha=fecha,
                                    documento=documento,
                                    beneficiario=beneficiario, 
                                    descripcion = descripcion,
                                    monto=valor_cuenta,
                                    cuenta = cuenta,
                                    tc=tc
                                    ).save()                                                        
                                logging.info(this)                                                                    
                                print documento,valor_cuenta , montoD, montoC, cuenta,descripcion
                    if this is None:                            
                        logging.warning(u"el documento %s no fue guardado"%documento)                                
                                                    
        except Exception as e:
            logging.exception(e)            
            transaction.rollback()
        else:
            transaction.commit()
            logging.info("Movimientos creados exitosamente")
            print ("Movimientos creados exitosamente")
            logging.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                    
            
            