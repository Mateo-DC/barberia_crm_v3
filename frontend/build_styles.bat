@echo off
setlocal
cd /d "%~dp0.."
where npx >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Se requiere Node.js y npm para compilar SCSS.
  echo El CSS ya compilado permite ejecutar la aplicacion sin Node.js.
  exit /b 1
)
call npx --yes sass --no-source-map --style=expanded "frontend/scss/main.scss" "frontend/static/css/style.css"
if errorlevel 1 (
  echo [ERROR] Sass no pudo compilar los estilos.
  exit /b 1
)
echo [OK] CSS actualizado en frontend/static/css/style.css
endlocal
