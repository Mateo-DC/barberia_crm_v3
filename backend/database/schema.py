from backend.database.connection import get_connection


def init_db():
    """Create current schema and migrate older SQLite databases safely."""
    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT NOT NULL,
                tipo_cliente TEXT NOT NULL DEFAULT 'Nuevo',
                ultima_visita TEXT,
                total_gastado REAL NOT NULL DEFAULT 0,
                visitas_totales INTEGER NOT NULL DEFAULT 0,
                fecha_registro TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                monto REAL NOT NULL CHECK (monto > 0),
                fecha TEXT NOT NULL,
                campana_asociada TEXT NOT NULL DEFAULT 'Sin campaña',
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            );
            CREATE TABLE IF NOT EXISTS grupos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE COLLATE NOCASE,
                descripcion TEXT NOT NULL DEFAULT '',
                activo INTEGER NOT NULL DEFAULT 1,
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS clientes_grupos (
                cliente_id INTEGER NOT NULL,
                grupo_id INTEGER NOT NULL,
                PRIMARY KEY (cliente_id, grupo_id),
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS promociones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL DEFAULT '',
                premio TEXT NOT NULL DEFAULT '',
                meta_visitas INTEGER NOT NULL CHECK(meta_visitas > 0),
                modo_conteo TEXT NOT NULL CHECK(modo_conteo IN ('acumuladas','consecutivas')),
                repeticion TEXT NOT NULL CHECK(repeticion IN ('una_vez','recurrente')),
                tipo_objetivo TEXT NOT NULL CHECK(tipo_objetivo IN ('categoria','grupo','todos')),
                objetivo TEXT NOT NULL DEFAULT 'Todos',
                mensaje TEXT NOT NULL,
                activa INTEGER NOT NULL DEFAULT 1,
                fecha_inicio TEXT,
                fecha_fin TEXT,
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS asistencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                nota TEXT NOT NULL DEFAULT '',
                rompe_racha INTEGER NOT NULL DEFAULT 0,
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_asistencias_cliente_fecha ON asistencias(cliente_id, fecha, id);
            CREATE INDEX IF NOT EXISTS idx_promociones_activa ON promociones(activa);
            CREATE TABLE IF NOT EXISTS logros_promocion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                promocion_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                ronda INTEGER NOT NULL DEFAULT 1,
                asistencias_meta INTEGER NOT NULL,
                fecha_logro TEXT NOT NULL,
                notificacion_enviada INTEGER NOT NULL DEFAULT 0,
                whatsapp_preparado INTEGER NOT NULL DEFAULT 0,
                UNIQUE(promocion_id, cliente_id, ronda),
                FOREIGN KEY (promocion_id) REFERENCES promociones(id) ON DELETE CASCADE,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS notificaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                logro_id INTEGER NOT NULL UNIQUE,
                leida INTEGER NOT NULL DEFAULT 0,
                creada_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (logro_id) REFERENCES logros_promocion(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre);
            CREATE INDEX IF NOT EXISTS idx_clientes_ultima_visita ON clientes(ultima_visita);
            CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha);
            CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas(cliente_id);
        """)
        attendance_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(asistencias)").fetchall()
        }
        if "rompe_racha" not in attendance_columns:
            connection.execute(
                "ALTER TABLE asistencias ADD COLUMN rompe_racha INTEGER NOT NULL DEFAULT 0"
            )
        # Backfill attendance history from existing sales only once.
        count = connection.execute("SELECT COUNT(*) FROM asistencias").fetchone()[0]
        if count == 0:
            connection.execute("""INSERT INTO asistencias(cliente_id, fecha, nota)
                SELECT cliente_id, fecha, 'Importada de una venta existente'
                FROM ventas ORDER BY fecha, id""")
