# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from core.models import TipoCambio, Moneda
import datetime
from django.db import transaction
from contabilidad.models import MESES
from suds.client import Client

class Command(BaseCommand):
    help = 'Importar tipos de cambios del banco central para el mes actual'
    
    @transaction.commit_manually
    def handle(self, *args, **options):
        
        try:            
            year = int(args[0] if len(args) > 0 else datetime.date.today().year)
            month = int(args[1] if len(args) > 1 else datetime.date.today().month)
            client = Client('https://servicios.bcn.gob.ni/Tc_Servicio/ServicioTC.asmx?WSDL')
            moneda = Moneda.objects.get(pk=2)
            data = client.service.RecuperaTC_Mes(year,month)['Detalle_TC'][0]
    
            for record in data:
                fecha = record['Fecha']
                base = record['Valor']
                tipo  = TipoCambio.objects.create(moneda=moneda,fecha=fecha, base = base)
                print "*************************"
                print base
                print fecha
                print "*************************"
                tipo.save()        
            
    
        except Exception as inst:
            print u"No se pudieron importar los Tipos de Cambios para el mes de  %s-%d" % (  MESES[month][1], year)            
            transaction.rollback()
            print unicode(inst)
        else:
            transaction.commit()
            print u"Tipos de Cambios Importados exitosamente para el mes de  %s-%d" % (  MESES[month][1], year)
                    
        

        

    