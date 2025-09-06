# src/services/vector_store.py

from __future__ import annotations

from typing import List, Optional, Sequence
from dataclasses import dataclass

from langchain_core.documents import Document  # Documento estándar LCEL
from langchain_openai import OpenAIEmbeddings  # Embeddings OpenAI modernos
from langchain_community.vectorstores import LanceDB  # VectorStore LanceDB
import lancedb

from config.settings import settings
from src.core.logger import logger


@dataclass
class SearchResult:
    """Contenedor tipado con documento y score de relevancia."""
    doc: Document
    score: float


class VectorStoreManager:
    """
    Capa de acceso al VectorStore (LanceDB) con una interfaz simple.
    - Conecta/crea tabla si falta.
    - Indexa y consulta documentos.
    - Expone retriever estándar para LangChain.
    - Incluye utilidades para la UI (conteo y limpieza).
    """

    def __init__(self) -> None:
        # Embeddings OpenAI (toma API key desde settings/env)
        self._emb = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=getattr(settings, "openai_api_key", None),
        )

        # Conexión física a LanceDB (directorio en disco)
        self._db = lancedb.connect(settings.lancedb_path)

        # Nombre de la tabla (permite múltiples colecciones)
        self._table_name = getattr(settings, "lancedb_table", "documents")

        # Instancia del VectorStore (lazy si la tabla aún no existe)
        self._vs: Optional[LanceDB] = None

        # Si la tabla existe, inicializa el VectorStore de una vez
        try:
            self._db.open_table(self._table_name)
            self._vs = self._init_vectorstore()
            logger.info(f"LanceDB: tabla '{self._table_name}' abierta e inicializada.")
        except Exception:
            logger.info(
                f"LanceDB: la tabla '{self._table_name}' no existe aún; "
                f"se creará automáticamente al indexar."
            )

    # ---- helpers internos ----

    def _init_vectorstore(self) -> LanceDB:
        """
        Crea el VectorStore apuntando a la conexión actual.
        Incluye fallback por diferencias de firma entre versiones.
        """
        try:
            # Firmas nuevas suelen aceptar table_name
            return LanceDB(connection=self._db, embedding=self._emb, table_name=self._table_name)
        except TypeError:
            # Fallback para firmas antiguas
            logger.warning(
                "VectorStore LanceDB inicializado sin 'table_name' (firma antigua). "
                "Se usará la tabla por defecto del vectorstore."
            )
            return LanceDB(connection=self._db, embedding=self._emb)

    def _ensure_vs(self) -> None:
        """Crea la tabla/VectorStore si aún no existe (lazy init)."""
        if self._vs is None:
            self._vs = self._init_vectorstore()
            logger.info("VectorStore LanceDB inicializado (lazy).")

    # ---- API pública usada por tu app ----

    def add_documents(self, docs: Sequence[Document]) -> int:
        """
        Indexa documentos ya 'chunked'.
        Devuelve cuántos documentos se añadieron.
        """
        self._ensure_vs()
        if not docs:
            return 0
        self._vs.add_documents(list(docs))
        logger.info(f"{len(docs)} chunks indexados en LanceDB (tabla '{self._table_name}').")
        return len(docs)

    def similarity_search_with_scores(self, query: str, k: int = 4) -> List[SearchResult]:
        """
        Búsqueda semántica con puntaje de relevancia (0..1 aprox).
        """
        self._ensure_vs()
        results = self._vs.similarity_search_with_relevance_scores(query, k=k)
        # results: List[Tuple[Document, float]]
        return [SearchResult(doc=doc, score=float(score)) for doc, score in results]

    def as_retriever(self, k: int = 4):
        """
        Exposición como retriever estándar de LangChain (para create_retrieval_chain).
        """
        self._ensure_vs()
        return self._vs.as_retriever(search_kwargs={"k": k})

    # ---- utilidades para la UI (sidebar) ----

    def get_document_count(self) -> int:
        """
        Devuelve el número de filas almacenadas en la tabla LanceDB.
        Usa count_rows() si existe; si no, intenta len().
        """
        try:
            tbl = self._db.open_table(self._table_name)
            if hasattr(tbl, "count_rows"):
                return int(tbl.count_rows())
            try:
                return int(len(tbl))  # fallback
            except Exception:
                return 0
        except Exception:
            return 0

    def clear_database(self) -> None:
        """
        Elimina la tabla de LanceDB usada por esta instancia y
        reinicia el VectorStore para recrearlo en el próximo uso.
        """
        try:
            self._db.drop_table(self._table_name)
            logger.info(f"LanceDB: tabla '{self._table_name}' eliminada.")
        except Exception as e:
            logger.warning(f"No se pudo eliminar la tabla '{self._table_name}': {e}")
        # Resetea para lazy-creation en la próxima operación
        self._vs = None
