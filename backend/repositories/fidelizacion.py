from backend.database.connection import get_connection
from backend.services.fidelizacion import cliente_cumple_objetivo, contar_visitas, calcular_ronda
from datetime import date


def listar_grupos():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM grupos WHERE activo=1 ORDER BY nombre COLLATE NOCASE").fetchall()


def crear_grupo(nombre: str, descripcion: str = ''):
    with get_connection() as conn:
        conn.execute('INSERT INTO grupos(nombre, descripcion) VALUES (?, ?)', (nombre.strip(), descripcion.strip()))


def asignar_cliente_grupo(cliente_id: int, grupo_id: int):
    with get_connection() as conn:
        conn.execute('INSERT OR IGNORE INTO clientes_grupos(cliente_id, grupo_id) VALUES (?, ?)', (cliente_id, grupo_id))


def grupos_de_cliente(conn, cliente_id: int) -> set[str]:
    return {r['nombre'] for r in conn.execute('''SELECT g.nombre FROM grupos g
        JOIN clientes_grupos cg ON cg.grupo_id=g.id WHERE cg.cliente_id=? AND g.activo=1''', (cliente_id,)).fetchall()}


def crear_promocion(datos: dict):
    with get_connection() as conn:
        conn.execute('''INSERT INTO promociones
            (nombre, descripcion, premio, meta_visitas, modo_conteo, repeticion,
             tipo_objetivo, objetivo, mensaje, activa, fecha_inicio, fecha_fin)
            VALUES (:nombre,:descripcion,:premio,:meta_visitas,:modo_conteo,:repeticion,
             :tipo_objetivo,:objetivo,:mensaje,1,:fecha_inicio,:fecha_fin)''', datos)


def obtener_promocion(promocion_id: int):
    with get_connection() as conn:
        return conn.execute('SELECT * FROM promociones WHERE id=?', (promocion_id,)).fetchone()


def actualizar_promocion(promocion_id: int, datos: dict):
    # Evitar reinterpretar logros ya concedidos al cambiar las reglas históricas.
    with get_connection() as conn:
        existe = conn.execute('SELECT * FROM promociones WHERE id=?', (promocion_id,)).fetchone()
        if not existe:
            raise ValueError('Promoción inexistente.')
        logros = conn.execute('SELECT 1 FROM logros_promocion WHERE promocion_id=? LIMIT 1', (promocion_id,)).fetchone()
        reglas = ('meta_visitas', 'modo_conteo', 'repeticion', 'tipo_objetivo', 'objetivo', 'fecha_inicio')
        if logros and any(str(existe[k] or '') != str(datos[k] or '') for k in reglas):
            raise ValueError('Hay logros registrados: no puedes cambiar meta, modalidad, público ni fecha inicial. Crea otra promoción para nuevas reglas.')
        conn.execute("""UPDATE promociones SET nombre=:nombre,descripcion=:descripcion,premio=:premio,
            meta_visitas=:meta_visitas,modo_conteo=:modo_conteo,repeticion=:repeticion,
            tipo_objetivo=:tipo_objetivo,objetivo=:objetivo,mensaje=:mensaje,
            fecha_inicio=:fecha_inicio,fecha_fin=:fecha_fin WHERE id=:id""", {**datos, 'id': promocion_id})


def listar_promociones():
    with get_connection() as conn:
        return conn.execute('SELECT * FROM promociones ORDER BY activa DESC, id DESC').fetchall()


def alternar_promocion(promocion_id: int):
    with get_connection() as conn:
        conn.execute('UPDATE promociones SET activa=CASE activa WHEN 1 THEN 0 ELSE 1 END WHERE id=?', (promocion_id,))


def marcar_cliente_promocion_preparado(promocion_id: int, cliente_id: int):
    with get_connection() as conn:
        conn.execute('UPDATE logros_promocion SET whatsapp_preparado=1 WHERE promocion_id=? AND cliente_id=?', (promocion_id, cliente_id))
        conn.execute('UPDATE notificaciones SET leida=1 WHERE logro_id IN (SELECT id FROM logros_promocion WHERE promocion_id=? AND cliente_id=?)', (promocion_id, cliente_id))


def registrar_asistencia(cliente_id: int, fecha: str, nota: str = '', rompe_racha: bool = False) -> int:
    """Record one visit and create one unique achievement/notification per round."""
    with get_connection() as conn:
        cliente = conn.execute('SELECT * FROM clientes WHERE id=?', (cliente_id,)).fetchone()
        if not cliente:
            raise ValueError('El cliente no existe.')
        conn.execute('INSERT INTO asistencias(cliente_id, fecha, nota, rompe_racha) VALUES (?,?,?,?)', (cliente_id, fecha, nota.strip(), int(rompe_racha)))
        conn.execute('UPDATE clientes SET ultima_visita=?, visitas_totales=visitas_totales+1 WHERE id=?', (fecha, cliente_id))
        groups = grupos_de_cliente(conn, cliente_id)
        promociones = conn.execute('SELECT * FROM promociones WHERE activa=1').fetchall()
        created = 0
        for promo in promociones:
            if promo['fecha_inicio'] and fecha < promo['fecha_inicio']:
                continue
            if promo['fecha_fin'] and fecha > promo['fecha_fin']:
                continue
            if not cliente_cumple_objetivo(cliente, promo['tipo_objetivo'], promo['objetivo'], groups):
                continue
            attendance_sql = 'SELECT fecha, rompe_racha FROM asistencias WHERE cliente_id=?'
            attendance_args = [cliente_id]
            if promo['fecha_inicio']:
                attendance_sql += ' AND fecha>=?'
                attendance_args.append(promo['fecha_inicio'])
            attendance_sql += ' ORDER BY fecha, id'
            records = [dict(row) for row in conn.execute(attendance_sql, attendance_args).fetchall()]
            count = contar_visitas(records, promo['modo_conteo'])
            last_award = conn.execute('SELECT COALESCE(MAX(ronda),0) FROM logros_promocion WHERE promocion_id=? AND cliente_id=?', (promo['id'], cliente_id)).fetchone()[0]
            if promo['repeticion'] == 'recurrente' and promo['modo_conteo'] == 'consecutivas':
                # Every completed streak block unlocks the next global round.
                if count < promo['meta_visitas'] or count % promo['meta_visitas'] != 0:
                    continue
                round_number = last_award + 1
            else:
                round_number = calcular_ronda(count, promo['meta_visitas'], promo['repeticion'])
            if round_number <= last_award or round_number < 1:
                continue
            start_round = last_award + 1
            for round_no in range(start_round, round_number + 1):
                cur = conn.execute('''INSERT OR IGNORE INTO logros_promocion
                    (promocion_id, cliente_id, ronda, asistencias_meta, fecha_logro)
                    VALUES (?,?,?,?,?)''', (promo['id'], cliente_id, round_no, promo['meta_visitas'], fecha))
                if cur.rowcount:
                    conn.execute('INSERT OR IGNORE INTO notificaciones(logro_id) VALUES (?)', (cur.lastrowid,))
                    created += 1
        return created


def datos_dashboard():
    with get_connection() as conn:
        notifications = conn.execute('''SELECT n.id AS notificacion_id, n.leida, lp.id AS logro_id,
            lp.ronda, lp.fecha_logro, c.nombre, c.telefono, c.tipo_cliente,
            p.id AS promocion_id, p.nombre AS promocion, p.premio, p.mensaje, p.meta_visitas
            FROM notificaciones n JOIN logros_promocion lp ON lp.id=n.logro_id
            JOIN clientes c ON c.id=lp.cliente_id JOIN promociones p ON p.id=lp.promocion_id
            ORDER BY n.leida ASC, n.id DESC LIMIT 30''').fetchall()
        pendientes = conn.execute('SELECT COUNT(*) FROM notificaciones WHERE leida=0').fetchone()[0]
    return notifications, pendientes


def marcar_notificacion_leida(notificacion_id: int):
    with get_connection() as conn:
        conn.execute('UPDATE notificaciones SET leida=1 WHERE id=?', (notificacion_id,))


def marcar_logro_preparado(logro_id: int):
    with get_connection() as conn:
        conn.execute('UPDATE logros_promocion SET whatsapp_preparado=1 WHERE id=?', (logro_id,))
        conn.execute('UPDATE notificaciones SET leida=1 WHERE logro_id=?', (logro_id,))


def listar_asistencias(limit: int = 100):
    with get_connection() as conn:
        return conn.execute('''SELECT a.id,a.fecha,a.nota,a.rompe_racha,c.nombre,c.tipo_cliente
            FROM asistencias a JOIN clientes c ON c.id=a.cliente_id
            ORDER BY a.fecha DESC,a.id DESC LIMIT ?''', (limit,)).fetchall()


def listar_clientes_grupos():
    with get_connection() as conn:
        return conn.execute('''SELECT DISTINCT c.id,c.nombre,c.tipo_cliente,g.nombre AS grupo
            FROM clientes c LEFT JOIN clientes_grupos cg ON cg.cliente_id=c.id
            LEFT JOIN grupos g ON g.id=cg.grupo_id AND g.activo=1
            ORDER BY c.nombre COLLATE NOCASE''').fetchall()
