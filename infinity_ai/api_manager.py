import logging
import aiohttp
import json
from typing import Dict, Optional, List, Any
from datetime import datetime
from config.api_config import api_config

logger = logging.getLogger(__name__)

class APIManager:
    def __init__(self):
        self.config = api_config
        self.session = None
        self.setup_logging()

    def setup_logging(self):
        """Configura o logging para o gerenciador de APIs"""
        handler = logging.FileHandler("logs/api_manager.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    async def initialize(self):
        """Inicializa a sessão HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Fecha a sessão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None

    async def call_openrouter(self, prompt: str, context: Dict = None) -> Dict:
        """Faz uma chamada para a OpenRouter API"""
        try:
            config = self.config.get_config("openrouter")
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            }

            data = {
                "model": config["default_model"],
                "messages": [
                    {"role": "system", "content": context.get("system_prompt", "")},
                    {"role": "user", "content": prompt}
                ]
            }

            async with self.session.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                return await response.json()

        except Exception as e:
            logger.error(f"Erro na chamada OpenRouter: {str(e)}")
            return {"error": str(e)}

    async def call_perplexity(self, prompt: str, context: Dict = None) -> Dict:
        """Faz uma chamada para a Perplexity API"""
        try:
            config = self.config.get_config("perplexity")
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            }

            data = {
                "model": config["default_model"],
                "messages": [
                    {"role": "system", "content": context.get("system_prompt", "")},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": config["max_tokens"],
                "temperature": config["temperature"]
            }

            async with self.session.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                return await response.json()

        except Exception as e:
            logger.error(f"Erro na chamada Perplexity: {str(e)}")
            return {"error": str(e)}

    async def call_openai(self, prompt: str, context: Dict = None) -> Dict:
        """Faz uma chamada para a OpenAI API"""
        try:
            config = self.config.get_config("openai")
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
                "OpenAI-Organization": config["organization"]
            }

            data = {
                "model": config["default_model"],
                "messages": [
                    {"role": "system", "content": context.get("system_prompt", "")},
                    {"role": "user", "content": prompt}
                ]
            }

            async with self.session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                return await response.json()

        except Exception as e:
            logger.error(f"Erro na chamada OpenAI: {str(e)}")
            return {"error": str(e)}

    async def call_cohere(self, prompt: str, context: Dict = None) -> Dict:
        """Faz uma chamada para a Cohere API"""
        try:
            config = self.config.get_config("cohere")
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            }

            data = {
                "model": config["default_model"],
                "prompt": prompt,
                "max_tokens": config["max_tokens"]
            }

            async with self.session.post(
                "https://api.cohere.ai/v1/generate",
                headers=headers,
                json=data
            ) as response:
                return await response.json()

        except Exception as e:
            logger.error(f"Erro na chamada Cohere: {str(e)}")
            return {"error": str(e)}

    async def process_with_fallback(self, prompt: str, context: Dict = None) -> Dict:
        """Processa uma requisição com fallback entre diferentes APIs"""
        apis = ["openrouter", "perplexity", "openai", "cohere"]
        
        for api_name in apis:
            try:
                if not self.config.get_api_key(api_name):
                    continue

                method = getattr(self, f"call_{api_name}")
                response = await method(prompt, context)

                if "error" not in response:
                    return {
                        "success": True,
                        "api_used": api_name,
                        "response": response
                    }

            except Exception as e:
                logger.error(f"Erro no fallback para {api_name}: {str(e)}")
                continue

        return {
            "success": False,
            "error": "Todas as APIs falharam",
            "apis_tried": apis
        }

# Instância global do gerenciador de APIs
api_manager = APIManager() 