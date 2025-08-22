"""
Aplicación principal de DocuBot AI usando Streamlit.
Interfaz web moderna para procesamiento de documentos y chat inteligente.
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import json

# Importar módulos del proyecto
from src.data.document_processor import DocumentProcessor
from src.data.vector_store import VectorStore
from src.llm.chat_manager import ChatManager
from src.core.logger import logger
from config.settings import settings

# Configuración de la página
st.set_page_config(
    page_title="DocuBot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .source-info {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    .confidence-bar {
        background-color: #e0e0e0;
        border-radius: 0.25rem;
        height: 0.5rem;
        margin: 0.5rem 0;
    }
    .confidence-fill {
        background-color: #4caf50;
        height: 100%;
        border-radius: 0.25rem;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_components():
    """
    Inicializa los componentes principales de la aplicación.
    Usa cache para evitar reinicialización innecesaria.
    """
    try:
        # Inicializar componentes
        document_processor = DocumentProcessor()
        vector_store = VectorStore()
        chat_manager = ChatManager(vector_store)
        
        logger.info("Componentes de la aplicación inicializados")
        return document_processor, vector_store, chat_manager
        
    except Exception as e:
        st.error(f"Error inicializando componentes: {str(e)}")
        logger.error(f"Error inicializando componentes: {str(e)}")
        return None, None, None

def display_chat_message(message: Dict[str, Any], is_user: bool = False):
    """
    Muestra un mensaje de chat con formato personalizado.
    
    Args:
        message: Diccionario con el mensaje
        is_user: Si es mensaje del usuario
    """
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 Tú:</strong><br>
            {message['question']}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Mostrar respuesta del bot
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 DocuBot:</strong><br>
            {message['answer']}
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar barra de confianza
        if 'confidence' in message and message['confidence'] > 0:
            confidence_percent = min(message['confidence'] * 100, 100)
            st.markdown(f"""
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {confidence_percent}%"></div>
            </div>
            <small>Confianza: {confidence_percent:.1f}%</small>
            """, unsafe_allow_html=True)
        
        # Mostrar fuentes si existen
        if 'sources' in message and message['sources']:
            with st.expander("📚 Ver fuentes"):
                for i, source in enumerate(message['sources']):
                    st.markdown(f"""
                    <div class="source-info">
                        <strong>Fuente {i+1}:</strong> {source['filename']}<br>
                        <strong>Contenido:</strong> {source['content']}<br>
                        <strong>Score:</strong> {source['score']:.3f}
                    </div>
                    """, unsafe_allow_html=True)

def main():
    """Función principal de la aplicación."""
    
    # Título principal
    st.markdown('<h1 class="main-header">🤖 DocuBot AI</h1>', unsafe_allow_html=True)
    st.markdown("### Sistema de IA Empresarial para Análisis de Documentos")
    
    # Inicializar componentes
    document_processor, vector_store, chat_manager = initialize_components()
    
    if not all([document_processor, vector_store, chat_manager]):
        st.error("Error al inicializar la aplicación. Verifica tu configuración.")
        return
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Estadísticas de la base de datos
        doc_count = vector_store.get_document_count()
        st.metric("Documentos en BD", doc_count)
        
        # Botones de control
        if st.button("🗑️ Limpiar Base de Datos"):
            with st.spinner("Limpiando base de datos..."):
                vector_store.clear_database()
                chat_manager.clear_memory()
                st.success("Base de datos limpiada")
                st.rerun()
        
        if st.button("🧠 Limpiar Memoria de Chat"):
            chat_manager.clear_memory()
            st.success("Memoria de chat limpiada")
            st.rerun()
        
        # Información del sistema
        st.header("ℹ️ Información")
        st.info(f"Modelo: {settings.openai_model}")
        st.info(f"Embeddings: {settings.embedding_model}")
        st.info(f"Chunk Size: {settings.chunk_size}")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["📄 Subir Documentos", "💬 Chat", "📊 Análisis"])
    
    # Tab 1: Subir Documentos
    with tab1:
        st.header("📄 Procesamiento de Documentos")
        
        uploaded_files = st.file_uploader(
            "Selecciona archivos PDF o DOCX",
            type=['pdf', 'docx'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("🚀 Procesar Documentos"):
                with st.spinner("Procesando documentos..."):
                    total_chunks = 0
                    
                    for uploaded_file in uploaded_files:
                        try:
                            # Guardar archivo temporalmente
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_file_path = tmp_file.name
                            
                            # Procesar documento
                            chunks = document_processor.process_document(tmp_file_path)
                            
                            # Agregar a la base de datos
                            vector_store.add_documents(chunks)
                            
                            total_chunks += len(chunks)
                            
                            # Limpiar archivo temporal
                            os.unlink(tmp_file_path)
                            
                            st.success(f"✅ {uploaded_file.name} procesado ({len(chunks)} chunks)")
                            
                        except Exception as e:
                            st.error(f"❌ Error procesando {uploaded_file.name}: {str(e)}")
                    
                    st.success(f"🎉 Procesamiento completado. Total: {total_chunks} chunks")
                    st.rerun()
    
    # Tab 2: Chat
    with tab2:
        st.header("💬 Chat Inteligente")
        
        # Inicializar historial de chat en session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Mostrar historial de chat
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                display_chat_message(message, is_user=message.get('is_user', False))
        
        # Input para nueva pregunta
        with st.container():
            question = st.text_input(
                "Haz una pregunta sobre tus documentos:",
                placeholder="Ej: ¿Qué dice el documento sobre...?",
                key="question_input"
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🚀 Enviar", type="primary"):
                    if question.strip():
                        # Agregar pregunta al historial
                        st.session_state.chat_history.append({
                            'question': question,
                            'is_user': True
                        })
                        
                        # Obtener respuesta
                        with st.spinner("🤔 Pensando..."):
                            response = chat_manager.ask_question(question)
                        
                        # Agregar respuesta al historial
                        st.session_state.chat_history.append(response)
                        
                        # Limpiar input
                        st.session_state.question_input = ""
                        st.rerun()
            
            with col2:
                if st.button("📝 Generar Resumen"):
                    with st.spinner("Generando resumen..."):
                        summary = chat_manager.get_conversation_summary()
                        st.info(f"**Resumen de la conversación:**\n\n{summary}")
    
    # Tab 3: Análisis
    with tab3:
        st.header("📊 Análisis y Estadísticas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Estadísticas de la Base de Datos")
            
            # Estadísticas básicas
            doc_count = vector_store.get_document_count()
            st.metric("Total de Chunks", doc_count)
            
            if doc_count > 0:
                st.success("✅ Base de datos activa")
            else:
                st.warning("⚠️ No hay documentos en la base de datos")
        
        with col2:
            st.subheader("🔍 Información del Sistema")
            
            # Información de configuración
            config_info = {
                "Modelo LLM": settings.openai_model,
                "Modelo Embeddings": settings.embedding_model,
                "Tamaño de Chunk": settings.chunk_size,
                "Overlap de Chunk": settings.chunk_overlap,
                "Temperatura": settings.openai_temperature
            }
            
            for key, value in config_info.items():
                st.text(f"{key}: {value}")
        
        # Historial de conversación
        st.subheader("💭 Historial de Conversación")
        if st.session_state.chat_history:
            history_data = []
            for i, message in enumerate(st.session_state.chat_history):
                if not message.get('is_user', False):
                    history_data.append({
                        "Pregunta": message.get('question', ''),
                        "Respuesta": message.get('answer', '')[:100] + "...",
                        "Confianza": f"{message.get('confidence', 0):.2f}",
                        "Fuentes": len(message.get('sources', []))
                    })
            
            if history_data:
                st.dataframe(history_data, use_container_width=True)
        else:
            st.info("No hay historial de conversación disponible.")

if __name__ == "__main__":
    main()
