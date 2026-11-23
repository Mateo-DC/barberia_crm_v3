from backend.database.connection import get_connection

def listar_clientes():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM clientes ORDER BY nombre COLLATE NOCASE").fetchall()

def obtener_cliente(cliente_id: int):
    with get_connection() as conn:
        return conn.execute('SELECT * FROM clientes WHERE id=?', (cliente_id,)).fetchone()


def actualizar_cliente(cliente_id: int, nombre: str, telefono: str, tipo_cliente: str):
    with get_connection() as conn:
        result = conn.execute('UPDATE clientes SET nombre=?, telefono=?, tipo_cliente=? WHERE id=?',
                              (nombre, telefono, tipo_cliente, cliente_id))
        return bool(result.rowcount)


def crear_cliente(nombre, telefono, tipo_cliente, fecha):
    with get_connection() as conn:
        cursor = conn.execute("""INSERT INTO clientes
            (nombre, telefono, tipo_cliente, ultima_visita, total_gastado,
             visitas_totales, fecha_registro)
            VALUES (?, ?, ?, ?, 0, 0, ?)""",
            (nombre, telefono, tipo_cliente, fecha, fecha))
        return cursor.lastrowid
