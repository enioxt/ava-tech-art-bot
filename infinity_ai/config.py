import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do Bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "AvaTechArtBot")
BOT_NAME = os.getenv("BOT_NAME", "AVA - Tech & Art")

# Configurações do Sistema
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENV = os.getenv("ENV", "development")

# Configurações de Imagem
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "800"))
ALLOWED_FORMATS = ["JPEG", "PNG", "GIF"]
OUTPUT_QUALITY = int(os.getenv("OUTPUT_QUALITY", "85"))

# Configurações de Cache
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "false").lower() == "true"
CACHE_DURATION = int(os.getenv("CACHE_DURATION", "3600"))

# Configurações de Rate Limit
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", "50"))

def validate_config():
    """Valida as configurações essenciais."""
    if not BOT_TOKEN:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN não configurado no .env")
    
    return True 