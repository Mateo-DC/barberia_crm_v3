# Teoría de los lenguajes de programación

[Índice](../README.md) · [Backend](../../app.py) · [Lanzador](../../launcher.py)

## Paradigmas y por qué usamos varios
- **Funcional:** entradas → salidas sin mutar estado externo en [reglas de fidelización](../../backend/services/fidelizacion.py) y [reglas inmutables](../../backend/domain/rules.py). Facilita pruebas.
- **Orientado a objetos:** `@dataclass(frozen=True)` define la clase [MetaVisitas](../../backend/domain/rules.py), con validación de invariantes. FastAPI utiliza objetos de petición en [app.py](../../app.py).
- **Lógico/declarativo:** reglas condicionales de elegibilidad en [cliente_cumple_objetivo](../../backend/services/fidelizacion.py) y consulta SQL en [repositorio](../../backend/repositories/fidelizacion.py). No equivale a un motor de inferencia Prolog.

## Léxico y semántica
El **léxico** define tokens legales: identificadores, operadores, palabras clave, cadenas y sangría. Por ejemplo, `def cumple_meta(asistencias: int, meta: MetaVisitas) -> bool:` en [domain/rules.py](../../backend/domain/rules.py).
La **sintaxis** establece la combinación válida de esos tokens. La **semántica** describe el comportamiento: `>=` verifica una meta; la función retorna `bool`; `@dataclass(frozen=True)` impide reasignar sus atributos (no hace inmutables objetos anidados).
Los errores léxicos/sintácticos se encuentran antes de ejecutar el módulo; un `ValueError` por meta inválida es un error de ejecución/validación, no de sintaxis.

## Traducción y ejecución
1. Python analiza texto fuente: análisis léxico, sintáctico y semántica de ejecución (nombres y tipos suelen comprobarse al ejecutar).
2. CPython compila el código Python a *bytecode* y su máquina virtual lo interpreta.
3. Nuitka analiza los módulos, genera C, llama al compilador **MSVC** y construye una carpeta `standalone` con dependencias; no hace que todas las bibliotecas y operaciones Python sean código C puro.
4. Errores de sintaxis → `python -m compileall`; de importación → pruebas de importación; errores de C/MSVC → [reporte Nuitka](../operacion/07_compilacion_nuitka.md). Para errores de negocio se devuelven validaciones HTTP y se prueban los servicios.
5. **Recuperación de errores:** prueba unitaria antes de compilar, conservar reporte XML, corregir y reconstruir; las transacciones SQLite hacen `rollback` en [connection.py](../../backend/database/connection.py) ante excepciones.

## Cuadro comparativo (general, no benchmark)

| Lenguaje | Paradigmas principales | Ejecución usual | Uso típico | En este proyecto |
|---|---|---|---|---|
| Python | OO, funcional, imperativo | CPython + bytecode; opcional Nuitka | Backend, análisis | Elegido: FastAPI/Pandas |
| JavaScript | OO prototípico, funcional, imperativo | Motor JS con JIT/intérprete | Navegador | Interacciones web |
| Java | OO, funcional e imperativo | JVM bytecode + JIT | Servicios empresariales | Alternativa, no usada |
| C# | OO, funcional e imperativo | .NET IL + JIT/AOT | Aplicaciones Windows | Alternativa, no usada |
| C | Procedimental/imperativo | Compilación nativa | Sistemas | Backend de compilación Nuitka |
| C++ | OO, genérico, imperativo | Compilación nativa | Sistemas y motores | Compilador MSVC |
| Go | Procedimental, concurrente, interfaces | Compilación nativa | Servidores compactos | Alternativa evaluada |
| Rust | Funcional/imperativo, traits | Compilación nativa | Sistemas seguros | Alternativa evaluada |
| Prolog | Lógico declarativo | Motor de reglas/resolución | Inferencia | Referencia conceptual |

Este cuadro compara características usuales, no declara un ranking exacto de popularidad.
