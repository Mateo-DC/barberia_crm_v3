# Barbería CRM — FastAPI y SQLite (organización v3.1)

Aplicación web para la red local, con Python 3.12, FastAPI, Jinja2, SQLite, Pandas, NumPy y compilación Nuitka `standalone`.

**[Documentación por áreas](docs/README.md)** · [Mapa de carpetas](docs/arquitectura/09_mapa_codigo.md) · [Guía SCSS](docs/arquitectura/08_estilos_scss.md)

## Iniciar en Windows (sin compilar)

```bat
py -3.12 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python launcher.py
```

- PC anfitriona: `http://127.0.0.1:8000`.
- Celulares en LAN: `http://IP-DEL-HOST:8000/registro`.
- Demo opcional: `set CRM_SEED_DEMO=1` antes de iniciar; no usar con datos reales.

## Editar apariencia

1. Modifica los archivos `frontend/scss/partials/*.scss`.
2. Ejecuta `frontend\build_styles.bat` para generar `frontend/static/css/style.css` (requiere Node.js y `npx` **solo para editar estilos**).
3. El CSS compilado ya está incluido y el programa **no requiere Node.js ni Sass**.

## Compilar y medir

`build_exe.bat` usa Nuitka con MSVC en modo `standalone`, empaqueta `backend/` y `frontend/static`, y genera informes en `reports/`.

Ver [compilación y benchmark](docs/operacion/07_compilacion_nuitka.md). Distribuir **toda** `build/launcher.dist`, no solo el `.exe`.

## Probar cambios

```bat
python -m unittest discover -s tests -v
```

## Funcionamiento y límites

Conserva clientes, ventas, asistencias, promociones, segmentación, grupos manuales, notificaciones y preparación de mensajes WhatsApp. El envío se confirma manualmente y las imágenes se adjuntan manualmente. Las asistencias consecutivas se reinician por ruptura explícita, no por calendario automático. La autorización por IP no sustituye un inicio de sesión real; no expongas el servicio a Internet.
