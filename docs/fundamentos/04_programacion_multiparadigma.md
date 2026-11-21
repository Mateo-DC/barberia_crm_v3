# Python multiparadigma: correspondencia entre conceptos y código

[Índice](../README.md)

| Concepto | Implementación | Por qué |
|---|---|---|
| Tipos de datos | [MetaVisitas](../../backend/domain/rules.py) `int`, `str`, `bool` | Validar invariantes |
| Variables y operadores | [calcular_ronda](../../backend/services/fidelizacion.py), `//`, `<`, `>=` | Metas por rondas |
| `print()` | [launcher.py](../../launcher.py) | Informar URLs en consola host |
| Entrada de datos | [Form(...) en app.py](../../app.py) | Entrada real desde formularios HTML, no teclado de consola |
| Control secuencial | [registrar_asistencia](../../backend/repositories/fidelizacion.py) | Inserción → conteo → logros |
| Cadenas | [personalizar_mensaje](../../backend/services/fidelizacion.py) | Plantillas de mensajes |
| Condicionales | [cliente_cumple_objetivo](../../backend/services/fidelizacion.py) | Filtrar elegibilidad |
| Repetitivas | `for promo in promociones` en [fidelizacion.py](../../backend/repositories/fidelizacion.py) | Evaluar promociones |
| Arreglos | [`numpy.asarray` en metrics.py](../../backend/analytics/metrics.py) | Agregación numérica |
| Listas | [seleccionar](../../backend/domain/rules.py) | Filtrado de colecciones |
| Tuplas | `fetchone()` y argumentos SQL en [fidelizacion.py](../../backend/repositories/fidelizacion.py) | Parámetros de consultas |
| Diccionarios | [metrics.py](../../backend/analytics/metrics.py) | Indicadores con claves claras |
| Funciones | [cumple_meta](../../backend/domain/rules.py) | Reutilización y pruebas |
| Módulos | [app.py](../../app.py), [analytics](../../backend/analytics/metrics.py), [security](../../backend/security/access.py) | Separación de responsabilidades |
| Clases y objetos | [MetaVisitas](../../backend/domain/rules.py), FastAPI [Request](../../app.py) | Modelado de objetos |
| Herencia | No se añade subclase innecesaria | La composición y las funciones bastan; ver nota |

**Herencia:** Python permite declarar `class Premium(Cliente)`, pero no existe en el dominio una especialización que lo requiera. Las categorías se representan como datos y reglas. Introducir jerarquías de clases sería complejidad artificial. El siguiente ejemplo es **didáctico y no se ejecuta en producción**:

```python
class Persona:
    def __init__(self, nombre):
        self.nombre = nombre

class Cliente(Persona):
    def __init__(self, nombre, visitas):
        super().__init__(nombre)
        self.visitas = visitas
```

**Ámbitos de variables**: locales de función, de módulo y de objeto. Configuración única en [config.py](../../backend/config.py); no usar estado global mutable para operaciones simultáneas.
