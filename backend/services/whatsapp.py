import re
from urllib.parse import quote

def limpiar_telefono(telefono):
    return re.sub(r"\D", "", str(telefono or ""))

def generar_enlace(telefono, mensaje):
    numero = limpiar_telefono(telefono)
    if not numero:
        raise ValueError("El teléfono no es válido.")
    return f"https://wa.me/{numero}?text={quote(mensaje)}"

def personalizar_mensaje(plantilla, nombre, dias):
    try:
        return plantilla.format(nombre=nombre, dias=dias)
    except (KeyError, ValueError, IndexError) as error:
        raise ValueError("Usa únicamente {nombre} y {dias}.") from error
