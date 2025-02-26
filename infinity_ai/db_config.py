import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mongodb.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MongoDB')

load_dotenv()

class MongoDBConnection:
    _instance: Optional['MongoDBConnection'] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    def __new__(cls) -> 'MongoDBConnection':
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._client:
            self._connect()

    def _connect(self):
        """Estabelece conexão com MongoDB"""
        try:
            # Obtém URI do MongoDB
            uri = os.getenv("MONGODB_URI")
            if not uri:
                raise ValueError("MONGODB_URI não encontrada no arquivo .env")

            # Conecta ao MongoDB
            self._client = MongoClient(uri)
            self._db = self._client.ava_db

            # Verifica conexão
            self._client.admin.command('ping')
            logger.info("Conectado ao MongoDB com sucesso!")

            # Configura índices
            self._setup_indexes()

        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB: {str(e)}")
            raise

    def _setup_indexes(self):
        """Configura índices necessários"""
        try:
            # Índices para memórias
            self._db.memories.create_index([("type", 1)])
            self._db.memories.create_index([("timestamp", -1)])
            self._db.memories.create_index([("importance", -1)])
            
            # Índices para consciência
            self._db.consciousness.create_index([("timestamp", -1)])
            self._db.consciousness.create_index([("awareness_level", -1)])
            
            # Índices para métricas
            self._db.metrics.create_index([("timestamp", -1)])
            
            logger.info("Índices configurados com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao configurar índices: {str(e)}")
            raise

    @property
    def db(self) -> Database:
        """Retorna instância do banco de dados"""
        if not self._db:
            self._connect()
        return self._db

    def close(self):
        """Fecha conexão com MongoDB"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("Conexão com MongoDB fechada.")

    def __del__(self):
        """Destrutor para garantir fechamento da conexão"""
        self.close()

# Singleton para conexão MongoDB
mongodb = MongoDBConnection() 