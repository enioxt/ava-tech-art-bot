#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - API Adapter
Adaptador para integração com APIs externas
Versão: 1.0.0 - Build 2024.03.26

Este módulo implementa adaptadores para comunicação com APIs externas,
permitindo que o sistema EVA & GUARANI se integre com serviços de terceiros.
"""

import logging
import aiohttp
import json
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from datetime import datetime

# Configuração de logging
logger = logging.getLogger("✨api-adapter✨")

class APIAdapter:
    """
    Adaptador para comunicação com APIs externas.
    Fornece uma interface unificada para realizar requisições HTTP.
    """
    
    def __init__(self, base_url: str = "", headers: Optional[Dict[str, str]] = None, 
                 timeout: int = 30, retry_attempts: int = 3):
        """
        Inicializa o adaptador de API.
        
        Args:
            base_url: URL base para todas as requisições
            headers: Cabeçalhos padrão para todas as requisições
            timeout: Tempo limite para requisições em segundos
            retry_attempts: Número de tentativas em caso de falha
        """
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session = None
        self.logger = logger
        
    async def initialize(self):
        """Inicializa o adaptador criando uma sessão HTTP."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
            self.logger.info(f"Sessão HTTP inicializada para {self.base_url}")
        
    async def close(self):
        """Fecha a sessão HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("Sessão HTTP fechada")
            
    async def request(self, method: str, endpoint: str, 
                     params: Optional[Dict[str, Any]] = None,
                     data: Optional[Any] = None,
                     json_data: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None,
                     timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Realiza uma requisição HTTP.
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE, etc)
            endpoint: Endpoint da API
            params: Parâmetros de query string
            data: Dados para enviar no corpo da requisição
            json_data: Dados JSON para enviar no corpo da requisição
            headers: Cabeçalhos adicionais para esta requisição
            timeout: Tempo limite para esta requisição
            
        Returns:
            Resposta da API como um dicionário
        """
        if self.session is None or self.session.closed:
            await self.initialize()
            
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        request_headers = {**self.headers, **(headers or {})}
        request_timeout = aiohttp.ClientTimeout(total=timeout or self.timeout)
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                self.logger.debug(f"Requisição {method} para {url} (tentativa {attempt}/{self.retry_attempts})")
                
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=request_headers,
                    timeout=request_timeout
                ) as response:
                    response_data = await response.json(content_type=None)
                    
                    if response.status >= 400:
                        self.logger.error(f"Erro na requisição: {response.status} - {response_data}")
                        if attempt == self.retry_attempts:
                            response.raise_for_status()
                        continue
                    
                    self.logger.debug(f"Resposta recebida: {response.status}")
                    return response_data
                    
            except aiohttp.ClientError as e:
                self.logger.error(f"Erro de cliente HTTP: {str(e)}")
                if attempt == self.retry_attempts:
                    raise
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout na requisição após {timeout or self.timeout}s")
                if attempt == self.retry_attempts:
                    raise
            
            # Espera exponencial entre tentativas
            if attempt < self.retry_attempts:
                wait_time = 2 ** attempt
                self.logger.info(f"Aguardando {wait_time}s antes da próxima tentativa")
                await asyncio.sleep(wait_time)
                
        raise Exception(f"Falha após {self.retry_attempts} tentativas")
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza uma requisição GET."""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza uma requisição POST."""
        return await self.request("POST", endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza uma requisição PUT."""
        return await self.request("PUT", endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza uma requisição DELETE."""
        return await self.request("DELETE", endpoint, **kwargs)
    
    async def patch(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza uma requisição PATCH."""
        return await self.request("PATCH", endpoint, **kwargs)


class APIAdapterManager:
    """
    Gerenciador de adaptadores de API.
    Permite registrar e gerenciar múltiplos adaptadores para diferentes serviços.
    """
    
    def __init__(self, config_path: str = "config/integration/api_adapters.json"):
        """
        Inicializa o gerenciador de adaptadores.
        
        Args:
            config_path: Caminho para o arquivo de configuração dos adaptadores
        """
        self.adapters: Dict[str, APIAdapter] = {}
        self.config_path = config_path
        self.logger = logger
        
    async def initialize(self):
        """Inicializa o gerenciador carregando as configurações e criando os adaptadores."""
        self.logger.info("Inicializando gerenciador de adaptadores de API")
        config = self._load_config()
        
        for adapter_name, adapter_config in config.items():
            self.register_adapter(
                name=adapter_name,
                base_url=adapter_config.get("base_url", ""),
                headers=adapter_config.get("headers", {}),
                timeout=adapter_config.get("timeout", 30),
                retry_attempts=adapter_config.get("retry_attempts", 3)
            )
            
        self.logger.info(f"Gerenciador inicializado com {len(self.adapters)} adaptadores")
        
    def _load_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Carrega a configuração dos adaptadores.
        
        Returns:
            Configuração carregada
        """
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                # Criar configuração padrão
                default_config = {
                    "default": {
                        "base_url": "",
                        "headers": {
                            "User-Agent": "EVA-GUARANI/1.0.0",
                            "Content-Type": "application/json"
                        },
                        "timeout": 30,
                        "retry_attempts": 3
                    }
                }
                # Garantir que o diretório existe
                config_file.parent.mkdir(parents=True, exist_ok=True)
                # Salvar configuração padrão
                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, indent=4)
                self.logger.info(f"Configuração padrão criada em: {self.config_path}")
                return default_config
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração: {e}")
            return {"default": {}}
            
    def register_adapter(self, name: str, base_url: str = "", 
                         headers: Optional[Dict[str, str]] = None,
                         timeout: int = 30, retry_attempts: int = 3) -> APIAdapter:
        """
        Registra um novo adaptador.
        
        Args:
            name: Nome do adaptador
            base_url: URL base para todas as requisições
            headers: Cabeçalhos padrão para todas as requisições
            timeout: Tempo limite para requisições em segundos
            retry_attempts: Número de tentativas em caso de falha
            
        Returns:
            O adaptador criado
        """
        adapter = APIAdapter(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            retry_attempts=retry_attempts
        )
        self.adapters[name] = adapter
        self.logger.info(f"Adaptador '{name}' registrado com sucesso")
        return adapter
        
    def get_adapter(self, name: str) -> APIAdapter:
        """
        Obtém um adaptador pelo nome.
        
        Args:
            name: Nome do adaptador
            
        Returns:
            O adaptador solicitado
            
        Raises:
            KeyError: Se o adaptador não existir
        """
        if name not in self.adapters:
            raise KeyError(f"Adaptador '{name}' não encontrado")
        return self.adapters[name]
        
    async def close_all(self):
        """Fecha todas as sessões HTTP de todos os adaptadores."""
        self.logger.info("Fechando todas as sessões HTTP")
        for name, adapter in self.adapters.items():
            await adapter.close()
            self.logger.debug(f"Sessão do adaptador '{name}' fechada")
