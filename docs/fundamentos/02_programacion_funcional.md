# Programación funcional aplicada

[Índice](../README.md) · [Reglas](../../backend/domain/rules.py) · [Analítica](../../backend/analytics/metrics.py)

## Programas como funciones, variables y funciones
[**cumple_meta**](../../backend/domain/rules.py) recibe datos y devuelve un resultado sin escribir en SQLite. Variables locales `asistencias` y `meta` están acotadas a la llamada.

```python
meta = MetaVisitas(cantidad=5, modo='acumuladas')
resultado = cumple_meta(5, meta)  # True
```

## Definición declarativa, valores inmutables y listas
`MetaVisitas` es `@dataclass(frozen=True, slots=True)`, una configuración inmutable. En [contar_visitas](../../backend/services/fidelizacion.py), una secuencia de registros se transforma en un número con una regla declarada: suma todas o cuenta desde la ruptura explícita. Se crea una lista de registros antes de evaluarla para evitar efectos colaterales con cursores.

## Funciones definidas y anónimas
- Función con `def`: [seleccionar](../../backend/domain/rules.py), genérica con `TypeVar`.
- Función **anónima** `lambda monto: monto > 0`: [calcular_indicadores_ventas](../../backend/analytics/metrics.py).
- **Funciones como parámetros**: `seleccionar(items, criterio)` recibe una función callable.
- **Funciones en listas**: el resultado de `filter` se materializa con `list` para permitir iteraciones posteriores sin consumir un iterador.

## Funciones de orden superior, genéricas y ámbitos
`seleccionar` es de orden superior porque recibe una función; también es genérica porque no exige un tipo concreto de elemento. Las variables `items`, `criterio` y `montos` tienen **ámbito local**. El nombre `T` es una variable de tipo definida a nivel de módulo; no es una variable global mutable de negocio.

Ejemplo práctico, ya utilizado por la analítica:
```python
montos = seleccionar([10.0, -5.0, 15.0], lambda monto: monto > 0)
# [10.0, 15.0]
```

No se obliga a usar `lambda` cuando un `def` con nombre mejora la legibilidad. Las reglas de negocio deben ser fáciles de auditar y probar: [test_fidelizacion.py](../../tests/test_fidelizacion.py) y [test_conceptos.py](../../tests/test_conceptos.py).
