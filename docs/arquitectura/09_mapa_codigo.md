# Mapa de módulos y responsabilidades

[Índice](../README.md)

```text
barberia_crm_v3/
├── backend/
│   ├── analytics/       # Pandas y NumPy (solo analítica)
│   ├── database/        # SQLite, conexión, esquema y datos demo
│   ├── domain/          # Modelos inmutables y reglas puras
│   ├── repositories/    # Acceso SQL y transacciones
│   ├── security/        # Restricciones por IP
│   ├── services/        # Reglas y procesos de negocio
│   ├── utils/           # Formato y utilidades
│   ├── config.py        # Rutas y configuración
│   └── web.py           # Endpoints FastAPI
├── frontend/
│   ├── templates/       # HTML/Jinja2
│   ├── scss/            # SCSS editables por área
│   ├── static/css/      # CSS compilado y distribuido
│   ├── static/js/       # Interacciones livianas
│   └── build_styles.bat # Compilación opcional de SCSS
├── docs/
│   ├── fundamentos/    # Material académico aplicado
│   ├── arquitectura/   # Mapa y pautas de mantenimiento
│   └── operacion/      # Compilación y benchmark
├── tests/              # Comprobaciones de reglas
├── tools/              # Benchmarks e informes
├── data/               # Datos locales en desarrollo
├── app.py              # Compatibilidad con uvicorn app:app
├── launcher.py         # Ejecuta el servidor y abre navegador
└── build_exe.bat       # Nuitka standalone con MSVC
```

## Flujo de una visita

1. [FastAPI recibe el formulario](../../backend/web.py).
2. [El repositorio escribe la visita](../../backend/repositories/fidelizacion.py).
3. [El servicio calcula la elegibilidad](../../backend/services/fidelizacion.py).
4. [La base conserva el estado](../../backend/database/schema.py).
5. [El dashboard muestra avisos](../../frontend/templates/dashboard.html).

## Reglas de diseño

- Los endpoints no deben contener consultas SQL largas nuevas: usar `repositories/`.
- El dominio debe ser independiente de FastAPI y SQLite.
- Analytics no debe ralentizar la captura de visitas.
- No mover ni borrar el archivo SQLite durante una actualización.
- Los permisos por IP se aplican en [middleware](../../backend/web.py) y se documentan como una **barrera básica**, no autenticación.
