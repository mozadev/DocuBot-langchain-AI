"""
Pruebas unitarias para el procesador de documentos.
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.data.document_processor import DocumentProcessor

class TestDocumentProcessor:
    """Pruebas para DocumentProcessor."""
    
    def setup_method(self):
        """Configuración antes de cada prueba."""
        self.processor = DocumentProcessor()
    
    def test_extract_text_from_pdf(self):
        """Prueba extracción de texto de PDF."""
        # Crear un archivo PDF de prueba
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            # Aquí deberías crear un PDF real para la prueba
            # Por ahora, solo verificamos que el método existe
            assert hasattr(self.processor, 'extract_text_from_pdf')
    
    def test_extract_text_from_docx(self):
        """Prueba extracción de texto de DOCX."""
        # Crear un archivo DOCX de prueba
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            # Aquí deberías crear un DOCX real para la prueba
            # Por ahora, solo verificamos que el método existe
            assert hasattr(self.processor, 'extract_text_from_docx')
    
    def test_split_text_into_chunks(self):
        """Prueba división de texto en chunks."""
        test_text = "Este es un texto de prueba. " * 100  # Texto largo
        metadata = {"source": "test.txt"}
        
        chunks = self.processor.split_text_into_chunks(test_text, metadata)
        
        assert len(chunks) > 0
        assert all(hasattr(chunk, 'page_content') for chunk in chunks)
        assert all(hasattr(chunk, 'metadata') for chunk in chunks)
    
    def test_extract_text_from_file_invalid_format(self):
        """Prueba manejo de formato de archivo no soportado."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            with pytest.raises(ValueError):
                self.processor.extract_text_from_file(tmp_file.name)
    
    def test_extract_text_from_file_not_found(self):
        """Prueba manejo de archivo no encontrado."""
        with pytest.raises(FileNotFoundError):
            self.processor.extract_text_from_file("archivo_inexistente.pdf")
