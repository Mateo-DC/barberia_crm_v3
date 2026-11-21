from datetime import date, datetime

def dias_desde_ultima_visita(fecha):
    if not fecha:
        return 9999
    try:
        ultima = datetime.strptime(fecha, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return 9999
    return max((date.today() - ultima).days, 0)

def filtrar_clientes(clientes, tipos, dias_minimos, busqueda=""):
    termino = busqueda.strip().casefold()
    resultado = []
    for cliente in clientes:
        dias = dias_desde_ultima_visita(cliente["ultima_visita"])
        if cliente["tipo_cliente"] not in tipos or dias < dias_minimos:
            continue
        if termino and termino not in cliente["nombre"].casefold() and termino not in cliente["telefono"]:
            continue
        resultado.append((cliente, dias))
    return resultado
