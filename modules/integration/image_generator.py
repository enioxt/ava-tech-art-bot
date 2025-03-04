#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de Geração de Imagens - EVA & GUARANI
--------------------------------------------
Este módulo gerencia a geração de imagens através de diversas APIs,
incluindo Stable Diffusion, Replicate e outras alternativas gratuitas.

Versão: 1.0.0
"""

import os
import json
import logging
import requests
import time
import base64
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
from PIL import Image
import io
import asyncio
import aiohttp

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/image_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("image-generator")

class ImageGenerator:
    """Gerencia a geração de imagens através de diversas APIs."""
    
    def __init__(self, config_path: str = "config/telegram_config.json"):
        """
        Inicializa o gerador de imagens.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Configurações das APIs
        self.stable_diffusion_config = self.config.get("stable_diffusion_api", {})
        self.replicate_config = self.config.get("replicate_api", {})
        self.unsplash_config = self.config.get("unsplash_api", {})
        self.pexels_config = self.config.get("pexels_api", {})
        self.pixabay_config = self.config.get("pixabay_api", {})
        
        # Diretório para salvar imagens geradas
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)
        
        # Estatísticas de uso
        self.stats = {
            "generation_count": 0,
            "search_count": 0,
            "total_processing_time": 0,
            "last_processing_time": 0,
            "errors": 0
        }
        
        logger.info("Módulo de geração de imagens inicializado")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega a configuração do arquivo.
        
        Returns:
            Dict: Configuração carregada
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {}
    
    async def generate_image_stable_diffusion(self, 
                                             prompt: str, 
                                             negative_prompt: str = "",
                                             width: int = 512, 
                                             height: int = 512,
                                             num_inference_steps: int = 30,
                                             guidance_scale: float = 7.5) -> Optional[str]:
        """
        Gera uma imagem usando a API do Stable Diffusion.
        
        Args:
            prompt: Descrição da imagem a ser gerada
            negative_prompt: O que não deve aparecer na imagem
            width: Largura da imagem
            height: Altura da imagem
            num_inference_steps: Número de passos de inferência
            guidance_scale: Escala de orientação
            
        Returns:
            str: Caminho para a imagem gerada ou None em caso de erro
        """
        if not self.stable_diffusion_config:
            logger.warning("API do Stable Diffusion não configurada")
            return None
        
        api_key = self.stable_diffusion_config.get("key")
        api_url = self.stable_diffusion_config.get("url", "https://stablediffusionapi.com/api/v3/text2img")
        
        if not api_key:
            logger.warning("Chave da API do Stable Diffusion não configurada")
            return None
        
        start_time = time.time()
        
        try:
            payload = {
                "key": api_key,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": str(width),
                "height": str(height),
                "samples": "1",
                "num_inference_steps": str(num_inference_steps),
                "guidance_scale": guidance_scale,
                "safety_checker": "yes",
                "webhook": None,
                "track_id": None
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Erro na API do Stable Diffusion: {response.status}")
                        return None
                    
                    result = await response.json()
                    
                    if result.get("status") == "success":
                        image_url = result.get("output", [None])[0]
                        if not image_url:
                            logger.error("URL da imagem não encontrada na resposta")
                            return None
                        
                        # Baixar a imagem
                        async with session.get(image_url) as img_response:
                            if img_response.status != 200:
                                logger.error(f"Erro ao baixar imagem: {img_response.status}")
                                return None
                            
                            image_data = await img_response.read()
                            
                            # Salvar a imagem
                            filename = f"sd_{uuid.uuid4()}.png"
                            image_path = self.output_dir / filename
                            
                            with open(image_path, "wb") as f:
                                f.write(image_data)
                            
                            # Atualizar estatísticas
                            self.stats["generation_count"] += 1
                            processing_time = time.time() - start_time
                            self.stats["last_processing_time"] = processing_time
                            self.stats["total_processing_time"] += processing_time
                            
                            logger.info(f"Imagem gerada com sucesso: {image_path}, tempo: {processing_time:.2f}s")
                            
                            return str(image_path)
                    else:
                        error_msg = result.get("message", "Erro desconhecido")
                        logger.error(f"Erro na geração de imagem: {error_msg}")
                        self.stats["errors"] += 1
                        return None
                        
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Erro ao gerar imagem com Stable Diffusion: {e}")
            return None
    
    async def generate_image_replicate(self, 
                                      prompt: str,
                                      negative_prompt: str = "",
                                      width: int = 512,
                                      height: int = 512) -> Optional[str]:
        """
        Gera uma imagem usando a API do Replicate (alternativa gratuita).
        
        Args:
            prompt: Descrição da imagem a ser gerada
            negative_prompt: O que não deve aparecer na imagem
            width: Largura da imagem
            height: Altura da imagem
            
        Returns:
            str: Caminho para a imagem gerada ou None em caso de erro
        """
        if not self.replicate_config:
            logger.warning("API do Replicate não configurada")
            return None
        
        api_key = self.replicate_config.get("key")
        
        if not api_key:
            logger.warning("Chave da API do Replicate não configurada")
            return None
        
        start_time = time.time()
        
        try:
            # Modelo Stable Diffusion no Replicate
            model = "stability-ai/sdxl:c221b2b8ef527988fb59bf24a8b97c4561f1c671f73bd389f866bfb27c061316"
            api_url = f"https://api.replicate.com/v1/predictions"
            
            headers = {
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "version": model,
                "input": {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height,
                    "num_outputs": 1
                }
            }
            
            async with aiohttp.ClientSession() as session:
                # Iniciar a predição
                async with session.post(api_url, headers=headers, json=payload) as response:
                    if response.status != 201:
                        logger.error(f"Erro ao iniciar predição no Replicate: {response.status}")
                        return None
                    
                    result = await response.json()
                    prediction_id = result.get("id")
                    
                    if not prediction_id:
                        logger.error("ID de predição não encontrado na resposta")
                        return None
                    
                    # Verificar status da predição
                    status_url = f"{api_url}/{prediction_id}"
                    
                    # Aguardar a conclusão da predição
                    while True:
                        await asyncio.sleep(2)  # Verificar a cada 2 segundos
                        
                        async with session.get(status_url, headers=headers) as status_response:
                            if status_response.status != 200:
                                logger.error(f"Erro ao verificar status da predição: {status_response.status}")
                                return None
                            
                            status_result = await status_response.json()
                            status = status_result.get("status")
                            
                            if status == "succeeded":
                                output = status_result.get("output")
                                if isinstance(output, list) and len(output) > 0:
                                    image_url = output[0]
                                    
                                    # Baixar a imagem
                                    async with session.get(image_url) as img_response:
                                        if img_response.status != 200:
                                            logger.error(f"Erro ao baixar imagem: {img_response.status}")
                                            return None
                                        
                                        image_data = await img_response.read()
                                        
                                        # Salvar a imagem
                                        filename = f"replicate_{uuid.uuid4()}.png"
                                        image_path = self.output_dir / filename
                                        
                                        with open(image_path, "wb") as f:
                                            f.write(image_data)
                                        
                                        # Atualizar estatísticas
                                        self.stats["generation_count"] += 1
                                        processing_time = time.time() - start_time
                                        self.stats["last_processing_time"] = processing_time
                                        self.stats["total_processing_time"] += processing_time
                                        
                                        logger.info(f"Imagem gerada com sucesso via Replicate: {image_path}, tempo: {processing_time:.2f}s")
                                        
                                        return str(image_path)
                                else:
                                    logger.error("URL da imagem não encontrada na resposta")
                                    return None
                            elif status == "failed":
                                error = status_result.get("error", "Erro desconhecido")
                                logger.error(f"Falha na geração de imagem: {error}")
                                self.stats["errors"] += 1
                                return None
                            elif status in ["starting", "processing"]:
                                # Continuar aguardando
                                continue
                            else:
                                logger.error(f"Status desconhecido: {status}")
                                return None
                                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Erro ao gerar imagem com Replicate: {e}")
            return None
    
    async def search_image(self, query: str, source: str = "all") -> Optional[List[Dict[str, Any]]]:
        """
        Busca imagens em bancos de imagens gratuitos.
        
        Args:
            query: Termo de busca
            source: Fonte da busca (unsplash, pexels, pixabay ou all)
            
        Returns:
            List: Lista de resultados de imagens ou None em caso de erro
        """
        start_time = time.time()
        results = []
        
        try:
            if source in ["unsplash", "all"] and self.unsplash_config.get("key"):
                unsplash_results = await self._search_unsplash(query)
                if unsplash_results:
                    results.extend(unsplash_results)
            
            if source in ["pexels", "all"] and self.pexels_config.get("key"):
                pexels_results = await self._search_pexels(query)
                if pexels_results:
                    results.extend(pexels_results)
            
            if source in ["pixabay", "all"] and self.pixabay_config.get("key"):
                pixabay_results = await self._search_pixabay(query)
                if pixabay_results:
                    results.extend(pixabay_results)
            
            if not results:
                logger.warning(f"Nenhum resultado encontrado para a busca: {query}")
                return None
            
            # Atualizar estatísticas
            self.stats["search_count"] += 1
            processing_time = time.time() - start_time
            self.stats["last_processing_time"] = processing_time
            self.stats["total_processing_time"] += processing_time
            
            logger.info(f"Busca de imagens concluída: {len(results)} resultados, tempo: {processing_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Erro na busca de imagens: {e}")
            return None
    
    async def _search_unsplash(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca imagens no Unsplash.
        
        Args:
            query: Termo de busca
            
        Returns:
            List: Lista de resultados de imagens
        """
        api_key = self.unsplash_config.get("key")
        if not api_key:
            return []
        
        api_url = "https://api.unsplash.com/search/photos"
        
        params = {
            "query": query,
            "per_page": 10,
            "client_id": api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Erro na API do Unsplash: {response.status}")
                        return []
                    
                    data = await response.json()
                    results = []
                    
                    for item in data.get("results", []):
                        results.append({
                            "id": item.get("id"),
                            "url": item.get("urls", {}).get("regular"),
                            "thumb": item.get("urls", {}).get("thumb"),
                            "description": item.get("description") or item.get("alt_description") or query,
                            "source": "unsplash",
                            "author": item.get("user", {}).get("name"),
                            "author_url": item.get("user", {}).get("links", {}).get("html")
                        })
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Erro ao buscar no Unsplash: {e}")
            return []
    
    async def _search_pexels(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca imagens no Pexels.
        
        Args:
            query: Termo de busca
            
        Returns:
            List: Lista de resultados de imagens
        """
        api_key = self.pexels_config.get("key")
        if not api_key:
            return []
        
        api_url = "https://api.pexels.com/v1/search"
        
        params = {
            "query": query,
            "per_page": 10
        }
        
        headers = {
            "Authorization": api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Erro na API do Pexels: {response.status}")
                        return []
                    
                    data = await response.json()
                    results = []
                    
                    for item in data.get("photos", []):
                        results.append({
                            "id": item.get("id"),
                            "url": item.get("src", {}).get("large"),
                            "thumb": item.get("src", {}).get("medium"),
                            "description": item.get("alt") or query,
                            "source": "pexels",
                            "author": item.get("photographer"),
                            "author_url": item.get("photographer_url")
                        })
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Erro ao buscar no Pexels: {e}")
            return []
    
    async def _search_pixabay(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca imagens no Pixabay.
        
        Args:
            query: Termo de busca
            
        Returns:
            List: Lista de resultados de imagens
        """
        api_key = self.pixabay_config.get("key")
        if not api_key:
            return []
        
        api_url = "https://pixabay.com/api/"
        
        params = {
            "key": api_key,
            "q": query,
            "per_page": 10,
            "image_type": "photo"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Erro na API do Pixabay: {response.status}")
                        return []
                    
                    data = await response.json()
                    results = []
                    
                    for item in data.get("hits", []):
                        results.append({
                            "id": item.get("id"),
                            "url": item.get("largeImageURL"),
                            "thumb": item.get("previewURL"),
                            "description": item.get("tags") or query,
                            "source": "pixabay",
                            "author": item.get("user"),
                            "author_url": f"https://pixabay.com/users/{item.get('user')}-{item.get('user_id')}/"
                        })
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Erro ao buscar no Pixabay: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de uso do gerador de imagens.
        
        Returns:
            Dict: Estatísticas de uso
        """
        return {
            "generation_count": self.stats["generation_count"],
            "search_count": self.stats["search_count"],
            "total_processing_time": self.stats["total_processing_time"],
            "last_processing_time": self.stats["last_processing_time"],
            "errors": self.stats["errors"],
            "apis": {
                "stable_diffusion": bool(self.stable_diffusion_config.get("key")),
                "replicate": bool(self.replicate_config.get("key")),
                "unsplash": bool(self.unsplash_config.get("key")),
                "pexels": bool(self.pexels_config.get("key")),
                "pixabay": bool(self.pixabay_config.get("key"))
            }
        }

# Função para criar uma instância do gerador de imagens
def create_image_generator() -> ImageGenerator:
    """
    Cria uma instância do gerador de imagens.
    
    Returns:
        ImageGenerator: Instância do gerador de imagens
    """
    return ImageGenerator()

# Instância global para uso no bot
image_generator = create_image_generator()
