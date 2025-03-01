#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Implementação do Modelo OpenAI
Adaptado do framework ElizaOS
Versão: 1.0.0 - Build 2024.02.26

Este módulo implementa a integração com a API da OpenAI.
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
import aiohttp
from ..model_manager import BaseModel, ModelConfig

class OpenAIModel(BaseModel):
    """Implementação do modelo OpenAI."""
    
    def __init__(self, config: ModelConfig):
        """Inicializa o modelo OpenAI."""
        super().__init__(config)
        self.base_url = "https://api.openai.com/v1"
        self.session = None
        self.logger.info(f"Modelo OpenAI inicializado: {self.name}")
        
    async def _ensure_session(self):
        """Garante que a sessão HTTP está inicializada."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
    
    async def _close_session(self):
        """Fecha a sessão HTTP."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Gera uma resposta usando o modelo OpenAI.
        
        Args:
            prompt: Texto de entrada
            **kwargs: Argumentos adicionais
            
        Returns:
            Resposta gerada
        """
        await self._ensure_session()
        
        # Mescla as configurações padrão com as fornecidas
        params = {
            "model": self.config.model_name or "gpt-4",
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            **self.config.options,
            **kwargs
        }
        
        # Prepara os dados para a API
        if "gpt-4" in params["model"] or "gpt-3.5" in params["model"]:
            # Formato para modelos de chat
            data = {
                "model": params["model"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": params["temperature"],
                "max_tokens": params["max_tokens"]
            }
            endpoint = f"{self.base_url}/chat/completions"
        else:
            # Formato para modelos de completions
            data = {
                "model": params["model"],
                "prompt": prompt,
                "temperature": params["temperature"],
                "max_tokens": params["max_tokens"]
            }
            endpoint = f"{self.base_url}/completions"
        
        # Remove parâmetros extras que não são aceitos pela API
        for key in list(kwargs.keys()):
            if key not in data:
                data[key] = kwargs[key]
        
        try:
            self.logger.debug(f"Enviando requisição para OpenAI: {json.dumps(data)[:100]}...")
            
            async with self.session.post(endpoint, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Erro na API OpenAI: {response.status} - {error_text}")
                    return f"Erro na API OpenAI: {response.status}"
                
                result = await response.json()
                
                # Extrai a resposta dependendo do tipo de modelo
                if "gpt-4" in params["model"] or "gpt-3.5" in params["model"]:
                    content = result["choices"][0]["message"]["content"]
                else:
                    content = result["choices"][0]["text"]
                
                self.logger.debug(f"Resposta recebida: {content[:100]}...")
                return content
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta: {e}")
            return f"Erro ao gerar resposta: {str(e)}"
    
    async def embed(self, text: str, **kwargs) -> List[float]:
        """
        Gera embeddings para o texto usando o modelo OpenAI.
        
        Args:
            text: Texto para gerar embeddings
            **kwargs: Argumentos adicionais
            
        Returns:
            Lista de embeddings
        """
        await self._ensure_session()
        
        # Modelo padrão para embeddings
        model = kwargs.get("model", "text-embedding-ada-002")
        
        data = {
            "model": model,
            "input": text
        }
        
        try:
            async with self.session.post(f"{self.base_url}/embeddings", json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Erro na API OpenAI: {response.status} - {error_text}")
                    raise Exception(f"Erro na API OpenAI: {response.status}")
                
                result = await response.json()
                embeddings = result["data"][0]["embedding"]
                
                self.logger.debug(f"Embeddings gerados com {len(embeddings)} dimensões")
                return embeddings
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar embeddings: {e}")
            raise
    
    async def moderate(self, text: str) -> Dict[str, Any]:
        """
        Modera o texto usando a API de moderação da OpenAI.
        
        Args:
            text: Texto para moderar
            
        Returns:
            Resultado da moderação
        """
        await self._ensure_session()
        
        data = {
            "input": text
        }
        
        try:
            async with self.session.post(f"{self.base_url}/moderations", json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Erro na API OpenAI: {response.status} - {error_text}")
                    raise Exception(f"Erro na API OpenAI: {response.status}")
                
                result = await response.json()
                
                # Formata o resultado para um formato mais amigável
                categories = result["results"][0]["categories"]
                scores = result["results"][0]["category_scores"]
                flagged = result["results"][0]["flagged"]
                
                return {
                    "flagged": flagged,
                    "categories": categories,
                    "scores": scores
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao moderar conteúdo: {e}")
            raise
    
    async def __aenter__(self):
        """Suporte para uso com 'async with'."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fecha a sessão ao sair do contexto."""
        await self._close_session() 