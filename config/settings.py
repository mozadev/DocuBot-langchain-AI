"""
Configuración principal del proyecto DocuBot AI.
Sigue las mejores prácticas de configuración empresarial.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings(BaseSettings):
    """
    Configuración centralizada del proyecto.
    Utiliza Pydantic para validación automática de tipos.
    """
    
    # Configuración de OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # Configuración de LanceDB
    lancedb_path: str = Field(default="./data/vector_db", env="LANCE_DB_PATH")
    
    # Configuración de la aplicación
    app_name: str = Field(default="DocuBot AI", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Configuración de embeddings
    embedding_model: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Configuración de logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Ignorar campos extra
    }

# Instancia global de configuración
settings = Settings()

# Crear directorios necesarios
os.makedirs(settings.lancedb_path, exist_ok=True)
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
