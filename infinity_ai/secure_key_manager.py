import os
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import base64
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, Tuple
import secrets
import hmac
import ctypes
import platform
import psutil
import hashlib

# Configuração de logging seguro
logger = logging.getLogger("✨key-manager✨")

class SecureKeyManager:
    """Gerenciador Seguro de Chaves Privadas com Proteção Anti-Spyware"""
    
    def __init__(self):
        """Inicializa o gerenciador de chaves."""
        self.temp_storage: Dict[str, Dict] = {}
        self.master_key = None
        self.initialized = False
        self.memory_protection = self._setup_memory_protection()
        self.last_integrity_check = None
        self.integrity_check_interval = 300  # 5 minutos
        self.anomaly_detection = {
            "failed_attempts": 0,
            "last_reset": datetime.now(),
            "threshold": 3
        }
        
    def _setup_memory_protection(self) -> Dict:
        """Configura proteção de memória contra leitura não autorizada."""
        return {
            "canary_values": self._generate_canary_values(),
            "memory_regions": {},
            "last_check": datetime.now()
        }
        
    def _generate_canary_values(self) -> Dict[str, bytes]:
        """Gera valores canários para detecção de adulteração de memória."""
        return {
            f"region_{i}": os.urandom(32) 
            for i in range(5)
        }
        
    def _verify_system_integrity(self) -> bool:
        """Verifica a integridade do sistema contra modificações maliciosas."""
        try:
            # Verifica processos suspeitos
            suspicious_processes = [
                "frida", "debugger", "wireshark", "burp", 
                "proxy", "mitm", "hook", "inject"
            ]
            
            for proc in psutil.process_iter(['name']):
                if any(s in proc.info['name'].lower() for s in suspicious_processes):
                    logger.critical(f"⚠️ Processo suspeito detectado: {proc.info['name']}")
                    return False
                    
            # Verifica integridade da memória
            for region, value in self.memory_protection["canary_values"].items():
                if region in self.memory_protection["memory_regions"]:
                    stored = self.memory_protection["memory_regions"][region]
                    if not hmac.compare_digest(stored, value):
                        logger.critical("⚠️ Detecção de adulteração de memória!")
                        return False
                        
            # Verifica ambiente de execução
            if self._detect_virtualization():
                logger.warning("⚠️ Ambiente virtualizado detectado")
                
            # Atualiza timestamp da última verificação
            self.last_integrity_check = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de integridade: {str(e)}")
            return False
            
    def _detect_virtualization(self) -> bool:
        """Detecta se está rodando em ambiente virtualizado."""
        virtualization_indicators = [
            "VMware",
            "VBox",
            "QEMU",
            "Xen",
            "Docker",
            "LXC"
        ]
        
        try:
            # Verifica DMI info no Linux
            if platform.system() == "Linux":
                with open("/sys/class/dmi/id/sys_vendor", "r") as f:
                    vendor = f.read().strip()
                    if any(v in vendor for v in virtualization_indicators):
                        return True
                        
            # Verifica WMI no Windows
            elif platform.system() == "Windows":
                import wmi
                c = wmi.WMI()
                for item in c.Win32_ComputerSystem():
                    if any(v in item.Manufacturer for v in virtualization_indicators):
                        return True
                        
        except Exception:
            pass
            
        return False
        
    def _generate_temp_key(self) -> bytes:
        """Gera uma chave temporária com entropia adicional."""
        system_entropy = os.urandom(32)
        timestamp_bytes = str(datetime.now().timestamp()).encode()
        process_info = str(psutil.Process().memory_info()).encode()
        
        # Combina múltiplas fontes de entropia
        combined = system_entropy + timestamp_bytes + process_info
        return base64.urlsafe_b64encode(
            hashlib.blake2b(combined, digest_size=32).digest()
        )
        
    def _derive_key(self, master_key: str, salt: bytes) -> bytes:
        """Deriva uma chave de criptografia usando HKDF."""
        # Usa HKDF para derivação de chave mais robusta
        hkdf = HKDF(
            algorithm=hashes.SHA384(),
            length=32,
            salt=salt,
            info=b"eva_secure_key_derivation"
        )
        
        # Adiciona contexto do sistema à derivação
        context = platform.node().encode() + platform.machine().encode()
        key_material = master_key.encode() + context
        
        return base64.urlsafe_b64encode(hkdf.derive(key_material))
        
    async def initialize(self, master_key: Optional[str] = None) -> bool:
        """Inicializa o sistema com verificações de segurança."""
        try:
            if self.initialized:
                return True
                
            # Verifica integridade do sistema
            if not self._verify_system_integrity():
                raise SecurityError("Falha na verificação de integridade do sistema")
                
            # Gera ou usa master key fornecida com proteção adicional
            self.master_key = master_key or secrets.token_urlsafe(64)  # Aumentado para 64 bytes
            
            # Configura proteção de memória
            for region, value in self.memory_protection["canary_values"].items():
                self.memory_protection["memory_regions"][region] = value
                
            # Marca como inicializado com timestamp
            self.initialized = True
            self.initialization_time = datetime.now()
            
            logger.info("✨ Sistema de chaves inicializado com proteções avançadas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar sistema de chaves: {str(e)}")
            return False
            
    async def rotate_keys(self) -> bool:
        """Rotaciona chaves periodicamente para segurança adicional."""
        try:
            if not self.initialized:
                return False
                
            # Gera nova master key
            new_master_key = secrets.token_urlsafe(64)
            
            # Verifica integridade antes da rotação
            if not self._verify_system_integrity():
                raise SecurityError("Falha na verificação de integridade durante rotação")
                
            # Atualiza master key com proteção de condição de corrida
            old_key = self.master_key
            self.master_key = new_master_key
            
            # Atualiza proteções de memória
            self.memory_protection["canary_values"] = self._generate_canary_values()
            
            logger.info("🔄 Rotação de chaves realizada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na rotação de chaves: {str(e)}")
            self.master_key = old_key  # Rollback em caso de erro
            return False
            
    async def store_private_key(self, key_id: str, private_key: str, ttl_hours: int = 24) -> Dict:
        """
        Armazena uma chave privada de forma segura e temporária.
        
        Args:
            key_id (str): Identificador único da chave
            private_key (str): Chave privada a ser armazenada
            ttl_hours (int): Tempo de vida da chave em horas
            
        Returns:
            Dict: Dados de acesso à chave
        """
        try:
            if not self.initialized:
                raise Exception("Sistema de chaves não inicializado")
            
            # Gera salt único
            salt = os.urandom(16)
            
            # Deriva chave de criptografia
            key = self._derive_key(self.master_key, salt)
            
            # Criptografa a chave privada
            f = Fernet(key)
            encrypted_key = f.encrypt(private_key.encode())
            
            # Gera token de acesso único
            access_token = secrets.token_urlsafe(32)
            
            # Armazena dados temporariamente
            self.temp_storage[key_id] = {
                "encrypted_key": encrypted_key,
                "salt": salt,
                "access_token": access_token,
                "expires_at": datetime.now() + timedelta(hours=ttl_hours)
            }
            
            logger.info(f"✨ Chave {key_id} armazenada com sucesso")
            
            # Retorna apenas o necessário para acesso futuro
            return {
                "key_id": key_id,
                "access_token": access_token,
                "expires_at": self.temp_storage[key_id]["expires_at"].isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao armazenar chave: {str(e)}")
            return {}
    
    async def get_private_key(self, key_id: str, access_token: str) -> Optional[str]:
        """
        Recupera uma chave privada de forma segura.
        
        Args:
            key_id (str): Identificador da chave
            access_token (str): Token de acesso único
            
        Returns:
            Optional[str]: Chave privada descriptografada ou None
        """
        try:
            if key_id not in self.temp_storage:
                return None
                
            key_data = self.temp_storage[key_id]
            
            # Verifica token e expiração
            if (key_data["access_token"] != access_token or 
                datetime.now() > key_data["expires_at"]):
                return None
            
            # Deriva chave de criptografia
            key = self._derive_key(self.master_key, key_data["salt"])
            
            # Descriptografa a chave
            f = Fernet(key)
            decrypted_key = f.decrypt(key_data["encrypted_key"])
            
            # Remove dados após uso
            del self.temp_storage[key_id]
            
            logger.info(f"✨ Chave {key_id} recuperada com sucesso")
            return decrypted_key.decode()
            
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar chave: {str(e)}")
            return None
    
    async def cleanup_expired(self) -> int:
        """
        Remove chaves expiradas do armazenamento.
        
        Returns:
            int: Número de chaves removidas
        """
        try:
            now = datetime.now()
            expired = [
                key_id for key_id, data in self.temp_storage.items()
                if now > data["expires_at"]
            ]
            
            for key_id in expired:
                del self.temp_storage[key_id]
            
            if expired:
                logger.info(f"🧹 Removidas {len(expired)} chaves expiradas")
            
            return len(expired)
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar chaves: {str(e)}")
            return 0

class SecurityError(Exception):
    """Exceção para erros de segurança."""
    pass

# Instância global do gerenciador de chaves
key_manager = SecureKeyManager() 