"""
EVA Logging System
Sistema de logging otimizado para Windows com suporte a métricas
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
import json
from typing import Dict, Any
import orjson  # Mais rápido e suporta datetime
import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

# Configurações básicas
LOG_FORMAT = "%(levelname)s: %(message)s"
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configuração do structlog para formatação bonita
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(serializer=orjson.dumps),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

class WindowsCompatibleRotatingFileHandler(RotatingFileHandler):
    """Handler de arquivo rotativo compatível com Windows."""
    
    def rotate(self, source: str, dest: str) -> None:
        """Sobrescreve método de rotação para lidar com bloqueios do Windows."""
        try:
            if os.path.exists(dest):
                os.remove(dest)
            os.rename(source, dest)
        except Exception as e:
            print(f"Erro ao rotacionar log: {e}")

class JSONFormatter(logging.Formatter):
    """Formatador JSON com suporte a objetos datetime."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o registro de log em JSON."""
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return orjson.dumps(log_obj).decode('utf-8')

def setup_logging(
    app_name: str,
    log_level: int = logging.WARNING,
    max_bytes: int = 10_485_760,
    backup_count: int = 5,
    console: bool = True
) -> logging.Logger:
    """Configura sistema de logging."""
    
    # Cria logger
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    
    # Configura handler de arquivo
    log_file = LOG_DIR / f"{app_name}.log"
    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    
    # Configura handler de console se necessário
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        console_handler.setLevel(logging.WARNING)
        logger.addHandler(console_handler)
    
    # Configura OpenTelemetry
    trace.set_tracer_provider(TracerProvider())
    span_processor = BatchSpanProcessor(ConsoleSpanExporter())
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    return logger

# Exemplo de uso:
if __name__ == "__main__":
    logger = setup_logging("test")
    logger.info("✨ Sistema de logging iniciado") 