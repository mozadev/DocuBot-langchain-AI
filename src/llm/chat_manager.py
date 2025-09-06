# src/llm/chat_manager.py

from __future__ import annotations

from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from config.settings import settings
from src.core.logger import logger, log_function_call
from src.data.vector_store import VectorStoreManager, SearchResult  # ajusta si tu vector_store está en otra ruta


# --- Store de historiales por sesión (usa ChatMessageHistory, no listas) ---
class SessionHistoryStore:
    def __init__(self) -> None:
        self._store: Dict[str, InMemoryChatMessageHistory] = {}

    def get(self, session_id: str) -> InMemoryChatMessageHistory:
        hist = self._store.get(session_id)
        if hist is None:
            hist = InMemoryChatMessageHistory()
            self._store[session_id] = hist
        return hist

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)


class ChatManager:
    """
    Chat RAG con:
      - LLM OpenAI
      - Retriever consciente del historial
      - Memoria multi-turn con RunnableWithMessageHistory
    """

    def __init__(self, vector_store: VectorStoreManager, session_id: str = "default") -> None:
        self.vector_store = vector_store
        self.session_id = session_id

        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key,
        )

        # Retriever (¡siempre .as_retriever()!)
        self.retriever = self.vector_store.as_retriever(k=4)

        # Prompt para reescribir la pregunta con historial
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Reescribe la última consulta como una pregunta independiente. "
                       "Usa el historial sólo si ayuda. No inventes datos."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        # Prompt de QA con contexto documental
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Responde exclusivamente usando el contexto provisto.\n\n"
             "Contexto:\n{context}\n\n"
             "Si no hay contexto relevante, dilo explícitamente."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        # Cadena RAG con historial
        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, self.contextualize_q_prompt
        )
        self.doc_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.doc_chain)

        # Memoria tipo ChatMessageHistory
        self._history_store = SessionHistoryStore()

        # Wrapper que gestiona el historial automáticamente
        self.chat = RunnableWithMessageHistory(
            self.rag_chain,
            lambda session_id: self._history_store.get(session_id),
            input_messages_key="input",           # el input del usuario
            history_messages_key="chat_history",  # coincide con MessagesPlaceholder
            output_messages_key="answer",         # añade la respuesta al historial
        )

        logger.info("ChatManager inicializado (LCEL).")

    @log_function_call
    def ask_question(self, question: str) -> Dict[str, Any]:
        if not question or not question.strip():
            return {"answer": "Por favor, proporciona una pregunta válida.", "sources": [], "confidence": 0.0}

        # Ejecuta la cadena con el historial de la sesión
        result = self.chat.invoke(
            {"input": question},
            config={"configurable": {"session_id": self.session_id}},
        )
        answer_text = result.get("answer", "")

        # Fuentes + “confianza” (opcional)
        scored = self.vector_store.similarity_search_with_scores(question, k=4)
        sources = [{
            "filename": sr.doc.metadata.get("filename", "Desconocido"),
            "content": (sr.doc.page_content[:200] + "...") if sr.doc.page_content else "",
            "score": sr.score,
        } for sr in scored]
        confidence = float(sum(s["score"] for s in sources) / len(sources)) if sources else 0.0

        logger.info(f"Pregunta respondida: {question[:80]}...")
        return {"answer": answer_text, "sources": sources, "confidence": confidence, "question": question}

    @log_function_call
    def get_chat_history(self) -> List[Dict[str, str]]:
        hist = self._history_store.get(self.session_id)
        return [{"role": m.type, "content": m.content} for m in hist.messages]

    @log_function_call
    def clear_memory(self) -> None:
        self._history_store.clear(self.session_id)
        logger.info("Memoria de conversación limpiada")

    @log_function_call
    def get_conversation_summary(self) -> str:
        hist = self._history_store.get(self.session_id)
        if not hist.messages:
            return "No hay historial de conversación."
        messages = [
            ("system", "Resume la conversación de forma breve y fiel al contenido."),
            ("human", str([{"role": m.type, "content": m.content} for m in hist.messages])),
        ]
        return self.llm.invoke(messages).content
