# Documentación de Barbería CRM

Esta documentación está organizada por **objetivo**, no por el orden de creación de los archivos.
Puedes abrir los enlaces desde VS Code para ir al código real.

## 1. Fundamentos académicos

| Tema | Guía | Código que lo demuestra |
|---|---|---|
| Paradigmas, léxico, semántica y compilación | [Teoría de lenguajes](fundamentos/01_teoria_lenguajes.md) | [Reglas de dominio](../backend/domain/rules.py) |
| Funciones puras, lambdas, orden superior y ámbitos | [Programación funcional](fundamentos/02_programacion_funcional.md) | [Funciones puras](../backend/domain/rules.py) |
| Predicados, resolución y límites de Python | [Programación lógica](fundamentos/03_programacion_logica.md) | [Reglas de fidelización](../backend/services/fidelizacion.py) |
| Tipos, control, clases y objetos | [Python multiparadigma](fundamentos/04_programacion_multiparadigma.md) | [Modelos](../backend/domain/rules.py) |
| Pandas y NumPy | [Ciencia de datos](fundamentos/05_ciencia_de_datos.md) | [Analítica](../backend/analytics/metrics.py) |

## 2. Arquitectura y operación

- [**Mapa de módulos, flujo de datos y seguridad**](arquitectura/06_arquitectura.md)
- [**Compilación con Nuitka y benchmark en Windows**](operacion/07_compilacion_nuitka.md)
- [**Diseño visual con SCSS**](arquitectura/08_estilos_scss.md)
- [**Mapa directo de archivos y responsabilidades**](arquitectura/09_mapa_codigo.md)

## Cómo mantener esta documentación

1. Implementa el cambio en su módulo, con pruebas cuando afecte reglas de negocio.
2. Si se introduce un concepto académico, enlaza la función **que de verdad lo implementa**.
3. Actualiza la guía de arquitectura cuando cambies rutas, responsabilidades o permisos.
4. Regenera el CSS únicamente cuando cambies los archivos de `frontend/scss`.

**Advertencia:** explicar un paradigma no significa implementarlo por completo. La unificación o la resolución de Prolog son ejemplos conceptuales; la aplicación usa Python y SQL, no un intérprete lógico.
