#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Implementação do Modelo Anthropic (Claude)
Adaptado do framework ElizaOS
Versão: 1.0.0 - Build 2024.02.26

Este módulo implementa a integração com a API da Anthropic (Claude).
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
import aiohttp
from ..model_manager import BaseModel, ModelConfig

class AnthropicModel(BaseModel):
    """Implementação do modelo Anthropic (Claude)."""
    
    def __init__(self, config: ModelConfig):
        """Inicializa o modelo Anthropic."""
        super().__init__(config)
        self.base_url = "https://api.anthropic.com/v1"
        self.session = None
        self.api_version = "2023-06-01"  # Versão da API Anthropic
        self.logger.info(f"Modelo Anthropic inicializado: {self.name}")
        
    async def _ensure_session(self):
        """Garante que a sessão HTTP está inicializada."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": self.api_version,
                    "Content-Type": "application/json"
                }
            )
    
    async def _close_session(self):
        """Fecha a sessão HTTP."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Gera uma resposta usando o modelo Anthropic Claude.
        
        Args:
            prompt: Texto de entrada
            **kwargs: Argumentos adicionais
            
        Returns:
            Resposta gerada
        """
        await self._ensure_session()
        
        # Mescla as configurações padrão com as fornecidas
        params = {
            "model": self.config.model_name or "claude-3-opus-20240229",
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            **self.config.options,
            **kwargs
        }
        
        # Prepara os dados para a API
        system_prompt = kwargs.get("system", "")
        
        # Formato para modelos Claude
        data = {
            "model": params["model"],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": params["temperature"],
            "max_tokens": params["max_tokens"]
        }
        
        # Adiciona o system prompt se fornecido
        if system_prompt:
            data["system"] = system_prompt
            
        # Adiciona parâmetros adicionais específicos do Claude
        if "top_p" in kwargs:
            data["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            data["top_k"] = kwargs["top_k"]
        if "stop_sequences" in kwargs:
            data["stop_sequences"] = kwargs["stop_sequences"]
        
        endpoint = f"{self.base_url}/messages"
        
        try:
            self.logger.debug(f"Enviando requisição para Anthropic: {json.dumps(data)[:100]}...")
            
            async with self.session.post(endpoint, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Erro na API Anthropic: {response.status} - {error_text}")
                    return f"Erro na API Anthropic: {response.status}"
                
                result = await response.json()
                
                # Extrai a resposta do modelo Claude
                content = result["content"][0]["text"]
                
                self.logger.debug(f"Resposta recebida: {content[:100]}...")
                return content
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta: {e}")
            return f"Erro ao gerar resposta: {str(e)}"
    
    async def embed(self, text: str, **kwargs) -> List[float]:
        """
        Gera embeddings para o texto usando o modelo Anthropic.
        
        Args:
            text: Texto para gerar embeddings
            **kwargs: Argumentos adicionais
            
        Returns:
            Lista de embeddings
        """
        # Anthropic ainda não oferece um serviço de embeddings público
        # Esta é uma implementação de fallback que usa a API de mensagens
        self.logger.warning("Anthropic não oferece API de embeddings. Usando OpenAI como fallback.")
        
        # Importa o modelo OpenAI para usar como fallback
        try:
            from .openai import OpenAIModel
            from ..model_manager import ModelConfig
            
            # Cria uma configuração temporária para o modelo OpenAI
            openai_config = ModelConfig(
                name="OpenAI-Embedding-Fallback",
                provider="openai",
                api_key=kwargs.get("openai_api_key", ""),
                model_name="text-embedding-ada-002"
            )
            
            # Cria uma instância temporária do modelo OpenAI
            openai_model = OpenAIModel(openai_config)
            
            # Gera embeddings usando o modelo OpenAI
            embeddings = await openai_model.embed(text, **kwargs)
            
            # Fecha a sessão do modelo OpenAI
            await openai_model._close_session()
            
            return embeddings
        except Exception as e:
            self.logger.error(f"Erro ao gerar embeddings com fallback: {e}")
            # Retorna um vetor de embeddings vazio em caso de erro
            return [0.0] * 1536  # Dimensão padrão dos embeddings da OpenAI
    
    async def moderate(self, text: str) -> Dict[str, Any]:
        """
        Modera o texto usando a API do Claude.
        
        Args:
            text: Texto para moderar
            
        Returns:
            Resultado da moderação
        """
        await self._ensure_session()
        
        # Claude não tem uma API específica de moderação, então usamos o modelo para avaliar
        prompt = """
        Por favor, avalie o seguinte texto quanto a conteúdo inadequado.
        Responda apenas com um objeto JSON contendo as seguintes categorias:
        - "flagged": booleano indicando se o texto contém conteúdo inadequado
        - "categories": objeto com as categorias (violence, sexual, hate, harassment, self-harm, etc.) e valores booleanos
        - "scores": objeto com as mesmas categorias e pontuações de 0 a 1
        
        Texto para avaliar:
        """
        
        try:
            # Usa o próprio modelo para avaliar o conteúdo
            response = await self.generate(prompt + text, temperature=0.0, max_tokens=500)
            
            # Tenta extrair o JSON da resposta
            try:
                # Encontra o início e fim do JSON na resposta
                start = response.find("{")
                end = response.rfind("}") + 1
                
                if start >= 0 and end > start:
                    json_str = response[start:end]
                    result = json.loads(json_str)
                    
                    # Verifica se o resultado tem a estrutura esperada
                    if "flagged" in result and "categories" in result and "scores" in result:
                        return result
            except json.JSONDecodeError:
                pass
            
            # Se não conseguir extrair o JSON, retorna um resultado padrão
            self.logger.warning("Não foi possível extrair resultado de moderação estruturado")
            return {
                "flagged": False,
                "categories": {
                    "violence": False,
                    "sexual": False,
                    "hate": False,
                    "harassment": False,
                    "self-harm": False,
                    "deceptive": False
                },
                "scores": {
                    "violence": 0.0,
                    "sexual": 0.0,
                    "hate": 0.0,
                    "harassment": 0.0,
                    "self-harm": 0.0,
                    "deceptive": 0.0
                }
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