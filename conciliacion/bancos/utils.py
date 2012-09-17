def get_row(row):
    dic = {
           'fecha':row.fecha,
           'cuenta':row.cuenta,
           'documento':row.documento,
           'estado':"" if row.conciliado else "Flotante",
           'beneficiario':row.beneficiario,
           'descripcion':row.descripcion,
           'montoC':abs(row.monto) if row.cuenta.moneda == "C$" else "",
           'montoD':abs(row.monto) if row.cuenta.moneda == "US$" else "",
           'tc':row.tc,
           'monto_cordobizado':row.monto_cordobizado,
           'monto':row.monto,
           'flotante':row.flotante                                
           }
    return dic