from django import template
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings

register = template.Library()

@register.simple_tag
def sum_value(list,cuenta,decimal_places=2):
    value = Decimal(0)    
    try:
        for item in list:
            if item.cuenta == cuenta:
                value +=item.monto
    except:
        pass
    return moneyfmt(value,decimal_places, cuenta.moneda)

@register.filter
def decimal_format(value,simbolo):
    try:
        if value == '0':
            return value
        
        value = Decimal(str(round(value,settings.DECIMAL_PLACES)))
        return moneyfmt(value,settings.DECIMAL_PLACES,simbolo)
    except ValueError:
        return ''

def moneyfmt( value, places = 4, curr = '', sep = ',', dp = '.', pos = '', neg = '-', trailneg = '' ):
    q = Decimal( 10 ) ** -places      # 2 places --> '0.01'
    sign, digits, _exp = value.quantize( q,rounding=ROUND_HALF_UP ).as_tuple()
    result = []
    digits = map( str, digits )
    build, next = result.append, digits.pop
    if sign:
        build( trailneg )
    for _i in range( places ):
        build( next() if digits else '0' )
    if places > 0:
        build( dp )
    if not digits:
        build( '0' )
    i = 0
    while digits:
        build( next() )
        i += 1
        if i == 3 and digits:
            i = 0        
            build( sep )
    build( curr )
    build( neg if sign else pos )
    return ''.join( reversed( result ) )
    