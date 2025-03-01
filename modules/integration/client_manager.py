#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Client Integration Manager
Adaptado do framework ElizaOS
Versão: 1.0.0 - Build 2024.02.26

Este módulo gerencia diferentes clientes de integração (Telegram, Discord, Twitter, etc.)
permitindo que o sistema se comunique através de múltiplas plataformas.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("✨quantum-integration✨")

@dataclass
class ClientConfig:
    """Configuração de cliente de integração."""
    name: str
    enabled: bool = True
    api_keys: Dict[str, str] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)

class BaseClient:
    """Cliente base para todas as integrações."""
    
    def __init__(self, config: ClientConfig):
        """Inicializa o cliente base."""
        self.config = config
        self.name = config.name
        self.enabled = config.enabled
        self.logger = logging.getLogger(f"✨client-{self.name}✨")
        self.handlers = []
        
    async def start(self):
        """Inicia o cliente. Deve ser implementado pelas subclasses."""
        raise NotImplementedError("Método start() deve ser implementado pela subclasse")
        
    async def stop(self):
        """Para o cliente. Deve ser implementado pelas subclasses."""
        raise NotImplementedError("Método stop() deve ser implementado pela subclasse")
        
    async def send_message(self, target: str, message: str, **kwargs):
        """Envia uma mensagem. Deve ser implementado pelas subclasses."""
        raise NotImplementedError("Método send_message() deve ser implementado pela subclasse")
        
    def register_handler(self, handler: Callable):
        """Registra um manipulador de mensagens."""
        self.handlers.append(handler)
        self.logger.info(f"Manipulador registrado: {handler.__name__}")

class ClientManager:
    """Gerenciador de clientes de integração inspirado no ElizaOS."""
    
    def __init__(self):
        """Inicializa o gerenciador de clientes."""
        self.clients = {}
        self.message_handlers = []
        self.logger = logging.getLogger("✨quantum-integration✨")
        self.config_dir = Path("config/integration")
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def register_client(self, client_type: str, config: ClientConfig) -> bool:
        """
        Registra um novo cliente de integração.
        
        Args:
            client_type: Tipo de cliente (telegram, discord, twitter, web)
            config: Configuração do cliente
            
        Returns:
            True se o cliente foi registrado com sucesso
        """
        if client_type in self.clients:
            self.logger.warning(f"Cliente {client_type} já registrado, substituindo")
        
        # Importação dinâmica do cliente apropriado
        try:
            if client_type == "telegram":
                from .clients.telegram import TelegramClient
                self.clients[client_type] = TelegramClient(config)
            elif client_type == "discord":
                from .clients.discord import DiscordClient
                self.clients[client_type] = DiscordClient(config)
            elif client_type == "twitter":
                from .clients.twitter import TwitterClient
                self.clients[client_type] = TwitterClient(config)
            elif client_type == "web":
                from .clients.web import WebClient
                self.clients[client_type] = WebClient(config)
            else:
                self.logger.error(f"Tipo de cliente desconhecido: {client_type}")
                return False
            
            # Registra os manipuladores globais no cliente
            for handler in self.message_handlers:
                self.clients[client_type].register_handler(handler)
            
            self.logger.info(f"Cliente {client_type} registrado com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao registrar cliente {client_type}: {e}")
            return False
    
    def register_message_handler(self, handler: Callable) -> None:
        """
        Registra um manipulador de mensagens global.
        
        Args:
            handler: Função de manipulação de mensagens
        """
        self.message_handlers.append(handler)
        
        # Registra o manipulador em todos os clientes existentes
        for client in self.clients.values():
            client.register_handler(handler)
            
        self.logger.info(f"Manipulador de mensagens global registrado: {handler.__name__}")
    
    async def start_all_clients(self) -> None:
        """Inicia todos os clientes registrados."""
        for client_type, client in self.clients.items():
            if not client.enabled:
                self.logger.info(f"Cliente {client_type} desativado, pulando")
                continue
                
            try:
                await client.start()
                self.logger.info(f"Cliente {client_type} iniciado")
            except Exception as e:
                self.logger.error(f"Erro ao iniciar cliente {client_type}: {e}")
    
    async def stop_all_clients(self) -> None:
        """Para todos os clientes registrados."""
        for client_type, client in self.clients.items():
            try:
                await client.stop()
                self.logger.info(f"Cliente {client_type} parado")
            except Exception as e:
                self.logger.error(f"Erro ao parar cliente {client_type}: {e}")
    
    async def send_message(self, client_type: str, target: str, message: str, **kwargs) -> bool:
        """
        Envia uma mensagem através de um cliente específico.
        
        Args:
            client_type: Tipo de cliente (telegram, discord, twitter, web)
            target: Identificador do alvo (chat_id, channel_id, etc.)
            message: Mensagem a ser enviada
            **kwargs: Argumentos adicionais específicos do cliente
            
        Returns:
            True se a mensagem foi enviada com sucesso
        """
        if client_type not in self.clients:
            self.logger.error(f"Cliente {client_type} não encontrado")
            return False
            
        client = self.clients[client_type]
        if not client.enabled:
            self.logger.warning(f"Cliente {client_type} desativado")
            return False
            
        try:
            await client.send_message(target, message, **kwargs)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem via {client_type}: {e}")
            return False
    
    async def broadcast_message(self, message: str, **kwargs) -> Dict[str, bool]:
        """
        Envia uma mensagem para todos os clientes ativos.
        
        Args:
            message: Mensagem a ser enviada
            **kwargs: Argumentos adicionais específicos dos clientes
            
        Returns:
            Dicionário com o status de envio para cada cliente
        """
        results = {}
        for client_type, client in self.clients.items():
            if not client.enabled:
                results[client_type] = False
                continue
                
            try:
                # Cada cliente deve implementar um método broadcast
                await client.broadcast_message(message, **kwargs)
                results[client_type] = True
            except Exception as e:
                self.logger.error(f"Erro ao fazer broadcast via {client_type}: {e}")
                results[client_type] = False
                
        return results
    
    def get_client(self, client_type: str) -> Optional[BaseClient]:
        """
        Obtém um cliente específico.
        
        Args:
            client_type: Tipo de cliente
            
        Returns:
            Cliente ou None se não encontrado
        """
        return self.clients.get(client_type)
    
    def save_config(self) -> bool:
        """
        Salva a configuração de todos os clientes.
        
        Returns:
            True se a configuração foi salva com sucesso
        """
        import json
        
        try:
            configs = {}
            for client_type, client in self.clients.items():
                # Converte a configuração para dicionário
                from dataclasses import asdict
                configs[client_type] = asdict(client.config)
            
            # Salva no arquivo
            config_path = self.config_dir / "clients.json"
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(configs, f, indent=2)
                
            self.logger.info(f"Configuração salva em {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {e}")
            return False
    
    def load_config(self) -> bool:
        """
        Carrega a configuração de todos os clientes.
        
        Returns:
            True se a configuração foi carregada com sucesso
        """
        import json
        
        try:
            config_path = self.config_dir / "clients.json"
            if not config_path.exists():
                self.logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
                return False
                
            with open(config_path, "r", encoding="utf-8") as f:
                configs = json.load(f)
                
            # Registra os clientes
            for client_type, config_dict in configs.items():
                config = ClientConfig(**config_dict)
                self.register_client(client_type, config)
                
            self.logger.info(f"Configuração carregada de {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração: {e}")
            return False

# Instância global para uso em todo o sistema
client_manager = ClientManager() 