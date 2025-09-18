#!/bin/bash

# ===========================================
# DocuBot AI - Script de Instalación Rápida
# ===========================================

set -e  # Salir si hay algún error

echo "🤖 DocuBot AI - Instalación Rápida"
echo "=================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Python está instalado
print_status "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado. Por favor instala Python 3.9 o superior."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $PYTHON_VERSION encontrado"

# Verificar versión de Python
if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
    print_success "Versión de Python compatible (3.9+)"
else
    print_error "Se requiere Python 3.9 o superior. Versión actual: $PYTHON_VERSION"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    print_status "Creando entorno virtual..."
    python3 -m venv venv
    print_success "Entorno virtual creado"
else
    print_warning "El entorno virtual ya existe"
fi

# Activar entorno virtual
print_status "Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno virtual activado"

# Actualizar pip
print_status "Actualizando pip..."
pip install --upgrade pip
print_success "pip actualizado"

# Instalar dependencias
print_status "Instalando dependencias..."
pip install -r requirements.txt
print_success "Dependencias instaladas"

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    print_status "Creando archivo de configuración..."
    cp env.example .env
    print_success "Archivo .env creado desde env.example"
    print_warning "IMPORTANTE: Edita el archivo .env y configura tu OPENAI_API_KEY"
else
    print_warning "El archivo .env ya existe"
fi

# Crear directorios necesarios
print_status "Creando directorios necesarios..."
mkdir -p data/vector_db
mkdir -p logs
print_success "Directorios creados"

# Verificar instalación
print_status "Verificando instalación..."
python3 -c "
import sys
try:
    import streamlit
    import langchain
    import lancedb
    import openai
    print('✅ Todas las dependencias principales están instaladas')
except ImportError as e:
    print(f'❌ Error importando dependencias: {e}')
    sys.exit(1)
"

print_success "Instalación completada exitosamente!"
echo ""
echo "🚀 Para ejecutar la aplicación:"
echo "   1. Activa el entorno virtual: source venv/bin/activate"
echo "   2. Configura tu OPENAI_API_KEY en el archivo .env"
echo "   3. Ejecuta: streamlit run streamlit_app.py"
echo ""
echo "📖 Para más información, consulta el README.md"
