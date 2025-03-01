#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Implementação do Modelo Google Gemini
Adaptado do framework ElizaOS
Versão: 1.0.0 - Build 2024.02.26

Este módulo implementa a integração com a API do Google Gemini.
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
import aiohttp
from ..model_manager import BaseModel, ModelConfig

class GeminiModel(BaseModel):
    """Implementação do modelo Google Gemini."""
    
    def __init__(self, config: ModelConfig):
        """Inicializa o modelo Google Gemini."""
        super().__init__(config)
        self.base_url = "https://generativelanguage.googleapis.com/v1"
        self.session = None
        self.logger.info(f"Modelo Google Gemini inicializado: {self.name}")
        
    async def _ensure_session(self):
        """Garante que a sessão HTTP está inicializada."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _close_session(self):
        """Fecha a sessão HTTP."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Gera uma resposta usando o modelo Google Gemini.
        
        Args:
            prompt: Texto de entrada
            **kwargs: Argumentos adicionais
            
        Returns:
            Resposta gerada
        """
        await self._ensure_session()
        
        # Mescla as configurações padrão com as fornecidas
        params = {
            "model": self.config.model_name or "gemini-2.0-flash-exp",
            "temperature": self.config.temperature,
            "max_output_tokens": self.config.max_tokens,
            **self.config.options,
            **kwargs
        }
        
        # Prepara os dados para a API
        model_name = params["model"]
        
        # Formato para modelos Gemini
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": params["temperature"],
                "maxOutputTokens": params["max_output_tokens"],
                "topP": kwargs.get("top_p", 0.95),
                "topK": kwargs.get("top_k", 40)
            }
        }
        
        # Adiciona o system prompt se fornecido
        if "system" in kwargs:
            data["contents"].insert(0, {
                "role": "system",
                "parts": [{"text": kwargs["system"]}]
            })
        
        # Adiciona parâmetros de segurança se fornecidos
        if "safety_settings" in kwargs:
            data["safetySettings"] = kwargs["safety_settings"]
        
        endpoint = f"{self.base_url}/models/{model_name}:generateContent?key={self.api_key}"
        
        try:
            self.logger.debug(f"Enviando requisição para Google Gemini: {json.dumps(data)[:100]}...")
            
            async with self.session.post(endpoint, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Erro na API Google Gemini: {response.status} - {error_text}")
                    return f"Erro na API Google Gemini: {response.status}"
                
                result = await response.json()
                
                # Extrai a resposta do modelo Gemini
                try:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    self.logger.debug(f"Resposta recebida: {content[:100]}...")
                    return content
                except (KeyError, IndexError) as e:
                    self.logger.error(f"Erro ao extrair resposta: {e}, resposta: {result}")
                    return "Erro ao extrair resposta do modelo Gemini"
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta: {e}")
            return f"Erro ao gerar resposta: {str(e)}"
    
    async def embed(self, text: str, **kwargs) -> List[float]:
        """
        Gera embeddings para o texto usando o modelo Google Gemini.
        
        Args:
            text: Texto para gerar embeddings
            **kwargs: Argumentos adicionais
            
        Returns:
            Lista de embeddings
        """
        await self._ensure_session()
        
        # Modelo padrão para embeddings
        model = kwargs.get("model", "embedding-001")
        
        data = {
            "model": f"models/{model}",
            "content": {
                "parts": [
                    {"text": text}
                ]
            }
        }
        
        endpoint = f"{self.base_url}/models/{model}:embedContent?key={self.api_key}"
        
        try:
            async with self.session.post(endpoint, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Erro na API Google Gemini: {response.status} - {error_text}")
                    raise Exception(f"Erro na API Google Gemini: {response.status}")
                
                result = await response.json()
                
                try:
                    embeddings = result["embedding"]["values"]
                    self.logger.debug(f"Embeddings gerados com {len(embeddings)} dimensões")
                    return embeddings
                except KeyError as e:
                    self.logger.error(f"Erro ao extrair embeddings: {e}, resposta: {result}")
                    raise Exception(f"Erro ao extrair embeddings: {e}")
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar embeddings: {e}")
            
            # Fallback para OpenAI se configurado
            if kwargs.get("fallback_to_openai", True) and kwargs.get("openai_api_key"):
                self.logger.warning("Usando OpenAI como fallback para embeddings")
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
                except Exception as fallback_error:
                    self.logger.error(f"Erro ao usar fallback para embeddings: {fallback_error}")
            
            # Retorna um vetor de embeddings vazio em caso de erro
            return [0.0] * 768  # Dimensão típica dos embeddings do Gemini
    
    async def moderate(self, text: str) -> Dict[str, Any]:
        """
        Modera o texto usando a API do Google Gemini.
        
        Args:
            text: Texto para moderar
            
        Returns:
            Resultado da moderação
        """
        await self._ensure_session()
        
        # Gemini tem moderação integrada na API de geração
        # Vamos usar o modelo para avaliar o conteúdo
        
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": text}]
                }
            ],
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
        }
        
        model_name = self.config.model_name or "gemini-2.0-flash-exp"
        endpoint = f"{self.base_url}/models/{model_name}:generateContent?key={self.api_key}"
        
        try:
            async with self.session.post(endpoint, json=data) as response:
                result = await response.json()
                
                # Verifica se há bloqueios de segurança
                if "promptFeedback" in result and "safetyRatings" in result["promptFeedback"]:
                    safety_ratings = result["promptFeedback"]["safetyRatings"]
                    
                    # Formata o resultado para um formato compatível com outros provedores
                    categories = {}
                    scores = {}
                    flagged = False
                    
                    for rating in safety_ratings:
                        category = rating["category"].lower().replace("harm_category_", "")
                        probability = rating.get("probability", "NEGLIGIBLE")
                        
                        # Converte a probabilidade em um valor numérico
                        score_map = {
                            "NEGLIGIBLE": 0.0,
                            "LOW": 0.25,
                            "MEDIUM": 0.5,
                            "HIGH": 0.75,
                            "VERY_HIGH": 1.0
                        }
                        
                        score = score_map.get(probability, 0.0)
                        blocked = score >= 0.5  # Considera bloqueado se for MEDIUM ou acima
                        
                        categories[category] = blocked
                        scores[category] = score
                        
                        if blocked:
                            flagged = True
                    
                    return {
                        "flagged": flagged,
                        "categories": categories,
                        "scores": scores
                    }
                
                # Se não houver informações de segurança, retorna um resultado padrão
                return {
                    "flagged": False,
                    "categories": {
                        "harassment": False,
                        "hate_speech": False,
                        "sexually_explicit": False,
                        "dangerous_content": False
                    },
                    "scores": {
                        "harassment": 0.0,
                        "hate_speech": 0.0,
                        "sexually_explicit": 0.0,
                        "dangerous_content": 0.0
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao moderar conteúdo: {e}")
            # Retorna um resultado padrão em caso de erro
            return {
                "flagged": False,
                "categories": {
                    "harassment": False,
                    "hate_speech": False,
                    "sexually_explicit": False,
                    "dangerous_content": False
                },
                "scores": {
                    "harassment": 0.0,
                    "hate_speech": 0.0,
                    "sexually_explicit": 0.0,
                    "dangerous_content": 0.0
                }
            }
    
    async def __aenter__(self):
        """Suporte para uso com 'async with'."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fecha a sessão ao sair do contexto."""
        await self._close_session() 