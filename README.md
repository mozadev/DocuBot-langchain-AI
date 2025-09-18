# 🤖 DocuBot AI - Sistema de IA Empresarial

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://langchain.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema de IA empresarial que demuestra las mejores prácticas de desarrollo en Python, LangChain, LanceDB y Streamlit. Este proyecto implementa un chatbot inteligente que puede procesar documentos y responder preguntas basándose en el contenido usando RAG (Retrieval-Augmented Generation).

## 🚀 Características Principales

- ✅ **Procesamiento de documentos** PDF/DOCX con extracción inteligente de texto
- ✅ **Base de datos vectorial** con LanceDB para búsquedas semánticas rápidas
- ✅ **Chat inteligente** con memoria de conversación y contexto
- ✅ **Interfaz web moderna** con Streamlit y diseño responsivo
- ✅ **Sistema de logging** empresarial con monitoreo
- ✅ **Configuración flexible** con variables de entorno
- ✅ **Pruebas unitarias** completas
- ✅ **Documentación detallada** y ejemplos de uso

## 🏗️ Arquitectura del Proyecto

```
docubot-ai/
├── src/                    # Código fuente principal
│   ├── core/              # Lógica de negocio central
│   │   └── logger.py      # Sistema de logging
│   ├── data/              # Manejo de datos y vectores
│   │   ├── document_processor.py  # Procesamiento de documentos
│   │   └── vector_store.py        # Gestión de base de datos vectorial
│   ├── llm/               # Integración con LLMs
│   │   └── chat_manager.py        # Gestión de conversaciones
│   └── ui/                # Interfaz de usuario
├── tests/                 # Pruebas unitarias
├── config/                # Configuraciones
│   └── settings.py        # Configuración con Pydantic
├── data/                  # Datos y base de datos vectorial
│   ├── sample_document.txt
│   └── vector_db/         # Base de datos LanceDB
├── logs/                  # Archivos de log
├── requirements.txt       # Dependencias Python
├── setup.py              # Configuración del paquete
├── env.example           # Ejemplo de variables de entorno
└── streamlit_app.py      # Aplicación principal
```

## 🛠️ Tecnologías Utilizadas

- **Python 3.9+**: Lenguaje principal
- **LangChain 0.3+**: Framework para aplicaciones de IA con LCEL
- **LanceDB**: Base de datos vectorial de alto rendimiento
- **OpenAI API**: Modelos de lenguaje y embeddings
- **Streamlit**: Interfaz de usuario web
- **Pydantic v2**: Validación de datos y configuración
- **Pandas & NumPy**: Procesamiento de datos
- **PyPDF & python-docx**: Procesamiento de documentos

## 📋 Requisitos del Sistema

- **Python**: 3.9 o superior
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB+)
- **Espacio en disco**: 1GB libre
- **Conexión a internet**: Para acceder a OpenAI API

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (Recomendada)

**Para macOS/Linux:**
```bash
git clone https://github.com/mozadev/DocuBot-langchain-AI.git
cd DocuBot-langchain-AI
chmod +x install.sh
./install.sh
```

**Para Windows:**
```cmd
git clone https://github.com/mozadev/DocuBot-langchain-AI.git
cd DocuBot-langchain-AI
install.bat
```

### Opción 2: Instalación Manual

#### 1. Clonar el Repositorio

```bash
git clone https://github.com/mozadev/DocuBot-langchain-AI.git
cd DocuBot-langchain-AI
```

#### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

#### 3. Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar el archivo .env con tu configuración
nano .env  # o usar tu editor preferido
```

**Configuración mínima requerida en `.env`:**
```env
# OBLIGATORIO: Tu clave de API de OpenAI
OPENAI_API_KEY=tu_clave_de_api_aqui

# Opcional: Configuración de modelos (valores por defecto)
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_TEMPERATURE=0.2
```

#### 5. Ejecutar la Aplicación

```bash
streamlit run streamlit_app.py
```

La aplicación estará disponible en: `http://localhost:8501`

## 🔧 Instalación Avanzada

### Instalación con pip (desarrollo)

```bash
# Instalar en modo desarrollo
pip install -e .

# Instalar dependencias de desarrollo
pip install -e ".[dev]"
```

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=src tests/

# Ejecutar pruebas específicas
pytest tests/test_document_processor.py -v
```

### Formateo y Linting

```bash
# Formatear código
black src/ tests/

# Verificar estilo
flake8 src/ tests/

# Verificar tipos
mypy src/
```

## 📖 Guía de Uso

### 1. Subir Documentos

1. Ve a la pestaña **"📄 Subir Documentos"**
2. Selecciona archivos PDF o DOCX
3. Haz clic en **"🚀 Procesar Documentos"**
4. Espera a que se complete el procesamiento

### 2. Chatear con tus Documentos

1. Ve a la pestaña **"💬 Chat"**
2. Escribe tu pregunta en el campo de texto
3. Haz clic en **"🚀 Enviar"**
4. El bot responderá basándose en tus documentos

### 3. Ver Análisis

1. Ve a la pestaña **"📊 Análisis"**
2. Revisa estadísticas de la base de datos
3. Ve el historial de conversaciones
4. Monitorea el rendimiento del sistema

## ⚙️ Configuración Avanzada

### Variables de Entorno Disponibles

```env
# --- OpenAI ---
OPENAI_API_KEY=tu_clave_aqui              # OBLIGATORIO
OPENAI_MODEL=gpt-4o-mini                  # Modelo de chat
OPENAI_TEMPERATURE=0.2                    # Creatividad (0-1)

# --- Embeddings ---
EMBEDDING_MODEL=text-embedding-3-small    # Modelo de embeddings

# --- Procesamiento ---
CHUNK_SIZE=1000                           # Tamaño de fragmentos
CHUNK_OVERLAP=200                         # Solapamiento entre fragmentos

# --- Base de Datos ---
LANCE_DB_PATH=./data/vector_db            # Ruta de la BD vectorial
LANCE_DB_TABLE=documents                  # Nombre de la tabla

# --- Aplicación ---
APP_NAME=DocuBot AI                       # Nombre de la app
DEBUG=False                               # Modo debug

# --- Logging ---
LOG_LEVEL=INFO                            # Nivel de logs
LOG_FILE=./logs/app.log                   # Archivo de logs
```

### Personalización de Modelos

Puedes cambiar los modelos de OpenAI en el archivo `.env`:

```env
# Modelos más potentes (más caros)
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-large

# Modelos más rápidos (más baratos)
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
```

## 🐛 Solución de Problemas

### Error: "No module named 'src'"

```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd DocuBot-langchain-AI

# Verifica que el entorno virtual esté activado
which python  # Debe apuntar a venv/bin/python
```

### Error: "OpenAI API key not found"

```bash
# Verifica que el archivo .env existe y tiene la clave
cat .env | grep OPENAI_API_KEY

# Asegúrate de que la clave es válida
export OPENAI_API_KEY="tu_clave_aqui"
```

### Error: "Permission denied" en LanceDB

```bash
# Verifica permisos del directorio de datos
chmod -R 755 data/
ls -la data/vector_db/
```

### La aplicación no carga

```bash
# Verifica que todas las dependencias estén instaladas
pip list | grep -E "(streamlit|langchain|lancedb|openai)"

# Reinstala si es necesario
pip install -r requirements.txt --force-reinstall
```

### Problemas de memoria

```bash
# Reduce el tamaño de chunks en .env
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# O usa un modelo más pequeño
OPENAI_MODEL=gpt-3.5-turbo
```

## 📊 Rendimiento y Optimización

### Configuración Recomendada por Uso

**Para desarrollo/testing:**
```env
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=500
```

**Para producción:**
```env
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=1000
```

**Para máxima precisión:**
```env
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-large
CHUNK_SIZE=1500
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de [Solución de Problemas](#-solución-de-problemas)
2. Busca en los [Issues](https://github.com/mozadev/DocuBot-langchain-AI/issues)
3. Crea un nuevo issue con detalles del problema

## 🙏 Agradecimientos

- [LangChain](https://langchain.com) por el framework de IA
- [LanceDB](https://lancedb.com) por la base de datos vectorial
- [Streamlit](https://streamlit.io) por la interfaz web
- [OpenAI](https://openai.com) por los modelos de IA

---

**¡Disfruta usando DocuBot AI! 🚀**
