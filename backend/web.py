from __future__ import annotations
from datetime import date
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.config import BASE_DIR, DATA_DIR, DB_PATH, APP_TITLE, CLIENT_TYPES, CAMPAIGNS
from backend.database.schema import init_db
from backend.database.seed import seed_demo_data
from backend.database.connection import get_connection
from backend.repositories.clientes import listar_clientes, crear_cliente, obtener_cliente, actualizar_cliente
from backend.repositories.ventas import listar_ventas, registrar_venta
from backend.repositories.fidelizacion import (
    listar_grupos, crear_grupo, asignar_cliente_grupo, crear_promocion,
    listar_promociones, obtener_promocion, actualizar_promocion, registrar_asistencia, datos_dashboard,
    marcar_notificacion_leida, marcar_logro_preparado, marcar_cliente_promocion_preparado, alternar_promocion, listar_asistencias,
    listar_clientes_grupos,
)
from backend.services.fidelizacion import personalizar_mensaje
from backend.repositories.servicios import listar_servicios, guardar_servicio, alternar_servicio
from backend.security.access import is_host_request, public_registration_path
from backend.analytics.metrics import calcular_indicadores_ventas

app = FastAPI(title=APP_TITLE, docs_url=None, redoc_url=None)
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / 'frontend' / 'templates'))
STATIC_DIR = BASE_DIR / 'frontend' / 'static'
UPLOAD_DIR = DATA_DIR / 'campaign_images'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount('/static', StaticFiles(directory=str(STATIC_DIR)), name='static')

@app.middleware('http')
async def restrict_remote_routes(request: Request, call_next):
    # Bloqueo central: también protege endpoints futuros olvidados en un router.
    if not is_host_request(request) and not public_registration_path(request.url.path):
        if request.url.path == '/' and request.method == 'GET':
            return RedirectResponse('/registro', status_code=303)
        return HTMLResponse('Acceso restringido a la PC anfitriona', status_code=403)
    return await call_next(request)



def render(request: Request, template: str, **context):
    return TEMPLATES.TemplateResponse(request=request, name=template, context={**context, 'is_admin': is_host_request(request), 'title': APP_TITLE})


@app.on_event('startup')
def startup():
    init_db()
    if __import__('os').getenv('CRM_SEED_DEMO') == '1':
        seed_demo_data()


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    if not is_host_request(request):
        return RedirectResponse('/registro', status_code=303)
    notifications, notifications_pending = datos_dashboard()
    with get_connection() as conn:
        total_clientes = conn.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
        total_ventas = conn.execute('SELECT COUNT(*) FROM ventas').fetchone()[0]
        ingresos = conn.execute("SELECT COALESCE(SUM(monto),0) FROM ventas WHERE fecha >= date('now','-30 day')").fetchone()[0]
        inactivos = conn.execute("SELECT COUNT(*) FROM clientes WHERE ultima_visita <= date('now','-30 day')").fetchone()[0]
    # Analítica aislada del CRUD. Las métricas no bloquean la escritura de visitas.
    recent = listar_ventas()[:8]
    stats = calcular_indicadores_ventas(recent)
    ticket_medio = stats['ticket_medio']
    return render(request, 'dashboard.html', clientes=total_clientes, ventas=total_ventas, ingresos=ingresos, inactivos=inactivos, ventas_recientes=recent, notifications=notifications, notifications_pending=notifications_pending, ticket_medio=ticket_medio)


@app.get('/registro', response_class=HTMLResponse)
def registro_page(request: Request, ok: int = 0):
    return render(request, 'registro.html', tipos=CLIENT_TYPES, ok=ok)


@app.post('/registro')
def registro_submit(request: Request, nombre: str = Form(...), telefono: str = Form(...)):
    nombre, telefono = nombre.strip(), ''.join(c for c in telefono if c.isdigit())
    if len(nombre) < 2 or len(telefono) < 8 or len(telefono) > 15:
        return RedirectResponse('/registro?ok=2', status_code=303)
    crear_cliente(nombre, telefono, 'Nuevo', date.today().isoformat())
    return RedirectResponse('/registro?ok=1', status_code=303)


@app.get('/clientes', response_class=HTMLResponse)
def clientes_page(request: Request, tipo: str = ''):
    if not is_host_request(request):
        raise HTTPException(403, 'Panel disponible únicamente desde la PC anfitriona.')
    clients = listar_clientes()
    if tipo:
        clients = [c for c in clients if c['tipo_cliente'] == tipo]
    return render(request, 'clientes.html', clientes=clients, tipos=CLIENT_TYPES, tipo=tipo)


@app.get('/clientes/{cliente_id}/editar', response_class=HTMLResponse)
def editar_cliente_page(request: Request, cliente_id: int):
    if not is_host_request(request):
        raise HTTPException(403)
    cliente = obtener_cliente(cliente_id)
    if not cliente:
        raise HTTPException(404, 'Cliente no encontrado.')
    return render(request, 'cliente_editar.html', cliente=cliente, tipos=CLIENT_TYPES)


@app.post('/clientes/{cliente_id}/editar')
def editar_cliente_submit(request: Request, cliente_id: int, nombre: str = Form(...), telefono: str = Form(...), tipo_cliente: str = Form(...)):
    if not is_host_request(request):
        raise HTTPException(403)
    nombre = nombre.strip()
    telefono = ''.join(c for c in telefono if c.isdigit())
    if len(nombre) < 2 or not 8 <= len(telefono) <= 15 or tipo_cliente not in CLIENT_TYPES:
        raise HTTPException(400, 'Revisa el nombre, teléfono y categoría.')
    if not actualizar_cliente(cliente_id, nombre, telefono, tipo_cliente):
        raise HTTPException(404)
    return RedirectResponse('/clientes?ok=1', status_code=303)



@app.get('/ventas', response_class=HTMLResponse)
def ventas_page(request: Request):
    if not is_host_request(request):
        raise HTTPException(403, 'Panel disponible únicamente desde la PC anfitriona.')
    return render(request, 'ventas.html', ventas=listar_ventas(), clientes=listar_clientes(), campanas=CAMPAIGNS, servicios=[s for s in listar_servicios() if s['activo']], today=date.today().isoformat())


@app.post('/ventas')
def ventas_submit(request: Request, cliente_id: int = Form(...), monto: float = Form(...), fecha: str = Form(...), campana: str = Form('Sin campaña'), servicio: str = Form('Servicio general')):
    if not is_host_request(request):
        raise HTTPException(403, 'No autorizado.')
    if servicio != 'Servicio general' and not any(s['nombre'] == servicio and s['activo'] for s in listar_servicios()):
        raise HTTPException(400, 'Selecciona un servicio activo.')
    registrar_venta(cliente_id, monto, fecha, campana, servicio)
    return RedirectResponse('/ventas', status_code=303)


@app.get('/servicios', response_class=HTMLResponse)
def servicios_page(request: Request):
    if not is_host_request(request):
        raise HTTPException(403)
    return render(request, 'servicios.html', servicios=listar_servicios())


@app.post('/servicios')
def servicios_guardar(request: Request, nombre: str = Form(...), precio: float = Form(...), servicio_id: int = Form(0)):
    if not is_host_request(request):
        raise HTTPException(403)
    try:
        guardar_servicio(nombre, precio, servicio_id or None)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except __import__('sqlite3').IntegrityError as exc:
        raise HTTPException(400, 'Ya existe un servicio con ese nombre.') from exc
    return RedirectResponse('/servicios?ok=1', status_code=303)


@app.post('/servicios/{servicio_id}/alternar')
def servicios_alternar(request: Request, servicio_id: int):
    if not is_host_request(request):
        raise HTTPException(403)
    alternar_servicio(servicio_id)
    return RedirectResponse('/servicios', status_code=303)


@app.get('/asistencias', response_class=HTMLResponse)
def asistencias_page(request: Request, ok: int = 0):
    if not is_host_request(request):
        raise HTTPException(403, 'Las asistencias solo se administran desde la PC anfitriona.')
    return render(request, 'asistencias.html', clientes=listar_clientes(), asistencias=listar_asistencias(), today=date.today().isoformat(), ok=ok)


@app.post('/asistencias')
def asistencias_submit(request: Request, cliente_id: int = Form(...), fecha: str = Form(...), nota: str = Form(''), rompe_racha: str = Form('')):
    if not is_host_request(request):
        raise HTTPException(403, 'No autorizado.')
    try:
        registrar_asistencia(cliente_id, fecha, nota, rompe_racha.lower() in {'1','on','true','si','sí'})
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return RedirectResponse('/asistencias?ok=1', status_code=303)


@app.get('/fidelizacion', response_class=HTMLResponse)
def fidelizacion_page(request: Request):
    if not is_host_request(request):
        raise HTTPException(403, 'Fidelización disponible únicamente desde la PC anfitriona.')
    return render(request, 'fidelizacion.html', promociones=listar_promociones(), grupos=listar_grupos(), tipos=CLIENT_TYPES, clientes_grupos=listar_clientes_grupos())


def validar_promocion(nombre, descripcion, premio, meta_visitas, modo_conteo, repeticion,
                      tipo_objetivo, objetivo, mensaje, fecha_inicio, fecha_fin):
    if not nombre.strip() or not mensaje.strip() or meta_visitas < 1 or meta_visitas > 1000:
        raise HTTPException(400, 'Nombre, mensaje y meta válida son obligatorios.')
    if modo_conteo not in {'acumuladas', 'consecutivas'} or repeticion not in {'una_vez', 'recurrente'} or tipo_objetivo not in {'categoria', 'grupo', 'todos'}:
        raise HTTPException(400, 'Revisa las reglas de la promoción.')
    if tipo_objetivo == 'grupo' and not any(g['nombre'] == objetivo for g in listar_grupos()):
        raise HTTPException(400, 'Selecciona un grupo válido.')
    if tipo_objetivo == 'categoria' and objetivo not in CLIENT_TYPES:
        raise HTTPException(400, 'Selecciona una categoría válida.')
    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        raise HTTPException(400, 'La fecha de inicio no puede superar la fecha final.')
    return {'nombre': nombre.strip(), 'descripcion': descripcion.strip(), 'premio': premio.strip(),
            'meta_visitas': meta_visitas, 'modo_conteo': modo_conteo, 'repeticion': repeticion,
            'tipo_objetivo': tipo_objetivo, 'objetivo': objetivo if tipo_objetivo != 'todos' else 'Todos',
            'mensaje': mensaje.strip(), 'fecha_inicio': fecha_inicio or None, 'fecha_fin': fecha_fin or None}


@app.get('/fidelizacion/promociones/{promocion_id}/editar', response_class=HTMLResponse)
def editar_promocion_page(request: Request, promocion_id: int):
    if not is_host_request(request):
        raise HTTPException(403)
    promocion = obtener_promocion(promocion_id)
    if not promocion:
        raise HTTPException(404)
    return render(request, 'promocion_editar.html', promocion=promocion, tipos=CLIENT_TYPES,
                  grupos=listar_grupos())


@app.post('/fidelizacion/promociones/{promocion_id}/editar')
def editar_promocion_submit(request: Request, promocion_id: int, nombre: str = Form(...), descripcion: str = Form(''), premio: str = Form(''), meta_visitas: int = Form(...), modo_conteo: str = Form(...), repeticion: str = Form(...), tipo_objetivo: str = Form(...), objetivo: str = Form(...), mensaje: str = Form(...), fecha_inicio: str = Form(''), fecha_fin: str = Form('')):
    if not is_host_request(request):
        raise HTTPException(403)
    datos = validar_promocion(nombre, descripcion, premio, meta_visitas, modo_conteo,
                             repeticion, tipo_objetivo, objetivo, mensaje, fecha_inicio, fecha_fin)
    try:
        actualizar_promocion(promocion_id, datos)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return RedirectResponse('/fidelizacion?ok=4', status_code=303)


@app.post('/fidelizacion/promociones')
def fidelizacion_crear_promocion(request: Request, nombre: str = Form(...), descripcion: str = Form(''), premio: str = Form(''), meta_visitas: int = Form(...), modo_conteo: str = Form(...), repeticion: str = Form(...), tipo_objetivo: str = Form(...), objetivo: str = Form(...), mensaje: str = Form(...), fecha_inicio: str = Form(''), fecha_fin: str = Form('')):
    if not is_host_request(request):
        raise HTTPException(403, 'No autorizado.')
    datos = validar_promocion(nombre, descripcion, premio, meta_visitas, modo_conteo, repeticion,
                              tipo_objetivo, objetivo, mensaje, fecha_inicio, fecha_fin)
    crear_promocion(datos)
    return RedirectResponse('/fidelizacion?ok=1', status_code=303)


@app.post('/fidelizacion/promociones/{promocion_id}/alternar')
def fidelizacion_alternar_promocion(request: Request, promocion_id: int):
    if not is_host_request(request):
        raise HTTPException(403, 'No autorizado.')
    alternar_promocion(promocion_id)
    return RedirectResponse('/fidelizacion', status_code=303)


@app.post('/grupos')
def grupos_crear(request: Request, nombre: str = Form(...), descripcion: str = Form('')):
    if not is_host_request(request):
        raise HTTPException(403, 'No autorizado.')
    try:
        crear_grupo(nombre, descripcion)
    except Exception as exc:
        raise HTTPException(400, 'No se pudo crear el grupo. Comprueba que el nombre no esté repetido.') from exc
    return RedirectResponse('/fidelizacion?ok=2', status_code=303)


@app.post('/grupos/asignar')
def grupos_asignar(request: Request, cliente_id: int = Form(...), grupo_id: int = Form(...)):
    if not is_host_request(request):
        raise HTTPException(403, 'No autorizado.')
    asignar_cliente_grupo(cliente_id, grupo_id)
    return RedirectResponse('/fidelizacion?ok=3', status_code=303)


@app.post('/notificaciones/{notification_id}/leer')
def notificacion_leer(request: Request, notification_id: int):
    if not is_host_request(request):
        raise HTTPException(403, 'No autorizado.')
    marcar_notificacion_leida(notification_id)
    return RedirectResponse('/', status_code=303)


@app.get('/campanas', response_class=HTMLResponse)
def campaign_page(request: Request):
    if not is_host_request(request):
        raise HTTPException(403, 'Campañas disponibles únicamente desde la PC anfitriona.')
    return render(request, 'campanas.html', clientes=listar_clientes(), promociones=[p for p in listar_promociones() if p['activa']], tipos=CLIENT_TYPES)


@app.post('/campanas')
async def campaign_submit(request: Request, mensaje: str = Form(''), tipo: str = Form('Todos'), promocion_id: int = Form(0), imagen: UploadFile | None = File(None)):
    if not is_host_request(request):
        raise HTTPException(403, 'No autorizado.')
    image_url = ''
    if imagen and imagen.filename:
        ext = Path(imagen.filename).suffix.lower()
        if ext not in {'.jpg', '.jpeg', '.png', '.webp'}:
            raise HTTPException(400, 'Formato permitido: JPG, PNG o WEBP.')
        content = await imagen.read(5 * 1024 * 1024 + 1)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(400, 'La imagen supera 5 MB.')
        filename = f'campaign_{date.today().strftime("%Y%m%d")}_{abs(hash(content))}{ext}'
        (UPLOAD_DIR / filename).write_bytes(content)
        image_url = f'/campaign-images/{filename}'
    promo = None
    with get_connection() as conn:
        if promocion_id:
            promo = conn.execute('SELECT * FROM promociones WHERE id=? AND activa=1', (promocion_id,)).fetchone()
            if not promo:
                raise HTTPException(400, 'La promoción seleccionada no existe o está inactiva.')
            rows = conn.execute('''SELECT c.id,c.nombre,c.telefono,c.tipo_cliente,MAX(lp.id) AS logro_id,MAX(lp.ronda) AS ronda
                FROM logros_promocion lp JOIN clientes c ON c.id=lp.cliente_id
                WHERE lp.promocion_id=? AND lp.whatsapp_preparado=0 GROUP BY c.id,c.nombre,c.telefono,c.tipo_cliente ORDER BY c.nombre''', (promocion_id,)).fetchall()
        else:
            rows = conn.execute('SELECT id,nombre,telefono,tipo_cliente,NULL AS logro_id,0 AS ronda FROM clientes ORDER BY nombre').fetchall()
    recipients = [r for r in rows if promocion_id or tipo == 'Todos' or r['tipo_cliente'] == tipo]
    if promocion_id and not recipients:
        raise HTTPException(400, 'No hay clientes pendientes que hayan desbloqueado esta promoción.')
    template = (promo['mensaje'] if promo and not mensaje.strip() else mensaje.strip()) or 'Hola {nombre}, tenemos una promoción especial para ti. ¿Te gustaría reservar una cita?'
    if not template:
        raise HTTPException(400, 'Escribe un mensaje para la campaña.')
    items = []
    for r in recipients:
        personalized = template.replace('{nombre}', r['nombre'])
        if promo:
            personalized = personalized.replace('{promocion}', promo['nombre']).replace('{premio}', promo['premio'] or promo['descripcion']).replace('{ronda}', str(r['ronda']))
        digits = ''.join(c for c in r['telefono'] if c.isdigit())
        items.append({'nombre': r['nombre'], 'telefono': r['telefono'], 'mensaje': personalized, 'url': f'https://wa.me/{digits}?text={quote(personalized)}'})
        if promo and r['logro_id']:
            marcar_cliente_promocion_preparado(promocion_id, r['id'])
    csv_path = DATA_DIR / 'ultima_campana.csv'
    import csv
    with csv_path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['nombre','telefono','mensaje','url']); writer.writeheader(); writer.writerows(items)
    return render(request, 'campana_resultado.html', items=items, image_url=image_url, csv_ready=True)


@app.get('/campaign-images/{filename}')
def campaign_image(filename: str, request: Request):
    if not is_host_request(request):
        raise HTTPException(403, 'No autorizado.')
    path = (UPLOAD_DIR / Path(filename).name).resolve()
    if UPLOAD_DIR.resolve() not in path.parents or not path.is_file():
        raise HTTPException(404)
    return FileResponse(path)


@app.get('/descargar-campana')
def download_campaign(request: Request):
    if not is_host_request(request):
        raise HTTPException(403, 'No autorizado.')
    path = DATA_DIR / 'ultima_campana.csv'
    if not path.exists(): raise HTTPException(404, 'Primero genera una campaña.')
    return FileResponse(path, filename='destinatarios_campana.csv', media_type='text/csv')
