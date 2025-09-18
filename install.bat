@echo off
REM ===========================================
REM DocuBot AI - Script de Instalación Rápida (Windows)
REM ===========================================

setlocal enabledelayedexpansion

echo 🤖 DocuBot AI - Instalación Rápida
echo ==================================

REM Verificar si Python está instalado
echo [INFO] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado. Por favor instala Python 3.9 o superior.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python !PYTHON_VERSION! encontrado

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    echo [SUCCESS] Entorno virtual creado
) else (
    echo [WARNING] El entorno virtual ya existe
)

REM Activar entorno virtual
echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat
echo [SUCCESS] Entorno virtual activado

REM Actualizar pip
echo [INFO] Actualizando pip...
python -m pip install --upgrade pip
echo [SUCCESS] pip actualizado

REM Instalar dependencias
echo [INFO] Instalando dependencias...
pip install -r requirements.txt
echo [SUCCESS] Dependencias instaladas

REM Crear archivo .env si no existe
if not exist ".env" (
    echo [INFO] Creando archivo de configuración...
    copy env.example .env
    echo [SUCCESS] Archivo .env creado desde env.example
    echo [WARNING] IMPORTANTE: Edita el archivo .env y configura tu OPENAI_API_KEY
) else (
    echo [WARNING] El archivo .env ya existe
)

REM Crear directorios necesarios
echo [INFO] Creando directorios necesarios...
if not exist "data\vector_db" mkdir data\vector_db
if not exist "logs" mkdir logs
echo [SUCCESS] Directorios creados

REM Verificar instalación
echo [INFO] Verificando instalación...
python -c "import streamlit, langchain, lancedb, openai; print('✅ Todas las dependencias principales están instaladas')" 2>nul
if errorlevel 1 (
    echo [ERROR] Error verificando dependencias
    pause
    exit /b 1
)

echo [SUCCESS] Instalación completada exitosamente!
echo.
echo 🚀 Para ejecutar la aplicación:
echo    1. Activa el entorno virtual: venv\Scripts\activate.bat
echo    2. Configura tu OPENAI_API_KEY en el archivo .env
echo    3. Ejecuta: streamlit run streamlit_app.py
echo.
echo 📖 Para más información, consulta el README.md
pause
