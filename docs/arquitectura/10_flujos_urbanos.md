# Flujos de Barbería CRM (interfaz urbana)

Esta actualización se aplica **encima de v3.1 (organización + SCSS)**. Las funciones de negocio mantienen SQLite, FastAPI y archivos locales. Los recursos web se empaquetan con Nuitka, pero la BD persistente sigue fuera del ejecutable.

## 1. Clientes

- `/clientes`: listado, filtros, accesos directos a WhatsApp y al editor.
- `/clientes/{id}/editar`: cambiar nombre, teléfono y categoría. No elimina historial ni recompensas.
- `/registro`: entrada LAN restringida a nombre y teléfono.
- Implementación: [`backend/web.py`](../../backend/web.py), [`backend/repositories/clientes.py`](../../backend/repositories/clientes.py) y [`frontend/templates/cliente_editar.html`](../../frontend/templates/cliente_editar.html).

## 2. Qué se brinda al cliente

- `/servicios`: catálogo local de servicios con precio sugerido, edición y activación.
- `/ventas`: registrar cliente, servicio, importe y fecha; historial legible.
- `ventas.servicio`: columna añadida con `ALTER TABLE` al abrir bases antiguas (valor por defecto: `Servicio general`); **no se borran ventas anteriores**.
- Las ventas **no** se contabilizan automáticamente como asistencias: una asistencia se registra explícitamente en `/asistencias` para evitar duplicación de recompensas. Un indicador `schema_meta` impide que ventas nuevas se vuelvan a importar como asistencias en el siguiente arranque.
- Implementación: [`backend/database/schema.py`](../../backend/database/schema.py), [`backend/repositories/servicios.py`](../../backend/repositories/servicios.py), [`backend/repositories/ventas.py`](../../backend/repositories/ventas.py).

## 3. Qué se entrega como fidelización

- `/fidelizacion`: crear reglas, grupos y promociones; enlaces para editar cada una.
- `/fidelizacion/promociones/{id}/editar`: edición de mensajes y beneficios. Si ya hubo logros, no se permite cambiar meta, método de conteo, repetición, público ni inicio (para proteger el historial).
- `/asistencias`: registra y evalúa metas, incrementa contadores, crea notificación.
- `/campanas`: prepara enlaces WhatsApp de quienes han alcanzado una meta; envío y adjunto de imagen siguen siendo manuales.
- Implementación: [`backend/repositories/fidelizacion.py`](../../backend/repositories/fidelizacion.py) y [`frontend/templates/promocion_editar.html`](../../frontend/templates/promocion_editar.html).

## 4. Diseño y pruebas

- Variables y estilos editables en [`frontend/scss/partials/_urban.scss`](../../frontend/scss/partials/_urban.scss).
- CSS generado y listo para distribución en [`frontend/static/css/style.css`](../../frontend/static/css/style.css).
- Pruebas del flujo web: [`tests/test_web_workflows.py`](../../tests/test_web_workflows.py).
- Para ejecutarlas: `python -m pip install -r requirements-dev.txt` y `python -m unittest discover -s tests -v`.
- Compilación: `build_exe.bat` (Nuitka 4.3.5, Python 3.12, MSVC) **debe verificarse en Windows**; no se ha ejecutado aquí.

## Seguridad

El aislamiento por IP ya existente se conserva para rutas administrativas. Es una medida para LAN privada, **no sustituye un inicio de sesión o autenticación de administrador**. No abras el puerto a Internet.
