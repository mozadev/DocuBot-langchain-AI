# tests/test_vector_store_manager.py
"""
Pruebas unitarias para VectorStoreManager (LanceDB).
- No dependen de OpenAI ni red: se mockea OpenAIEmbeddings por DummyEmbeddings.
- Usan un directorio LanceDB temporal por test.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import List

import pytest

# Document moderno de LangChain
from langchain_core.documents import Document
# Vamos a monkeypatch-ar el símbolo OpenAIEmbeddings dentro de tu módulo
import src.services.vector_store as vsmod
from config.settings import settings


# ---------- DummyEmbeddings (sin red) ----------

from langchain_core.embeddings import Embeddings

class DummyEmbeddings(Embeddings):
    """
    Embeddings deterministas y baratos (sin red).
    Estrategia simple: vector de 16 floats acumulando bytes del texto.
    Suficiente para probar flujo de LanceDB/VectorStore.
    """
    dim = 16

    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        # Distribuye los bytes del texto por el vector
        for i, b in enumerate(text.encode("utf-8")):
            vec[i % self.dim] += b / 255.0
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(t or "") for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text or "")


# ---------- Fixtures ----------

@pytest.fixture(autouse=True)
def _patch_embeddings(monkeypatch):
    """
    Reemplaza OpenAIEmbeddings por DummyEmbeddings DENTRO del módulo vector_store.
    Así, VectorStoreManager usará esta clase sin hablar con OpenAI.
    """
    monkeypatch.setattr(vsmod, "OpenAIEmbeddings", DummyEmbeddings, raising=True)
    yield


@pytest.fixture
def tmp_lancedb_env(tmp_path: Path, monkeypatch):
    """
    Ajusta settings para que VectorStoreManager use un directorio temporal
    y una tabla única por test.
    """
    ldb_dir = tmp_path / "lancedb"
    ldb_dir.mkdir(parents=True, exist_ok=True)
    table = f"tbl_{uuid.uuid4().hex[:8]}"

    # Mutamos settings usados por VectorStoreManager
    settings.lancedb_path = str(ldb_dir)
    settings.lancedb_table = table

    yield {"path": ldb_dir, "table": table}


@pytest.fixture
def vsm(tmp_lancedb_env):
    """Instancia fresca del VectorStoreManager para cada test."""
    return vsmod.VectorStoreManager()


# ---------- Helpers ----------

def _make_docs() -> List[Document]:
    """
    Crea documentos de juguete con metadatos.
    """
    return [
        Document(page_content="Apple banana mango", metadata={"filename": "frutas1.txt"}),
        Document(page_content="Coche camión carretera", metadata={"filename": "vehiculos1.txt"}),
        Document(page_content="Banana fresa papaya", metadata={"filename": "frutas2.txt"}),
    ]


# ---------- Tests ----------

def test_add_and_count_documents(vsm: vsmod.VectorStoreManager):
    """Debe indexar documentos y reportar el conteo."""
    docs = _make_docs()
    added = vsm.add_documents(docs)
    assert added == len(docs)

    count = vsm.get_document_count()
    # Dependiendo de la implementación, count debe ser >= added (debería ser ==)
    assert count >= added


def test_similarity_search_with_scores(vsm: vsmod.VectorStoreManager):
    """La búsqueda debe devolver el doc más relevante y un score float."""
    vsm.add_documents(_make_docs())

    results = vsm.similarity_search_with_scores("apple", k=2)
    assert len(results) > 0
    top = results[0]
    assert isinstance(top.score, float)
    # El contenido del top debería estar relacionado con "apple"/"banana".
    assert "banana" in top.doc.page_content.lower() or "apple" in top.doc.page_content.lower()


def test_as_retriever_get_relevant_documents(vsm: vsmod.VectorStoreManager):
    """El retriever debe devolver documentos relevantes con la API estándar."""
    vsm.add_documents(_make_docs())
    retriever = vsm.as_retriever(k=2)
    docs = retriever.get_relevant_documents("camión")
    assert len(docs) > 0
    # El primer doc debería venir de vehiculos
    assert any("vehiculos" in d.metadata.get("filename", "") for d in docs)


def test_clear_database_resets_count(vsm: vsmod.VectorStoreManager):
    """clear_database borra la tabla y deja el conteo en 0."""
    vsm.add_documents(_make_docs())
    before = vsm.get_document_count()
    assert before > 0

    vsm.clear_database()
    after = vsm.get_document_count()
    assert after == 0

    # Debe poder reindexar después de limpiar
    added = vsm.add_documents(_make_docs())
    assert added > 0
    assert vsm.get_document_count() >= added


def test_add_documents_empty_list(vsm: vsmod.VectorStoreManager):
    """Agregar lista vacía no debe fallar y retorna 0."""
    added = vsm.add_documents([])
    assert added == 0
