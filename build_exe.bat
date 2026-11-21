@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Barberia CRM - Nuitka Standalone MSVC

echo ===========================================
echo  BARBERIA CRM - COMPILACION STANDALONE
echo ===========================================

where py >nul 2>nul
if errorlevel 1 (
 echo [ERROR] No se encuentra el lanzador py. Instala Python 3.12 x64.
 goto failed
)
py -3.12 -c "import sys; assert sys.maxsize > 2**32" >nul 2>nul
if errorlevel 1 (
 echo [ERROR] Python 3.12 de 64 bits no disponible.
 goto failed
)

if not exist ".venv-build\Scripts\python.exe" (
 py -3.12 -m venv .venv-build
 if errorlevel 1 goto failed
)
call ".venv-build\Scripts\activate.bat"
if errorlevel 1 goto failed
python -m pip install -r requirements-build.txt
if errorlevel 1 goto failed

if not exist reports mkdir reports
if not exist "frontend\static\css\style.css" (
 echo [ERROR] Falta el CSS compilado de frontend\scss\main.scss
 echo Ejecuta frontend\build_styles.bat y reintenta.
 goto failed
)
python tools\build_clock.py start

echo.
echo [COMPILANDO] MSVC, modo standalone. No se usara MinGW.
python -m nuitka ^
 --msvc=latest ^
 --standalone ^
 --assume-yes-for-downloads ^
 --output-dir=build ^
 --output-filename=BarberiaCRM.exe ^
 --include-data-dir=frontend\templates=frontend/templates ^
 --include-data-dir=frontend\static=frontend/static ^
 --include-package=backend ^
 --include-package=fastapi ^
 --include-package=starlette ^
 --include-package=jinja2 ^
 --report=reports\nuitka_compilation.xml ^
 launcher.py
set BUILD_RESULT=%ERRORLEVEL%
python tools\build_clock.py stop
if not "%BUILD_RESULT%"=="0" (
 echo [ERROR] Fallo la compilacion. Comprueba MSVC y reports\nuitka_compilation.xml.
 goto failed
)
if not exist "build\launcher.dist\BarberiaCRM.exe" (
 echo [ERROR] No existe el ejecutable final.
 goto failed
)

echo.
echo [OK] build\launcher.dist\BarberiaCRM.exe
echo [OK] Reporte Nuitka: reports\nuitka_compilation.xml
echo [MEDICION] Ejecutando 3 pruebas con datos temporales...
python tools\benchmark.py --exe "build/launcher.dist/BarberiaCRM.exe" --runs 3
if errorlevel 1 (
 echo [AVISO] El EXE existe, pero fallo la medicion. Ejecuta: python tools\benchmark.py
) else (
 echo [OK] reports\benchmark.md y reports\benchmark.json
)
echo.
echo [FINALIZADO] Conserva completa la carpeta build\launcher.dist.
pause
exit /b 0

:failed
echo [FALLO] Revisa las instrucciones en docs\operacion\07_compilacion_nuitka.md
pause
exit /b 1
