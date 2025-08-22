"""
Gestor de base de datos vectorial usando LanceDB.
Implementa almacenamiento y recuperación de embeddings de documentos.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import lancedb
import numpy as np
from langchain.schema import Document as LangChainDocument
from langchain_openai import OpenAIEmbeddings

from src.core.logger import logger, log_function_call
from config.settings import settings

class VectorStore:
    """
    Gestor de base de datos vectorial usando LanceDB.
    Maneja el almacenamiento y recuperación de embeddings de documentos.
    """
    
    def __init__(self):
        """Inicializa el gestor de base de datos vectorial."""
        self.db_path = settings.lancedb_path
        self.table_name = "documents"
        
        # Conectar a LanceDB
        self.db = lancedb.connect(self.db_path)
        
        # Inicializar embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Crear tabla si no existe
        self._create_table_if_not_exists()
        
        logger.info("VectorStore inicializado")
    
    @log_function_call
    def _create_table_if_not_exists(self):
        """Crea la tabla de documentos si no existe."""
        try:
            if self.table_name not in self.db.table_names():
                # Esquema de la tabla
                schema = {
                    "id": "string",
                    "content": "string",
                    "embedding": "float32[1536]",  # Dimensiones de OpenAI embeddings
                    "metadata": "string",  # JSON string
                    "source": "string",
                    "filename": "string",
                    "chunk_index": "int32"
                }
                
                # Crear tabla vacía
                self.db.create_table(self.table_name, schema=schema)
                logger.info(f"Tabla {self.table_name} creada")
            else:
                logger.info(f"Tabla {self.table_name} ya existe")
                
        except Exception as e:
            logger.error(f"Error creando tabla: {str(e)}")
            raise
    
    @log_function_call
    def add_documents(self, documents: List[LangChainDocument]) -> None:
        """
        Agrega documentos a la base de datos vectorial.
        
        Args:
            documents: Lista de documentos LangChain a agregar
        """
        try:
            if not documents:
                logger.warning("No hay documentos para agregar")
                return
            
            # Preparar datos para inserción
            data_to_insert = []
            
            for i, doc in enumerate(documents):
                # Generar embedding
                embedding = self.embeddings.embed_query(doc.page_content)
                
                # Preparar registro
                record = {
                    "id": f"{doc.metadata.get('filename', 'unknown')}_{i}",
                    "content": doc.page_content,
                    "embedding": embedding,
                    "metadata": str(doc.metadata),  # Convertir a string
                    "source": doc.metadata.get('source', ''),
                    "filename": doc.metadata.get('filename', ''),
                    "chunk_index": i
                }
                
                data_to_insert.append(record)
            
            # Insertar en la tabla
            table = self.db.open_table(self.table_name)
            table.add(data_to_insert)
            
            logger.info(f"Agregados {len(documents)} documentos a la base de datos")
            
        except Exception as e:
            logger.error(f"Error agregando documentos: {str(e)}")
            raise
    
    @log_function_call
    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[LangChainDocument, float]]:
        """
        Realiza búsqueda por similitud en la base de datos.
        
        Args:
            query: Consulta de búsqueda
            k: Número de resultados a retornar
            
        Returns:
            Lista de tuplas (documento, score)
        """
        try:
            # Generar embedding de la consulta
            query_embedding = self.embeddings.embed_query(query)
            
            # Realizar búsqueda
            table = self.db.open_table(self.table_name)
            
            # Búsqueda por similitud coseno
            results = table.search(query_embedding).metric("cosine").limit(k).to_list()
            
            # Convertir resultados a formato LangChain
            documents = []
            for result in results:
                # Recrear documento LangChain
                doc = LangChainDocument(
                    page_content=result['content'],
                    metadata={
                        'source': result['source'],
                        'filename': result['filename'],
                        'chunk_index': result['chunk_index'],
                        'score': result['_distance']  # Score de similitud
                    }
                )
                documents.append((doc, result['_distance']))
            
            logger.info(f"Búsqueda completada: {len(documents)} resultados")
            return documents
            
        except Exception as e:
            logger.error(f"Error en búsqueda por similitud: {str(e)}")
            raise
    
    @log_function_call
    def get_document_count(self) -> int:
        """
        Obtiene el número total de documentos en la base de datos.
        
        Returns:
            Número de documentos
        """
        try:
            table = self.db.open_table(self.table_name)
            return len(table)
        except Exception as e:
            logger.error(f"Error obteniendo conteo de documentos: {str(e)}")
            return 0
    
    @log_function_call
    def clear_database(self) -> None:
        """Limpia toda la base de datos."""
        try:
            if self.table_name in self.db.table_names():
                self.db.drop_table(self.table_name)
                self._create_table_if_not_exists()
                logger.info("Base de datos limpiada")
        except Exception as e:
            logger.error(f"Error limpiando base de datos: {str(e)}")
            raise
    
    @log_function_call
    def get_documents_by_source(self, source: str) -> List[LangChainDocument]:
        """
        Obtiene todos los documentos de una fuente específica.
        
        Args:
            source: Ruta de la fuente
            
        Returns:
            Lista de documentos
        """
        try:
            table = self.db.open_table(self.table_name)
            results = table.search().where(f"source = '{source}'").to_list()
            
            documents = []
            for result in results:
                doc = LangChainDocument(
                    page_content=result['content'],
                    metadata={
                        'source': result['source'],
                        'filename': result['filename'],
                        'chunk_index': result['chunk_index']
                    }
                )
                documents.append(doc)
            
            logger.info(f"Obtenidos {len(documents)} documentos de {source}")
            return documents
            
        except Exception as e:
            logger.error(f"Error obteniendo documentos por fuente: {str(e)}")
            raise
