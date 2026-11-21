# Compilación con Nuitka y benchmark Windows

[Índice](../README.md) · [Script build_exe.bat](../../build_exe.bat) · [Benchmark](../../tools/benchmark.py)

## Requisitos
Windows de 64 bits, Python 3.12 x64 (`py -3.12`), Visual Studio con **Desktop development with C++**, MSVC y Windows SDK. En Developer Command Prompt puedes comprobar `where cl` y `cl`. Que Rust compile **no garantiza** que Nuitka encuentre el mismo MSVC; Rust puede utilizar `windows-gnu` o `windows-msvc`.

## Ejecutar
1. Abrir terminal de desarrollador de Visual Studio si Nuitka no detecta MSVC.
2. Desde la raíz ejecutar `build_exe.bat`.
3. El script crea `.venv-build`, instala [versiones fijadas](../../requirements-build.txt), ejecuta `--msvc=latest --standalone`, agrega plantillas y estáticos y genera `build/launcher.dist/BarberiaCRM.exe`.
4. Se guarda `reports/nuitka_compilation.xml`, `reports/build_duration_seconds.txt`, `reports/benchmark.json` y `reports/benchmark.md`.
5. **Distribuir toda la carpeta `.dist`, no solo el `.exe`.** El modo `onefile` se evaluará tras estabilidad.

## Benchmark
Después de compilar, `python tools/benchmark.py --exe build/launcher.dist/BarberiaCRM.exe --runs 3` inicia procesos separados con datos SQLite temporales, desactiva navegador y demo, mide:
- **Tamaño del `.exe`** y **de la carpeta de distribución** (MB).
- **Duración de compilación** (segundos, capturada por script).
- **Arranque**: desde `Popen` hasta primer `GET /registro` HTTP 200.
- **Memoria RSS aproximada**: lectura de procesos con `psutil` tras arranque.
- **Latencia HTTP local**: 20 consultas de `/registro` por repetición.
- Comparación **Python interpretado vs. Nuitka standalone**, en el mismo equipo, con mismas rutas, sin datos reales.

No hay números predefinidos ni promesas de reducción. Antivirus, disco, cachés y CPU afectan resultados. No se mide tiempo de interfaz del navegador, concurrencia LAN ni memoria máxima absoluta. Si el script de benchmark falla no invalida necesariamente una compilación exitosa.

## Si falla
- `cannot locate suitable C compiler`: ejecutar desde Visual Studio Developer Command Prompt, comprobar `where cl`.
- `windows.h: No such file`: comprobar Windows SDK o conflicto con GCC/MinGW.
- error de importación/recursos: comprobar `reports/nuitka_compilation.xml`, que templates/static estén dentro de `.dist`, ejecutar `.exe` desde consola.
- puerto ocupado: cerrar instancia anterior o `set CRM_PORT=8100`.
- guardar datos en otra ruta: `set CRM_DATA_DIR=C:\Ruta\Datos` antes de ejecutar.
- Opcional para demo: `set CRM_SEED_DEMO=1` (no usar si deseas datos reales limpios).

**Rust y MSVC:** comprobar `rustc -vV`; `host: x86_64-pc-windows-msvc` indica toolchain MSVC (buena señal), `windows-gnu` no. Incluso con MSVC instalado hay que tener disponible el entorno `cl.exe` y el Windows SDK para Nuitka.
