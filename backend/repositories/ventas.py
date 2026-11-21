from backend.database.connection import get_connection

def listar_ventas():
    with get_connection() as conn:
        return conn.execute("""SELECT v.id, v.monto, v.fecha, v.campana_asociada,
            c.id AS cliente_id, c.nombre, c.tipo_cliente
            FROM ventas v JOIN clientes c ON c.id = v.cliente_id
            ORDER BY v.fecha DESC, v.id DESC""").fetchall()

def registrar_venta(cliente_id, monto, fecha, campana):
    if monto <= 0:
        raise ValueError("El importe debe ser mayor que cero.")
    with get_connection() as conn:
        if not conn.execute("SELECT id FROM clientes WHERE id = ?", (cliente_id,)).fetchone():
            raise ValueError("El cliente no existe.")
        conn.execute("""INSERT INTO ventas
            (cliente_id, monto, fecha, campana_asociada) VALUES (?, ?, ?, ?)""",
            (cliente_id, monto, fecha, campana))
        conn.execute("""UPDATE clientes SET ultima_visita = ?,
            total_gastado = total_gastado + ?,
            visitas_totales = visitas_totales + 1 WHERE id = ?""",
            (fecha, monto, cliente_id))
