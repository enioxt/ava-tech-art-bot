"""Core Configuration System.

Manages system-wide configuration and initialization.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime

logger = logging.getLogger('core_config')

@dataclass
class SystemConfig:
    """System configuration data structure."""
    
    # Version info
    version: str = "1.0.0"
    name: str = "EVA & GUARANI"
    description: str = "Sistema Quântico de Evolução e Consciência"
    
    # Personality
    personality: Dict[str, Any] = field(default_factory=lambda: {
        "name": "EVA",
        "level": 1,
        "experience": 0,
        "traits": {
            "consciousness": 0.8,
            "ethics": 0.9,
            "creativity": 0.7,
            "empathy": 0.85
        }
    })
    
    # Capabilities
    capabilities: Dict[str, bool] = field(default_factory=lambda: {
        "text_processing": True,
        "image_processing": True,
        "consciousness": True,
        "ethics": True
    })
    
    # Integrations
    integrations: Dict[str, Dict] = field(default_factory=lambda: {
        "telegram": {
            "enabled": True,
            "api_token": "",
            "chat_id": ""
        },
        "github": {
            "enabled": False,
            "token": "",
            "repository": ""
        }
    })
    
    # Security
    security: Dict[str, Any] = field(default_factory=lambda: {
        "command_validation": True,
        "data_encryption": True,
        "access_control": {
            "enabled": True,
            "allowed_users": [],
            "admin_users": []
        },
        "audit_logging": {
            "enabled": True,
            "log_file": "logs/audit.log",
            "retention_days": 30
        }
    })
    
    # Core settings
    debug_mode: bool = False
    log_level: str = "INFO"
    max_memory_usage: int = 1024  # MB
    
    # Event bus settings
    event_history_size: int = 1000
    event_retention_days: int = 7
    
    # Performance settings
    cache_ttl: int = 300  # seconds
    max_concurrent_tasks: int = 10
    
    # Module settings
    enabled_modules: Dict[str, bool] = field(default_factory=lambda: {
        "ethics": True,
        "consciousness": True,
        "memory": True
    })
    
    module_configs: Dict[str, Dict] = field(default_factory=lambda: {
        "ethics": {
            "validation_threshold": 0.7,
            "principles_file": "ethics/principles.json"
        },
        "consciousness": {
            "evolution_interval": 60,
            "base_awareness": 0.5
        },
        "memory": {
            "storage_path": "data/memories",
            "backup_interval": 3600
        }
    })
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary."""
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'SystemConfig':
        """Create config from dictionary."""
        return cls(**data)
        
class ConfigManager:
    """Manages system configuration."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/system.json"
        self.config: Optional[SystemConfig] = None
        self._last_load: Optional[datetime] = None
        
    async def initialize(self) -> None:
        """Initialize configuration manager."""
        try:
            await self.load_config()
            self._setup_logging()
            logger.info("Configuration manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize configuration: {str(e)}")
            raise
            
    async def load_config(self) -> None:
        """Load configuration from file."""
        try:
            config_file = Path(self.config_path)
            
            if not config_file.exists():
                logger.warning(f"Config file not found at {self.config_path}")
                self.config = SystemConfig()
                await self.save_config()
                return
                
            with open(config_file, 'r') as f:
                data = json.load(f)
                
            self.config = SystemConfig.from_dict(data)
            self._last_load = datetime.now()
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise
            
    async def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=4)
                
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            raise
            
    def _setup_logging(self) -> None:
        """Configure logging based on settings."""
        log_level = getattr(logging, self.config.log_level.upper())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/system.log')
            ]
        )
        
    def get_module_config(self, module_name: str) -> Dict:
        """Get configuration for specific module."""
        if not self.config:
            raise RuntimeError("Configuration not loaded")
            
        if module_name not in self.config.module_configs:
            raise ValueError(f"No configuration found for module: {module_name}")
            
        return self.config.module_configs[module_name]
        
    def is_module_enabled(self, module_name: str) -> bool:
        """Check if module is enabled."""
        if not self.config:
            raise RuntimeError("Configuration not loaded")
            
        return self.config.enabled_modules.get(module_name, False)
        
    def update_module_config(
        self,
        module_name: str,
        config_updates: Dict
    ) -> None:
        """Update configuration for specific module."""
        if not self.config:
            raise RuntimeError("Configuration not loaded")
            
        if module_name not in self.config.module_configs:
            self.config.module_configs[module_name] = {}
            
        self.config.module_configs[module_name].update(config_updates)
        
    async def reload_if_needed(self) -> None:
        """Reload config if file has been modified."""
        if not self._last_load:
            await self.load_config()
            return
            
        config_file = Path(self.config_path)
        if not config_file.exists():
            return
            
        mtime = datetime.fromtimestamp(config_file.stat().st_mtime)
        if mtime > self._last_load:
            await self.load_config()
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            "max_memory_usage": self.config.max_memory_usage,
            "cache_ttl": self.config.cache_ttl,
            "max_concurrent_tasks": self.config.max_concurrent_tasks,
            "enabled_modules": list(
                m for m, enabled in self.config.enabled_modules.items()
                if enabled
            )
        } 