# tests/test_document_processor.py
"""
Pruebas unitarias para el procesador de documentos.
"""

import os
from pathlib import Path

import pytest

from src.data.document_processor import DocumentProcessor


# ---------- Fixtures ----------

@pytest.fixture(scope="function")
def processor():
    """Instancia fresca por test."""
    return DocumentProcessor()


# ---------- Helpers ----------

def _create_docx(path: Path, lines=None):
    from docx import Document
    doc = Document()
    for line in (lines or ["Hola", "Este es un DOCX de prueba"]):
        doc.add_paragraph(line)
    doc.save(path)


def _create_pdf_with_reportlab(path: Path, text: str = "Hola - PDF de prueba"):
    """
    Crea un PDF simple usando reportlab. Si reportlab no está instalado, este helper no se usa.
    """
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(path), pagesize=LETTER)
    width, height = LETTER
    # Escribimos texto en una posición visible
    c.drawString(100, height - 100, text)
    c.showPage()
    c.save()


# ---------- Tests ----------

def test_extract_text_from_docx_real(tmp_path: Path, processor: DocumentProcessor):
    """Debe extraer texto de un DOCX real."""
    fpath = tmp_path / "sample.docx"
    _create_docx(fpath, ["Hola mundo", "Segundo párrafo"])
    extracted = processor.extract_text_from_docx(str(fpath))
    assert "Hola mundo" in extracted
    assert "Segundo párrafo" in extracted


def test_extract_text_from_pdf_real(tmp_path: Path, processor: DocumentProcessor):
    """Debe extraer texto de un PDF real (salta si no hay reportlab)."""
    reportlab = pytest.importorskip("reportlab", reason="Instala reportlab para probar extracción de PDF real.")
    fpath = tmp_path / "sample.pdf"
    _create_pdf_with_reportlab(fpath, "Texto PDF de prueba")
    extracted = processor.extract_text_from_pdf(str(fpath))
    # La extracción puede normalizar espacios/saltos; validamos con un substring robusto
    assert "Texto" in extracted and "prueba" in extracted


def test_split_text_into_chunks(processor: DocumentProcessor):
    """Divide un texto largo en chunks (Document de LCEL con metadata)."""
    test_text = "Este es un texto de prueba. " * 200
    metadata = {"source": "test.txt"}

    chunks = processor.split_text_into_chunks(test_text, metadata)

    assert len(chunks) > 0
    # Cada chunk debe ser un Document con page_content y metadata
    for ch in chunks:
        assert hasattr(ch, "page_content")
        assert isinstance(ch.page_content, str)
        assert hasattr(ch, "metadata")
        assert isinstance(ch.metadata, dict)
        # metadata original se propaga
        assert ch.metadata.get("source") == "test.txt"


def test_process_document_docx_metadata(tmp_path: Path, processor: DocumentProcessor):
    """process_document debe retornar chunks con metadatos completos para DOCX."""
    fpath = tmp_path / "informe.docx"
    _create_docx(fpath, ["Linea 1", "Linea 2"])

    chunks = processor.process_document(str(fpath))
    assert len(chunks) > 0

    # Valida metadatos enriquecidos que agrega process_document
    any_chunk = chunks[0]
    md = any_chunk.metadata
    assert md.get("filename") == "informe.docx"
    assert md.get("file_type") == ".docx"
    assert isinstance(md.get("file_size"), int)
    assert md.get("source") == str(fpath)


def test_extract_text_from_file_invalid_format(tmp_path: Path, processor: DocumentProcessor):
    """Lanza ValueError para formatos no soportados."""
    fpath = tmp_path / "no_soportado.txt"
    fpath.write_text("texto plano")
    with pytest.raises(ValueError):
        processor.extract_text_from_file(str(fpath))


def test_extract_text_from_file_not_found(processor: DocumentProcessor):
    """Lanza FileNotFoundError si el archivo no existe."""
    with pytest.raises(FileNotFoundError):
        processor.extract_text_from_file("archivo_inexistente.pdf")
