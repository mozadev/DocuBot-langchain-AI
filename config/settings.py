
"""
Configuración principal del proyecto DocuBot AI (Pydantic v2 + pydantic-settings).
"""

import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (si existe)
load_dotenv()

class Settings(BaseSettings):
    # Pydantic Settings v2: configuración del modelo/entorno
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",         # ignora claves desconocidas en .env
        case_sensitive=False    # variables de entorno no sensibles a mayúsc/minúsc
    )

    # --- OpenAI ---
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")
    openai_temperature: float = Field(0.2, alias="OPENAI_TEMPERATURE")

    # --- LanceDB ---
    lancedb_path: str = Field("./data/vector_db", alias="LANCE_DB_PATH")
    lancedb_table: str = Field("documents", alias="LANCE_DB_TABLE")

    # --- App ---
    app_name: str = Field("DocuBot AI", alias="APP_NAME")
    debug: bool = Field(False, alias="DEBUG")

    # --- Embeddings / chunking ---
    embedding_model: str = Field("text-embedding-3-small", alias="EMBEDDING_MODEL")
    chunk_size: int = Field(1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(200, alias="CHUNK_OVERLAP")

    # --- Logging ---
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_file: str = Field("./logs/app.log", alias="LOG_FILE")


# Instancia global de configuración
settings = Settings()

# Crear directorios necesarios
os.makedirs(settings.lancedb_path, exist_ok=True)
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
