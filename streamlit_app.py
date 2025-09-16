"""
Aplicación principal de DocuBot AI usando Streamlit (LCEL).
Interfaz web moderna para procesamiento de documentos y chat inteligente.
"""

import os
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st

# --- Módulos del proyecto (ajusta rutas si tu árbol difiere) ---
from src.data.document_processor import DocumentProcessor  # usa langchain_core.documents.Document
from src.data.vector_store import VectorStoreManager   # LanceDB + OpenAIEmbeddings
from src.llm.chat_manager import ChatManager          # LCEL (history-aware retriever)
from src.core.logger import logger
from config.settings import settings

# --------- Config de página ----------
st.set_page_config(
    page_title="DocuBot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------- CSS ----------
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


# --------- Helpers internos ----------
def _safe_doc_count(vs: VectorStoreManager) -> int:
    """Obtiene el conteo de documentos si el VectorStore lo expone; si no, intenta abrir la tabla LanceDB.
    Devuelve 0 si no puede determinarlo (no rompe la UI)."""
    try:
        if hasattr(vs, "get_document_count"):
            return int(vs.get_document_count())  # si implementaste este método en VectorStoreManager
    except Exception:
        pass
    # Fallback best-effort (no obligatorio)
    try:
        if hasattr(vs, "_db") and hasattr(settings, "lancedb_table"):
            tbl = vs._db.open_table(settings.lancedb_table)
            # Algunas versiones de lancedb exponen count_rows() o __len__()
            if hasattr(tbl, "count_rows"):
                return int(tbl.count_rows())
            try:
                return int(len(tbl))  # puede no estar disponible
            except Exception:
                return 0
    except Exception:
        return 0
    return 0


@st.cache_resource
def initialize_components():
    """
    Inicializa los componentes principales (una sola vez por sesión).
    """
    try:
        document_processor = DocumentProcessor()
        vector_store = VectorStoreManager()
        # Sesión lógica para memoria de chat (puedes usar el user_id real si lo tienes)
        session_id = "streamlit_user"
        chat_manager = ChatManager(vector_store=vector_store, session_id=session_id)

        logger.info("Componentes de la aplicación inicializados")
        return document_processor, vector_store, chat_manager

    except Exception as e:
        st.error(f"Error inicializando componentes: {str(e)}")
        logger.error(f"Error inicializando componentes: {str(e)}")
        return None, None, None


def display_chat_message(message: Dict[str, Any], is_user: bool = False):
    """
    Muestra un mensaje de chat con formato.
    """
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 Tú:</strong><br>
            {message.get('question','')}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 DocuBot:</strong><br>
            {message.get('answer','')}
        </div>
        """, unsafe_allow_html=True)

        # Barra de confianza
        if 'confidence' in message and message['confidence'] > 0:
            confidence_percent = min(float(message['confidence']) * 100, 100)
            st.markdown(f"""
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {confidence_percent:.2f}%"></div>
            </div>
            <small>Confianza: {confidence_percent:.1f}%</small>
            """, unsafe_allow_html=True)

        # Fuentes
        if message.get('sources'):
            with st.expander("📚 Ver fuentes"):
                for i, source in enumerate(message['sources']):
                    fname = source.get('filename', 'Desconocido')
                    content = source.get('content', '')
                    score = source.get('score', 0.0)
                    st.markdown(f"""
                    <div class="source-info">
                        <strong>Fuente {i+1}:</strong> {fname}<br>
                        <strong>Contenido:</strong> {content}<br>
                        <strong>Score:</strong> {score:.3f}
                    </div>
                    """, unsafe_allow_html=True)


def main():
    """Punto de entrada de la app."""
    st.markdown('<h1 class="main-header">🤖 DocuBot AI</h1>', unsafe_allow_html=True)
    st.markdown("### Sistema de IA Empresarial para Análisis de Documentos (RAG con LanceDB + LCEL)")

    document_processor, vector_store, chat_manager = initialize_components()
    if not all([document_processor, vector_store, chat_manager]):
        st.error("Error al inicializar la aplicación. Verifica tu configuración.")
        return

    # --------- Sidebar ----------
    with st.sidebar:
        st.header("⚙️ Configuración")

        doc_count = _safe_doc_count(vector_store)
        st.metric("Documentos en BD", doc_count)

        if st.button("🗑️ Limpiar Base de Datos"):
            with st.spinner("Limpiando base de datos..."):
                try:
                    # Si implementaste clear_database() en VectorStoreManager, úsalo:
                    if hasattr(vector_store, "clear_database"):
                        vector_store.clear_database()
                    else:
                        st.warning("clear_database() no está implementado en VectorStoreManager.")
                    chat_manager.clear_memory()
                    st.success("Base de datos y memoria limpiadas.")
                    st.rerun()
                except Exception as e:
                    st.error(f"No se pudo limpiar la base de datos: {e}")

        if st.button("🧠 Limpiar Memoria de Chat"):
            chat_manager.clear_memory()
            st.success("Memoria de chat limpiada")
            st.rerun()

        st.header("ℹ️ Información")
        st.info(f"Modelo: {settings.openai_model}")
        st.info(f"Embeddings: {settings.embedding_model}")
        st.info(f"Chunk Size: {settings.chunk_size}")

    # --------- Tabs ----------
    tab1, tab2, tab3 = st.tabs(["📄 Subir Documentos", "💬 Chat", "📊 Análisis"])

    # ---- Tab 1: Upload ----
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
                            suffix = f".{uploaded_file.name.split('.')[-1].lower()}"
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_path = tmp_file.name

                            # Extrae y parte en chunks (LangChain Document moderno)
                            chunks = document_processor.process_document(tmp_path)

                            # Indexa en LanceDB
                            added = vector_store.add_documents(chunks)
                            total_chunks += int(added)

                            os.unlink(tmp_path)
                            st.success(f"✅ {uploaded_file.name} procesado ({len(chunks)} chunks)")
                        except Exception as e:
                            st.error(f"❌ Error procesando {uploaded_file.name}: {str(e)}")

                    st.success(f"🎉 Procesamiento completado. Total: {total_chunks} chunks")
                    st.rerun()

    # ---- Tab 2: Chat ----
    with tab2:
        st.header("💬 Chat Inteligente")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                display_chat_message(message, is_user=message.get('is_user', False))

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
                        st.session_state.chat_history.append({'question': question, 'is_user': True})
                        with st.spinner("🤔 Pensando..."):
                            response = chat_manager.ask_question(question)
                        st.session_state.chat_history.append(response)
                        st.rerun()

            with col2:
                if st.button("📝 Generar Resumen"):
                    with st.spinner("Generando resumen..."):
                        summary = chat_manager.get_conversation_summary()
                        st.info(f"**Resumen de la conversación:**\n\n{summary}")

    # ---- Tab 3: Análisis ----
    with tab3:
        st.header("📊 Análisis y Estadísticas")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Estadísticas de la Base de Datos")
            doc_count = _safe_doc_count(vector_store)
            st.metric("Total de Chunks", doc_count)
            st.success("✅ Base de datos activa" if doc_count > 0 else "⚠️ No hay documentos en la base")

        with col2:
            st.subheader("🔍 Información del Sistema")
            config_info = {
                "Modelo LLM": settings.openai_model,
                "Modelo Embeddings": settings.embedding_model,
                "Tamaño de Chunk": settings.chunk_size,
                "Overlap de Chunk": settings.chunk_overlap,
                "Temperatura": settings.openai_temperature
            }
            for key, value in config_info.items():
                st.text(f"{key}: {value}")

        st.subheader("💭 Historial de Conversación")
        if st.session_state.chat_history:
            history_data = []
            for i, message in enumerate(st.session_state.chat_history):
                if not message.get('is_user', False):
                    history_data.append({
                        "Pregunta": message.get('question', ''),
                        "Respuesta": (message.get('answer', '')[:100] + "...") if message.get('answer') else "",
                        "Confianza": f"{float(message.get('confidence', 0.0)):.2f}",
                        "Fuentes": len(message.get('sources', [])) if message.get('sources') else 0
                    })
            if history_data:
                st.dataframe(history_data, use_container_width=True)
        else:
            st.info("No hay historial de conversación disponible.")


if __name__ == "__main__":
    main()
