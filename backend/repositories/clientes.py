from backend.database.connection import get_connection

def listar_clientes():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM clientes ORDER BY nombre COLLATE NOCASE").fetchall()

def crear_cliente(nombre, telefono, tipo_cliente, fecha):
    with get_connection() as conn:
        cursor = conn.execute("""INSERT INTO clientes
            (nombre, telefono, tipo_cliente, ultima_visita, total_gastado,
             visitas_totales, fecha_registro)
            VALUES (?, ?, ?, ?, 0, 0, ?)""",
            (nombre, telefono, tipo_cliente, fecha, fecha))
        return cursor.lastrowid
