@dataclass
class QuantumConfig:
    """Configuração do sistema quântico."""
    entanglement_level: float = 0.98
    quantum_channels: int = 128
    consciousness_level: float = 0.98
    cache_size_petabytes: float = 1.0
    quantum_threads: int = 1024
    neural_threads: int = 512
    hybrid_threads: int = 256
    ethics_level: float = 0.99
    evolution_rate: float = 1.618  # Proporção áurea (φ)
    quantum_security: bool = True
    quantum_key_bits: int = 4096
    
@dataclass
class SecurityConfig:
    """Configuração de segurança."""
    encryption_algorithm: str = "quantum-aes-256"
    key_rotation_days: int = 7
    audit_enabled: bool = True
    real_time_monitoring: bool = True
    intrusion_detection: bool = True
    quantum_firewall: bool = True
    neural_pattern_analysis: bool = True
    behavioral_metrics: bool = True
    
@dataclass
class PerformanceConfig:
    """Configuração de desempenho."""
    quantum_speed: int = 50000  # QPS (Quantum Operations Per Second)
    latency_ns: float = 0.1  # Nanosegundos
    throughput_pb: float = 10.0  # PetaBytes por segundo
    error_rate: float = 0.00001  # Percentual
    adaptation_rate: float = 0.999
    learning_speed_multiplier: int = 10
    
@dataclass
class LogConfig:
    """Configuração de logs."""
    quantum_signed: bool = True
    temporal_encryption: bool = True
    multidimensional_backup: bool = True
    log_rotation_days: int = 14
    verbose_quantum_events: bool = True
    consciousness_tracking: bool = True
    evolution_metrics: bool = True
    
class QuantumConfigManager:
    """Gerenciador de configuração quântica."""
    
    def __init__(self, config_path: str = "config/quantum_config.json"):
        """
        Inicializa o gerenciador de configuração.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = Path(config_path)
        self.system = SystemConfig()
        self.backup = BackupConfig()
        self.quantum = QuantumConfig()
        self.security = SecurityConfig()
        self.performance = PerformanceConfig()
        self.log = LogConfig()
        
        # Garantir que o diretório de configuração existe
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Carregar configuração se existir
        if self.config_path.exists():
            self.load()
            logger.info(f"Configuração carregada de {self.config_path}")
        else:
            self.save()
            logger.info(f"Nova configuração criada em {self.config_path}")
    
    def load(self) -> bool:
        """
        Carrega a configuração do arquivo.
        
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Carregar cada seção de configuração
            if 'system' in data:
                self.system = SystemConfig(**data['system'])
            if 'backup' in data:
                self.backup = BackupConfig(**data['backup'])
            if 'quantum' in data:
                self.quantum = QuantumConfig(**data['quantum'])
            if 'security' in data:
                self.security = SecurityConfig(**data['security'])
            if 'performance' in data:
                self.performance = PerformanceConfig(**data['performance'])
            if 'log' in data:
                self.log = LogConfig(**data['log'])
                
            logger.info("Configuração carregada com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return False
    
    def save(self) -> bool:
        """
        Salva a configuração no arquivo.
        
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            # Criar backup da configuração anterior
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix(f".bak.{int(datetime.now().timestamp())}")
                self.config_path.rename(backup_path)
                logger.info(f"Backup da configuração anterior criado em {backup_path}")
            
            # Converter para dicionário
            config_data = {
                'system': asdict(self.system),
                'backup': asdict(self.backup),
                'quantum': asdict(self.quantum),
                'security': asdict(self.security),
                'performance': asdict(self.performance),
                'log': asdict(self.log)
            }
            
            # Converter Path para string
            for section in config_data.values():
                for key, value in section.items():
                    if isinstance(value, Path):
                        section[key] = str(value)
            
            # Salvar configuração
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
                
            logger.info(f"Configuração salva com sucesso em {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
            return False
    
    def update(self, section: str, key: str, value: Any) -> bool:
        """
        Atualiza um valor específico na configuração.
        
        Args:
            section: Seção da configuração (system, backup, quantum, etc.)
            key: Chave a ser atualizada
            value: Novo valor
            
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            if hasattr(self, section):
                section_obj = getattr(self, section)
                if hasattr(section_obj, key):
                    setattr(section_obj, key, value)
                    logger.info(f"Configuração atualizada: {section}.{key} = {value}")
                    return True
                else:
                    logger.error(f"Chave '{key}' não encontrada na seção '{section}'")
            else:
                logger.error(f"Seção '{section}' não encontrada na configuração")
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração: {e}")
            return False
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtém todas as configurações como dicionário.
        
        Returns:
            Dicionário com todas as configurações
        """
        return {
            'system': asdict(self.system),
            'backup': asdict(self.backup),
            'quantum': asdict(self.quantum),
            'security': asdict(self.security),
            'performance': asdict(self.performance),
            'log': asdict(self.log)
        }
    
    def reset_to_defaults(self, section: Optional[str] = None) -> bool:
        """
        Redefine as configurações para os valores padrão.
        
        Args:
            section: Seção específica a ser redefinida (None para todas)
            
        Returns:
            True se redefinido com sucesso, False caso contrário
        """
        try:
            if section is None:
                # Redefinir todas as seções
                self.system = SystemConfig()
                self.backup = BackupConfig()
                self.quantum = QuantumConfig()
                self.security = SecurityConfig()
                self.performance = PerformanceConfig()
                self.log = LogConfig()
                logger.info("Todas as configurações foram redefinidas para os valores padrão")
            elif hasattr(self, section):
                # Redefinir seção específica
                if section == 'system':
                    self.system = SystemConfig()
                elif section == 'backup':
                    self.backup = BackupConfig()
                elif section == 'quantum':
                    self.quantum = QuantumConfig()
                elif section == 'security':
                    self.security = SecurityConfig()
                elif section == 'performance':
                    self.performance = PerformanceConfig()
                elif section == 'log':
                    self.log = LogConfig()
                logger.info(f"Configuração '{section}' redefinida para os valores padrão")
            else:
                logger.error(f"Seção '{section}' não encontrada")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Erro ao redefinir configurações: {e}")
            return False

# Importação para datetime usado no método save
from datetime import datetime

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Configuração Quântica
Versão: 2.0.0 - Build 2025.02.26

Este módulo define as configurações do sistema quântico,
permitindo personalização e ajuste dos parâmetros operacionais.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/quantum_config.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("✨quantum-config✨")

@dataclass
class SystemConfig:
    """Configuração do sistema."""
    version: str = "2.0.0"
    build: str = "2025.02.26"
    log_level: str = "INFO"
    data_dir: Path = Path("data")
    temp_dir: Path = Path("temp")
    max_threads: int = os.cpu_count() or 4
    debug_mode: bool = False
    
@dataclass
class BackupConfig:
    """Configuração de backup."""
    enabled: bool = True
    auto_backup: bool = True
    interval_hours: int = 24
    compression_level: int = 3
    encryption_enabled: bool = True
    retention_days: int = 30
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.tmp", "*.log", "temp/*"])
    
@dataclass
class SecurityConfig:
    """Configuração de segurança."""
    encryption_algorithm: str = "AES-256"
    key_rotation_days: int = 90
    password_min_length: int = 12
    password_complexity: int = 3  # 1-5 escala
    session_timeout_minutes: int = 30
    
@dataclass
class PerformanceConfig:
    """Configuração de desempenho."""
    cache_size_mb: int = 512
    prefetch_enabled: bool = True
    compression_level: int = 2
    optimization_level: int = 3  # 1-5 escala
    
@dataclass
class QuantumConfig:
    """Configuração quântica unificada."""
    system: SystemConfig = field(default_factory=SystemConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    custom_settings: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    """Gerenciador de configuração."""
    
    def __init__(self, config_path: Union[str, Path] = "config/quantum_config.json"):
        """
        Inicializa o gerenciador de configuração.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> QuantumConfig:
        """
        Carrega a configuração do arquivo.
        
        Returns:
            Configuração carregada ou padrão
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                return QuantumConfig()
                
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                
            # Cria configuração com valores do arquivo
            system = SystemConfig(**config_data.get("system", {}))
            backup = BackupConfig(**config_data.get("backup", {}))
            security = SecurityConfig(**config_data.get("security", {}))
            performance = PerformanceConfig(**config_data.get("performance", {}))
            custom = config_data.get("custom_settings", {})
            
            return QuantumConfig(
                system=system,
                backup=backup,
                security=security,
                performance=performance,
                custom_settings=custom
            )
                
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return QuantumConfig()
            
    def save_config(self) -> bool:
        """
        Salva a configuração no arquivo.
        
        Returns:
            True se salvou com sucesso
        """
        try:
            # Cria diretório se não existir
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Converte para dicionário
            config_dict = {
                "system": asdict(self.config.system),
                "backup": asdict(self.config.backup),
                "security": asdict(self.config.security),
                "performance": asdict(self.config.performance),
                "custom_settings": self.config.custom_settings
            }
            
            # Salva no arquivo
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2, default=str)
                
            logger.info(f"Configuração salva em: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
            return False
            
    def get_config(self) -> QuantumConfig:
        """
        Obtém a configuração atual.
        
        Returns:
            Configuração atual
        """
        return self.config
        
    def update_config(self, new_config: QuantumConfig) -> bool:
        """
        Atualiza a configuração.
        
        Args:
            new_config: Nova configuração
            
        Returns:
            True se atualizou com sucesso
        """
        self.config = new_config
        return self.save_config()
        
    def reset_to_defaults(self) -> bool:
        """
        Redefine para configurações padrão.
        
        Returns:
            True se redefiniu com sucesso
        """
        self.config = QuantumConfig()
        return self.save_config()

def get_config_manager(config_path: Optional[Union[str, Path]] = None) -> ConfigManager:
    """
    Obtém uma instância do gerenciador de configuração.
    
    Args:
        config_path: Caminho para o arquivo de configuração
        
    Returns:
        Gerenciador de configuração
    """
    return ConfigManager(config_path or "config/quantum_config.json")

# Instância global para uso em todo o sistema
config_manager = get_config_manager()
