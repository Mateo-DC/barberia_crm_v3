from backend.database.connection import get_connection

def listar_ventas():
    with get_connection() as conn:
        return conn.execute("""SELECT v.id, v.monto, v.fecha, v.campana_asociada, v.servicio,
            c.id AS cliente_id, c.nombre, c.tipo_cliente
            FROM ventas v JOIN clientes c ON c.id = v.cliente_id
            ORDER BY v.fecha DESC, v.id DESC""").fetchall()

def registrar_venta(cliente_id, monto, fecha, campana, servicio="Servicio general"):
    if monto <= 0:
        raise ValueError("El importe debe ser mayor que cero.")
    with get_connection() as conn:
        if not conn.execute("SELECT id FROM clientes WHERE id = ?", (cliente_id,)).fetchone():
            raise ValueError("El cliente no existe.")
        conn.execute("""INSERT INTO ventas
            (cliente_id, monto, fecha, campana_asociada, servicio) VALUES (?, ?, ?, ?, ?)""",
            (cliente_id, monto, fecha, campana, servicio))
        # Registrar un servicio no implica una visita adicional: las asistencias
        # se cuentan únicamente desde el formulario de visitas.
        conn.execute("UPDATE clientes SET total_gastado = total_gastado + ? WHERE id = ?",
                     (monto, cliente_id))
