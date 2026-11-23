from datetime import date, timedelta
from backend.database.connection import get_connection

def seed_demo_data():
    hoy = date.today()
    ejemplos = [
        ("Carlos Gómez", "51987654321", "VIP", 4, 12),
        ("Juan Pérez", "51987654322", "Frecuente", 12, 8),
        ("Luis Hernández", "51987654323", "Inactivo", 48, 4),
        ("Mateo Rodríguez", "51987654324", "Esporádico", 25, 3),
        ("Sofía Martínez", "51987654325", "Frecuente", 7, 6),
        ("Diego Torres", "51987654326", "Inactivo", 62, 2),
        ("Andrés Silva", "51987654327", "Nuevo", 2, 1),
        ("Gabriel López", "51987654328", "VIP", 9, 10),
    ]
    with get_connection() as conn:
        if conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]:
            return
        for nombre, telefono, tipo, dias, visitas in ejemplos:
            ultima = (hoy - timedelta(days=dias)).isoformat()
            conn.execute("""INSERT INTO clientes
                (nombre, telefono, tipo_cliente, ultima_visita, total_gastado,
                 visitas_totales, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (nombre, telefono, tipo, ultima, visitas * 35.0, visitas, hoy.isoformat()))
            cliente_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            for i in range(min(visitas, 4)):
                fecha = (hoy - timedelta(days=i * 9 + dias)).isoformat()
                campana = ["Sin campaña", "Promo WhatsApp 15%",
                           "Publicidad general", "Reactivación de inactivos"][i % 4]
                conn.execute("""INSERT INTO ventas
                    (cliente_id, monto, fecha, campana_asociada)
                    VALUES (?, ?, ?, ?)""", (cliente_id, 35.0, fecha, campana))
                conn.execute("""INSERT INTO asistencias(cliente_id, fecha, nota)
                    VALUES (?, ?, 'Importada de una venta de demostración')""", (cliente_id, fecha))
