# Programación lógica: reglas y límites

[Índice](../README.md) · [Reglas aplicadas](../../backend/services/fidelizacion.py) · [Evaluación de logros](../../backend/repositories/fidelizacion.py)

## Especificación: términos, átomos, constantes y predicados
En un lenguaje lógico como Prolog, un **término** puede ser variable, constante o estructura; un **átomo** identifica una entidad simbólica; un **predicado** declara una relación; una **regla** concluye algo cuando otras condiciones se cumplen.

Ejemplo **conceptual Prolog, no código Python en ejecución**:
```prolog
categoria(ana, nuevo).
visitas(ana, 5).
meta(nuevo, 5).
elegible(C) :- categoria(C, T), visitas(C, V), meta(T, M), V >= M.
```
`ana` y `nuevo` son átomos; `5` es una constante numérica; `categoria/2` es un predicado; `C`, `T`, `V`, `M` son variables lógicas.

## Reglas, programas y extracción de respuestas
En Python, [cliente_cumple_objetivo](../../backend/services/fidelizacion.py) evalúa pertenencia a grupo o categoría. [registrar_asistencia](../../backend/repositories/fidelizacion.py) combina elegibilidad, meta y vigencia para emitir logros. [datos_dashboard](../../backend/repositories/fidelizacion.py) consulta el conjunto de respuestas persistidas con SQL.

## Unificación y resolución
En Prolog, la unificación hace coincidir términos mediante sustituciones; resolución utiliza reglas para encontrar demostraciones. **Esta aplicación no implementa unificación ni resolución de Prolog**. Usa condicionales Python y consultas SQL parametrizadas. No confundimos estas operaciones con un motor lógico formal.

## Control de ejecución, listas e indeterminismo
El algoritmo operativo es **determinista**: ordena asistencias por fecha e id, y asigna un logro único por promoción, cliente y ronda. La base impone [UNIQUE(promocion_id, cliente_id, ronda)](../../backend/database/schema.py); evita logros duplicados. Una lista de asistencias representa hechos ordenados. El indeterminismo y backtracking de Prolog se estudian con el ejemplo anterior, pero no se incorporan a la aplicación por complejidad innecesaria.

### Regla de negocio rastreable
1. [Se registra una visita](../../app.py).
2. [Se comprueba pertenencia](../../backend/services/fidelizacion.py).
3. [Se calcula conteo y ronda](../../backend/services/fidelizacion.py).
4. [Se guarda logro y notificación](../../backend/repositories/fidelizacion.py).
5. [Se presenta en dashboard](../../frontend/templates/dashboard.html).
