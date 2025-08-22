"""
Sistema de logging empresarial para DocuBot AI.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from config.settings import settings

class CustomFormatter(logging.Formatter):
    """
    Formateador personalizado para logs con colores y estructura clara.
    """
    
    # Colores para diferentes niveles de log
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Agregar timestamp
        record.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Agregar color si es terminal
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

def setup_logger(name: str = "docubot", level: Optional[str] = None) -> logging.Logger:
    """
    Configura el logger principal de la aplicación.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level or settings.log_level))
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Formato para consola
    console_format = CustomFormatter(
        '%(timestamp)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Formato para archivo (más detallado)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger

# Logger principal de la aplicación
logger = setup_logger()

def log_function_call(func):
    """
    Decorador para logging automático de llamadas a funciones.
    Útil para debugging y monitoreo.
    """
    def wrapper(*args, **kwargs):
        logger.debug(f"Llamando función: {func.__name__} con args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Función {func.__name__} completada exitosamente")
            return result
        except Exception as e:
            logger.error(f"Error en función {func.__name__}: {str(e)}")
            raise
    return wrapper
