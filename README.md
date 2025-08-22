# DocuBot AI - Sistema de IA Empresarial

## Descripción
Sistema de IA empresarial que demuestra las mejores prácticas de desarrollo en Python, LangChain, LanceDB y Streamlit. Este proyecto implementa un chatbot inteligente que puede procesar documentos y responder preguntas basándose en el contenido.

## Arquitectura del Proyecto

```
docubot-ai/
├── src/                    # Código fuente principal
│   ├── core/              # Lógica de negocio central
│   ├── data/              # Manejo de datos y vectores
│   ├── llm/               # Integración con LLMs
│   └── ui/                # Interfaz de usuario
├── tests/                 # Pruebas unitarias
├── config/                # Configuraciones
├── data/                  # Datos de ejemplo
├── requirements.txt       # Dependencias
└── streamlit_app.py       # Aplicación principal
```

## Tecnologías Utilizadas

- **Python 3.9+**: Lenguaje principal
- **LangChain**: Framework para aplicaciones de IA
- **LanceDB**: Base de datos vectorial de alto rendimiento
- **OpenAI API**: Modelo de lenguaje
- **Streamlit**: Interfaz de usuario
- **Pydantic**: Validación de datos
- **Logging**: Sistema de logs empresarial

## Instalación

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables de entorno
4. Ejecutar: `streamlit run streamlit_app.py`

## Características Principales

- ✅ Procesamiento de documentos PDF/DOCX
- ✅ Embeddings vectoriales con LanceDB
- ✅ Chat inteligente con memoria
- ✅ Interfaz web moderna
- ✅ Logging y monitoreo
- ✅ Configuración flexible
- ✅ Pruebas unitarias
- ✅ Documentación completa
