"""
Gestor de chat inteligente usando LangChain y OpenAI.
Implementa conversaciones con memoria y contexto de documentos.
"""

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import Document as LangChainDocument
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from src.core.logger import logger, log_function_call
from config.settings import settings

class ChatManager:
    """
    Gestor de chat inteligente que integra LangChain con OpenAI.
    Maneja conversaciones con memoria y contexto de documentos.
    """
    
    def __init__(self, vector_store):
        """
        Inicializa el gestor de chat.
        
        Args:
            vector_store: Instancia de VectorStore para búsqueda de documentos
        """
        self.vector_store = vector_store
        
        # Inicializar modelo de lenguaje
        self.llm = ChatOpenAI(
            model_name=settings.openai_model,
            temperature=settings.openai_temperature,
            openai_api_key=settings.openai_api_key
        )
        
        # Configurar memoria de conversación
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Configurar retriever con compresión contextual
        self._setup_retriever()
        
        # Configurar cadena de conversación
        self._setup_conversation_chain()
        
        logger.info("ChatManager inicializado")
    
    @log_function_call
    def _setup_retriever(self):
        """Configura el retriever con compresión contextual."""
        try:
            # Retriever base
            base_retriever = self.vector_store.similarity_search
            
            # Compresor contextual para mejorar relevancia
            compressor_prompt = PromptTemplate(
                input_variables=["question", "context"],
                template="""Dado el siguiente contexto y pregunta, extrae solo la información relevante para responder la pregunta.

Contexto: {context}
Pregunta: {question}

Información relevante:"""
            )
            
            compressor = LLMChainExtractor.from_llm(self.llm, compressor_prompt)
            
            # Retriever con compresión
            self.retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=base_retriever
            )
            
            logger.info("Retriever configurado con compresión contextual")
            
        except Exception as e:
            logger.error(f"Error configurando retriever: {str(e)}")
            raise
    
    @log_function_call
    def _setup_conversation_chain(self):
        """Configura la cadena de conversación."""
        try:
            # Prompt personalizado para el chat
            template = """Eres un asistente de IA experto en analizar documentos y responder preguntas basándote en el contenido proporcionado.

Contexto de documentos:
{context}

Historial de conversación:
{chat_history}

Pregunta del usuario: {question}

Instrucciones:
1. Responde basándote únicamente en el contexto proporcionado
2. Si no encuentras información relevante en el contexto, indícalo claramente
3. Proporciona respuestas claras y concisas
4. Cita las fuentes cuando sea apropiado
5. Mantén un tono profesional pero amigable

Respuesta:"""
            
            prompt = PromptTemplate(
                input_variables=["context", "chat_history", "question"],
                template=template
            )
            
            # Crear cadena de conversación
            self.conversation_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.retriever,
                memory=self.memory,
                combine_docs_chain_kwargs={"prompt": prompt},
                return_source_documents=True,
                verbose=settings.debug
            )
            
            logger.info("Cadena de conversación configurada")
            
        except Exception as e:
            logger.error(f"Error configurando cadena de conversación: {str(e)}")
            raise
    
    @log_function_call
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Realiza una pregunta al sistema de chat.
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Diccionario con respuesta y metadatos
        """
        try:
            if not question.strip():
                return {
                    "answer": "Por favor, proporciona una pregunta válida.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Realizar consulta
            result = self.conversation_chain({"question": question})
            
            # Extraer fuentes
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    sources.append({
                        "filename": doc.metadata.get("filename", "Desconocido"),
                        "content": doc.page_content[:200] + "...",
                        "score": doc.metadata.get("score", 0.0)
                    })
            
            # Calcular confianza basada en scores de similitud
            confidence = 0.0
            if sources:
                scores = [s["score"] for s in sources if s["score"] is not None]
                if scores:
                    confidence = sum(scores) / len(scores)
            
            response = {
                "answer": result["answer"],
                "sources": sources,
                "confidence": confidence,
                "question": question
            }
            
            logger.info(f"Pregunta respondida: {question[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error procesando pregunta: {str(e)}")
            return {
                "answer": f"Lo siento, ocurrió un error al procesar tu pregunta: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "question": question
            }
    
    @log_function_call
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Obtiene el historial de conversación.
        
        Returns:
            Lista de mensajes del historial
        """
        try:
            history = []
            for message in self.memory.chat_memory.messages:
                history.append({
                    "role": message.type,
                    "content": message.content
                })
            return history
        except Exception as e:
            logger.error(f"Error obteniendo historial: {str(e)}")
            return []
    
    @log_function_call
    def clear_memory(self) -> None:
        """Limpia la memoria de conversación."""
        try:
            self.memory.clear()
            logger.info("Memoria de conversación limpiada")
        except Exception as e:
            logger.error(f"Error limpiando memoria: {str(e)}")
            raise
    
    @log_function_call
    def get_conversation_summary(self) -> str:
        """
        Genera un resumen de la conversación actual.
        
        Returns:
            Resumen de la conversación
        """
        try:
            history = self.get_chat_history()
            if not history:
                return "No hay historial de conversación."
            
            # Crear resumen usando el LLM
            summary_prompt = f"""
            Genera un resumen conciso de la siguiente conversación:
            
            {history}
            
            Resumen:
            """
            
            response = self.llm.invoke(summary_prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generando resumen: {str(e)}")
            return "Error generando resumen de la conversación."
