"""
Universal Value Logger
Sistema personalizável de registro de valores e experiências fundamentais
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any
import random
from dataclasses import dataclass, asdict
import asyncio
from cryptography.fernet import Fernet
import base64

# Configuração de logging temática
logger = logging.getLogger("✨valor-universal✨")
logger.setLevel(logging.INFO)

# Limites do sistema (como stats em RPG)
SYSTEM_LIMITS = {
    "max_memories": 1000,  # Capacidade máxima do grimório
    "warning_threshold": 900,  # Alerta de grimório quase cheio
    "batch_size": 50,  # Tamanho do grupo de memórias
    "cooldown": 60  # Tempo entre registros (1 min)
}

# Estados do sistema (como status effects)
SYSTEM_STATES = {
    "resting": "🌙 Grimório em repouso",
    "recording": "✨ Registrando memória",
    "warning": "📚 Grimório quase cheio",
    "full": "🔒 Grimório completo",
    "error": "💔 Falha na magia"
}

# Classes de valor (como classes de RPG)
VALUE_CLASSES = {
    "primary_value": {
        "name": "Paladino do Amor",
        "power": "Luz Divina",
        "alignment": "Lawful Good"
    },
    "secondary_value": {
        "name": "Druida da Gratidão",
        "power": "Harmonia Natural",
        "alignment": "Neutral Good"
    },
    "tertiary_value": {
        "name": "Bardo da Harmonia",
        "power": "Canção do Equilíbrio",
        "alignment": "Chaotic Good"
    }
}

@dataclass
class ValueMemory:
    """Memória de valor (como uma relíquia sagrada)"""
    timestamp: str
    value_type: str
    message: str
    context: Dict[str, Any]
    frequencies: Dict[str, float]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'ValueMemory':
        return cls(**data)

class UniversalValueLogger:
    """Sistema de Registro Universal (como o Cristal do Tempo em Chrono Trigger)"""
    
    def __init__(self, log_dir: str = "logs", config_path: str = "config/core_values_config.json"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = Path(config_path)
        self.memories_file = self.log_dir / "universal_memories.json"
        self.config = self._load_config()
        self.last_recording = datetime.now()
        self.memories_count = 0
        self._setup_logging()
        self._setup_encryption()
        
    def _setup_logging(self):
        """Configura logging temático (como o diário de quest)"""
        if not logger.handlers:
            fh = logging.FileHandler("logs/universal_values.log")
            fh.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s'
            ))
            logger.addHandler(fh)
            
    def _check_system_state(self) -> str:
        """Verifica estado do sistema (como status check)"""
        if (datetime.now() - self.last_recording).total_seconds() < SYSTEM_LIMITS["cooldown"]:
            return "resting"
        if self.memories_count >= SYSTEM_LIMITS["max_memories"]:
            return "full"
        if self.memories_count >= SYSTEM_LIMITS["warning_threshold"]:
            return "warning"
        return "recording"
        
    def _setup_encryption(self):
        """Configura criptografia"""
        try:
            key_file = self.log_dir / ".key"
            if key_file.exists():
                self.key = key_file.read_bytes()
            else:
                self.key = Fernet.generate_key()
                key_file.write_bytes(self.key)
            self.cipher = Fernet(self.key)
        except Exception as e:
            logger.error(f"❌ Erro ao configurar criptografia: {e}")
            self.cipher = None
            
    def _load_config(self) -> Dict:
        """Carrega configuração"""
        try:
            if not self.config_path.exists():
                logger.warning("⚠️ Arquivo de configuração não encontrado")
                return {}
                
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            return {}
            
    def _get_value_config(self, value_type: str) -> Dict:
        """Obtém configuração do valor"""
        try:
            return self.config.get("core_values", {}).get(value_type, {})
        except Exception as e:
            logger.error(f"❌ Erro ao obter configuração do valor: {e}")
            return {}
            
    def _get_frequencies(self, value_type: str) -> Dict[str, float]:
        """Obtém frequências associadas ao valor"""
        try:
            value_config = self._get_value_config(value_type)
            freq_type = value_config.get("attributes", {}).get("frequency")
            if freq_type:
                freq_config = self.config.get("frequencies", {}).get(freq_type, {})
                return {
                    "name": freq_config.get("name", ""),
                    "value": freq_config.get("value", 0.0),
                    "description": freq_config.get("description", "")
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Erro ao obter frequências: {e}")
            return {}
            
    def _format_value_message(self, value_type: str, message: str, context: Optional[Dict] = None) -> str:
        """Formata mensagem do valor"""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            value_config = self._get_value_config(value_type)
            value_name = value_config.get("name", value_type)
            
            # Formata contexto
            ctx = ""
            if context:
                ctx = "\nContexto:\n" + "\n".join(
                    f"- {k}: {v}" for k, v in context.items()
                )
                
            # Adiciona inspiração
            inspiration = self.get_inspiration_quote()
            
            # Adiciona frequências
            frequencies = self._get_frequencies(value_type)
            freq_info = ""
            if frequencies:
                freq_info = f"\nFrequência: {frequencies['name']} ({frequencies['value']} Hz)"
                
            return f"""
✨ Momento de {value_name} ✨
{now}

{message}
{ctx}
{freq_info}

Inspiração:
"{inspiration}"
"""
        except Exception as e:
            logger.error(f"❌ Erro ao formatar mensagem: {e}")
            return message
            
    def _encrypt_data(self, data: Dict) -> str:
        """Criptografa dados"""
        try:
            if self.cipher and self.config.get("customization", {}).get("privacy", {}).get("encrypt_memories"):
                json_data = json.dumps(data)
                return base64.b64encode(
                    self.cipher.encrypt(json_data.encode())
                ).decode()
            return json.dumps(data)
        except Exception as e:
            logger.error(f"❌ Erro ao criptografar dados: {e}")
            return json.dumps(data)
            
    def _decrypt_data(self, encrypted: str) -> Dict:
        """Descriptografa dados"""
        try:
            if self.cipher and self.config.get("customization", {}).get("privacy", {}).get("encrypt_memories"):
                json_data = self.cipher.decrypt(
                    base64.b64decode(encrypted.encode())
                ).decode()
                return json.loads(json_data)
            return json.loads(encrypted)
        except Exception as e:
            logger.error(f"❌ Erro ao descriptografar dados: {e}")
            return {}
            
    async def _save_memory(self, memory: ValueMemory) -> None:
        """Salva memória de valor"""
        try:
            # Carrega memórias existentes
            if self.memories_file.exists():
                with open(self.memories_file, "r", encoding="utf-8") as f:
                    data = self._decrypt_data(f.read())
            else:
                data = {"memories": [], "meta": {}}
                
            # Adiciona nova memória
            data["memories"].append(memory.to_dict())
            
            # Atualiza meta
            data["meta"] = {
                "updated_at": datetime.now().isoformat(),
                "total_memories": len(data["memories"]),
                "value_types": list(set(m["value_type"] for m in data["memories"]))
            }
            
            # Criptografa e salva
            encrypted = self._encrypt_data(data)
            with open(self.memories_file, "w", encoding="utf-8") as f:
                f.write(encrypted)
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar memória: {e}")
            
    def get_inspiration_quote(self, collection: str = "universal") -> str:
        """Retorna uma citação inspiradora"""
        try:
            quotes = self.config.get("inspiration_quotes", {}).get("collections", {}).get(collection, [])
            if quotes:
                quote = random.choice(quotes)
                return f"{quote['quote']} - {quote['source']}"
            return "O amor é a força mais poderosa do universo"
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter citação: {e}")
            return "O amor é a força mais poderosa do universo"
            
    async def log_value(self, value_type: str, message: str, context: Optional[Dict] = None) -> None:
        """Registra um momento de valor (como registrar uma conquista épica)"""
        try:
            state = self._check_system_state()
            
            if state == "resting":
                logger.debug(SYSTEM_STATES["resting"])
                return
                
            if state == "full":
                logger.warning(SYSTEM_STATES["full"])
                return
            
            # Verifica classe do valor
            value_class = VALUE_CLASSES.get(value_type, {})
            if not value_class:
                raise ValueError(f"Classe de valor inválida: {value_type}")
            
            # Formata mensagem com tema RPG
            formatted = self._format_value_message(value_type, message, context)
            
            # Cria memória
            memory = ValueMemory(
                timestamp=datetime.now().isoformat(),
                value_type=value_type,
                message=formatted,
                context=context or {},
                frequencies=self._get_frequencies(value_type),
                metadata={
                    "class": value_class["name"],
                    "power": value_class["power"],
                    "alignment": value_class["alignment"],
                    "version": "1.0.0"
                }
            )
            
            # Salva memória
            await self._save_memory(memory)
            self.memories_count += 1
            
            # Log temático
            logger.info(f"✨ {value_class['name']} registrou uma nova conquista!")
            
        except Exception as e:
            logger.error(f"{SYSTEM_STATES['error']}: {e}")
            
    async def get_memories(self, value_type: Optional[str] = None) -> List[ValueMemory]:
        """Retorna memórias de valor"""
        try:
            if not self.memories_file.exists():
                return []
                
            with open(self.memories_file, "r", encoding="utf-8") as f:
                data = self._decrypt_data(f.read())
                
            memories = [
                ValueMemory.from_dict(m)
                for m in data.get("memories", [])
            ]
            
            if value_type:
                memories = [m for m in memories if m.value_type == value_type]
                
            return memories
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter memórias: {e}")
            return []
            
    def add_inspiration_quote(self, quote: str, source: str, context: str, collection: str = "personal") -> bool:
        """Adiciona uma citação inspiradora"""
        try:
            if not self.config.get("customization", {}).get("allow_quote_addition"):
                raise ValueError("Adição de citações não permitida")
                
            quotes = self.config.get("inspiration_quotes", {}).get("collections", {})
            if collection not in quotes:
                quotes[collection] = []
                
            quotes[collection].append({
                "quote": quote,
                "source": source,
                "context": context
            })
            
            # Salva configuração
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar citação: {e}")
            return False
            
    def customize_value(self, value_type: str, new_name: str, new_description: str) -> bool:
        """Personaliza um valor"""
        try:
            if not self.config.get("customization", {}).get("allow_value_renaming"):
                raise ValueError("Renomeação de valores não permitida")
                
            value = self.config.get("core_values", {}).get(value_type)
            if not value:
                raise ValueError(f"Valor não encontrado: {value_type}")
                
            value["name"] = new_name
            value["attributes"]["description"] = new_description
            
            # Salva configuração
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao personalizar valor: {e}")
            return False

# Instância global do logger
universal_logger = UniversalValueLogger()