#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Gerenciador de Modelos de IA
Adaptado do framework ElizaOS
Versão: 1.0.0 - Build 2024.02.26

Este módulo gerencia diferentes modelos de IA (OpenAI, Anthropic, Gemini, etc.)
permitindo que o sistema utilize diferentes provedores de forma transparente.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/models.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("✨quantum-models✨")

@dataclass
class ModelConfig:
    """Configuração de modelo de IA."""
    name: str
    provider: str
    api_key: str = ""
    model_name: str = ""
    temperature: float = 0.7
    max_tokens: int = 1000
    options: Dict[str, Any] = field(default_factory=dict)

class BaseModel:
    """Modelo base para todas as integrações de IA."""
    
    def __init__(self, config: ModelConfig):
        """Inicializa o modelo base."""
        self.config = config
        self.name = config.name
        self.provider = config.provider
        self.api_key = config.api_key
        self.logger = logging.getLogger(f"✨model-{self.name}✨")
        
    async def generate(self, prompt: str, **kwargs) -> str:
        """Gera uma resposta. Deve ser implementado pelas subclasses."""
        raise NotImplementedError("Método generate() deve ser implementado pela subclasse")
        
    async def embed(self, text: str, **kwargs) -> List[float]:
        """Gera embeddings. Deve ser implementado pelas subclasses."""
        raise NotImplementedError("Método embed() deve ser implementado pela subclasse")
        
    async def moderate(self, text: str) -> Dict[str, Any]:
        """Modera o texto. Deve ser implementado pelas subclasses."""
        raise NotImplementedError("Método moderate() deve ser implementado pela subclasse")

class ModelManager:
    """Gerenciador de modelos de IA inspirado no ElizaOS."""
    
    def __init__(self):
        """Inicializa o gerenciador de modelos."""
        self.models = {}
        self.default_model = None
        self.logger = logging.getLogger("✨quantum-models✨")
        self.config_dir = Path("config/integration")
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def register_model(self, model_id: str, config: ModelConfig) -> bool:
        """
        Registra um novo modelo de IA.
        
        Args:
            model_id: Identificador único do modelo
            config: Configuração do modelo
            
        Returns:
            True se o modelo foi registrado com sucesso
        """
        if model_id in self.models:
            self.logger.warning(f"Modelo {model_id} já registrado, substituindo")
        
        # Importação dinâmica do modelo apropriado
        try:
            if config.provider == "openai":
                from .models.openai import OpenAIModel
                self.models[model_id] = OpenAIModel(config)
            elif config.provider == "anthropic":
                from .models.anthropic import AnthropicModel
                self.models[model_id] = AnthropicModel(config)
            elif config.provider == "gemini":
                from .models.gemini import GeminiModel
                self.models[model_id] = GeminiModel(config)
            elif config.provider == "llama":
                from .models.llama import LlamaModel
                self.models[model_id] = LlamaModel(config)
            elif config.provider == "local":
                from .models.local import LocalModel
                self.models[model_id] = LocalModel(config)
            else:
                self.logger.error(f"Provedor de modelo desconhecido: {config.provider}")
                return False
            
            # Define como modelo padrão se for o primeiro
            if self.default_model is None:
                self.default_model = model_id
                
            self.logger.info(f"Modelo {model_id} ({config.provider}) registrado com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao registrar modelo {model_id}: {e}")
            return False
    
    def set_default_model(self, model_id: str) -> bool:
        """
        Define o modelo padrão.
        
        Args:
            model_id: Identificador do modelo
            
        Returns:
            True se o modelo foi definido como padrão
        """
        if model_id not in self.models:
            self.logger.error(f"Modelo {model_id} não encontrado")
            return False
        
        self.default_model = model_id
        self.logger.info(f"Modelo padrão definido: {model_id}")
        return True
    
    async def generate_response(self, prompt: str, model_id: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        Gera uma resposta usando o modelo especificado ou o padrão.
        
        Args:
            prompt: Texto de entrada
            model_id: Identificador do modelo (usa o padrão se None)
            **kwargs: Argumentos adicionais específicos do modelo
            
        Returns:
            Resposta gerada ou None em caso de erro
        """
        model_id = model_id or self.default_model
        
        if not model_id:
            self.logger.error("Nenhum modelo padrão definido")
            return None
        
        if model_id not in self.models:
            self.logger.error(f"Modelo {model_id} não encontrado")
            return None
        
        try:
            model = self.models[model_id]
            response = await model.generate(prompt, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta com modelo {model_id}: {e}")
            return None
    
    async def generate_embedding(self, text: str, model_id: Optional[str] = None, **kwargs) -> Optional[List[float]]:
        """
        Gera embeddings para o texto usando o modelo especificado ou o padrão.
        
        Args:
            text: Texto para gerar embeddings
            model_id: Identificador do modelo (usa o padrão se None)
            **kwargs: Argumentos adicionais específicos do modelo
            
        Returns:
            Lista de embeddings ou None em caso de erro
        """
        model_id = model_id or self.default_model
        
        if not model_id:
            self.logger.error("Nenhum modelo padrão definido")
            return None
        
        if model_id not in self.models:
            self.logger.error(f"Modelo {model_id} não encontrado")
            return None
        
        try:
            model = self.models[model_id]
            embeddings = await model.embed(text, **kwargs)
            return embeddings
        except Exception as e:
            self.logger.error(f"Erro ao gerar embeddings com modelo {model_id}: {e}")
            return None
    
    async def moderate_content(self, text: str, model_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Modera o conteúdo usando o modelo especificado ou o padrão.
        
        Args:
            text: Texto para moderar
            model_id: Identificador do modelo (usa o padrão se None)
            
        Returns:
            Resultado da moderação ou None em caso de erro
        """
        model_id = model_id or self.default_model
        
        if not model_id:
            self.logger.error("Nenhum modelo padrão definido")
            return None
        
        if model_id not in self.models:
            self.logger.error(f"Modelo {model_id} não encontrado")
            return None
        
        try:
            model = self.models[model_id]
            result = await model.moderate(text)
            return result
        except Exception as e:
            self.logger.error(f"Erro ao moderar conteúdo com modelo {model_id}: {e}")
            return None
    
    def get_model(self, model_id: str) -> Optional[BaseModel]:
        """
        Obtém um modelo específico.
        
        Args:
            model_id: Identificador do modelo
            
        Returns:
            Modelo ou None se não encontrado
        """
        return self.models.get(model_id)
    
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Lista todos os modelos registrados.
        
        Returns:
            Dicionário com informações dos modelos
        """
        result = {}
        for model_id, model in self.models.items():
            # Não incluir a chave API por segurança
            config = asdict(model.config)
            config["api_key"] = "***" if config["api_key"] else ""
            
            result[model_id] = {
                "name": model.name,
                "provider": model.provider,
                "is_default": model_id == self.default_model,
                "config": config
            }
        return result
    
    def save_config(self) -> bool:
        """
        Salva a configuração de todos os modelos.
        
        Returns:
            True se a configuração foi salva com sucesso
        """
        try:
            configs = {}
            for model_id, model in self.models.items():
                # Converte a configuração para dicionário
                configs[model_id] = asdict(model.config)
            
            # Adiciona informação sobre o modelo padrão
            meta = {
                "default_model": self.default_model,
                "version": "1.0.0"
            }
            
            # Salva no arquivo
            config_path = self.config_dir / "models.json"
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({"meta": meta, "models": configs}, f, indent=2)
                
            self.logger.info(f"Configuração salva em {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {e}")
            return False
    
    def load_config(self) -> bool:
        """
        Carrega a configuração de todos os modelos.
        
        Returns:
            True se a configuração foi carregada com sucesso
        """
        try:
            config_path = self.config_dir / "models.json"
            if not config_path.exists():
                self.logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
                return False
                
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Registra os modelos
            for model_id, config_dict in data.get("models", {}).items():
                config = ModelConfig(**config_dict)
                self.register_model(model_id, config)
                
            # Define o modelo padrão
            default_model = data.get("meta", {}).get("default_model")
            if default_model:
                self.set_default_model(default_model)
                
            self.logger.info(f"Configuração carregada de {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração: {e}")
            return False

# Instância global para uso em todo o sistema
model_manager = ModelManager() 