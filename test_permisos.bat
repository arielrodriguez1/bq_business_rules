@echo off
:: ════════════════════════════════════════════════════════════════════
::  Test de Permisos BigQuery — Launcher
::  Doble clic para probar tus permisos en proyectos de BigQuery
:: ════════════════════════════════════════════════════════════════════

title Test de Permisos BigQuery - Walmart Tech

:: Cambiar al directorio donde está este script
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║      Test de Permisos BigQuery — Walmart Tech              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

:: Verificar que Python esté instalado
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Python no esta instalado o no esta en el PATH.
    echo  Por favor instala Python 3.8+ desde https://www.python.org
    pause
    exit /b 1
)

:: Ejecutar el script de prueba
python test_permisos.py

pause
