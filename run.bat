@echo off
:: ════════════════════════════════════════════════════════════════════
::  BQ Business Rules Generator — Launcher
::  Doble clic en este archivo para iniciar el generador
:: ════════════════════════════════════════════════════════════════════

title BQ Business Rules Generator - Walmart Tech

:: Cambiar al directorio donde está este script
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║      BQ Business Rules Generator — Walmart Tech             ║
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

:: Verificar dependencias y ofrecer instalarlas
python -c "import google.cloud.bigquery, pandas, openpyxl" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [INFO] Instalando dependencias necesarias...
    echo.
    pip install google-cloud-bigquery pandas openpyxl db-dtypes pyarrow
    echo.
)

:: Ejecutar la aplicación principal
python main.py

pause
