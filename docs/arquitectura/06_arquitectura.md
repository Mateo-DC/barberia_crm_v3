# Arquitectura y seguridad

[Índice](../README.md) · [Mapa de módulos](09_mapa_codigo.md)

## Separación de responsabilidades

| Capa | Código | Qué hace |
|---|---|---|
| HTTP | [backend/web.py](../../backend/web.py) | Rutas y validación de formularios |
| Seguridad | [backend/security/access.py](../../backend/security/access.py) | Acceso según IP de origen |
| Dominio | [backend/domain/rules.py](../../backend/domain/rules.py) | Objetos inmutables, reglas comprobables |
| Servicios | [backend/services/fidelizacion.py](../../backend/services/fidelizacion.py) | Cálculo de metas y mensajes |
| Persistencia | [backend/repositories/fidelizacion.py](../../backend/repositories/fidelizacion.py) | Guardar visitas y logros con transacciones |
| Base local | [backend/database/schema.py](../../backend/database/schema.py) | Tablas, relaciones y restricciones SQLite |
| Analítica | [backend/analytics/metrics.py](../../backend/analytics/metrics.py) | Pandas y NumPy para informes |
| Frontend | [Jinja](../../frontend/templates/base.html) / [SCSS](../../frontend/scss/main.scss) | Experiencia visual responsiva |
| Ejecutable | [launcher.py](../../launcher.py) | Inicio de Uvicorn y URL del formulario |

## Flujo y permisos

La PC anfitriona administra clientes, ventas, promociones, grupos y campañas. Los equipos remotos pueden acceder al formulario `/registro` y a sus archivos estáticos. El [middleware](../../backend/web.py) rechaza otras rutas para IP remotas; `proxy_headers=False` evita confiar en cabeceras de origen no verificadas. Se recomienda restringir el puerto al segmento LAN por firewall.

**La IP no es autenticación.** La seguridad de producción debería sumar acceso de administrador, protección CSRF, rate limiting y copias de seguridad. No exponer directamente el servicio a Internet.

## Datos persistentes

La aplicación no necesita un servidor externo de base de datos. En desarrollo escribe en `data/`; en standalone usa `%LOCALAPPDATA%\BarberiaCRM` mediante [configuración](../../backend/config.py). Las imágenes son archivos locales editables. Se evita empaquetar la base de datos dentro del EXE o perderla al actualizarlo.

Para migrar una instalación anterior, respalda primero `barberia.db` y la carpeta de imágenes. La migración de la carpeta raíz se conserva solo cuando el archivo de destino aún no existe.
