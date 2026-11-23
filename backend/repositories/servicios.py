"""Catálogo local de servicios prestados. Sin dependencias externas."""
from backend.database.connection import get_connection


def listar_servicios():
    with get_connection() as conn:
        return conn.execute('SELECT * FROM servicios ORDER BY activo DESC, nombre COLLATE NOCASE').fetchall()


def guardar_servicio(nombre: str, precio: float, servicio_id: int | None = None):
    if not nombre.strip() or precio < 0:
        raise ValueError('Nombre y precio válidos son obligatorios.')
    with get_connection() as conn:
        if servicio_id is None:
            conn.execute('INSERT INTO servicios(nombre, precio) VALUES (?,?)', (nombre.strip(), precio))
        else:
            result = conn.execute('UPDATE servicios SET nombre=?, precio=? WHERE id=?',
                                  (nombre.strip(), precio, servicio_id))
            if not result.rowcount:
                raise ValueError('Servicio inexistente.')


def alternar_servicio(servicio_id: int):
    with get_connection() as conn:
        conn.execute('UPDATE servicios SET activo=1-activo WHERE id=?', (servicio_id,))
