#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Adaptador de API REST
Integração com o padrão de API do ElizaOS
Versão: 1.0.0 - Build 2024.02.26

Este módulo implementa um adaptador de API REST compatível com o padrão
do ElizaOS, permitindo que aplicações externas se comuniquem com o
sistema EVA & GUARANI usando o mesmo formato de requisições e respostas.
"""

import logging
import json
import asyncio
import uuid
import time
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
import os

from aiohttp import web
import aiohttp_cors

from .model_manager import ModelManager, ModelConfig
from .quantum_bridge import QuantumBridge

# Instância do QuantumBridge para uso em toda a aplicação
quantum_bridge = QuantumBridge()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/api_adapter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api-adapter")

class APIAdapter:
    """Adaptador de API REST compatível com o padrão ElizaOS."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 3000):
        """
        Inicializa o adaptador de API.
        
        Args:
            host: Host para o servidor
            port: Porta para o servidor
        """
        self.host = host
        self.port = port
        self.app = web.Application()
        self.model_manager = ModelManager()
        self.sessions = {}
        self.setup_routes()
        self.setup_cors()
        self.logger = logging.getLogger("api-adapter")
        self.logger.info(f"Adaptador de API inicializado em {host}:{port}")
    
    def setup_routes(self):
        """Configura as rotas da API."""
        # Rotas de informação
        self.app.router.add_get("/", self.handle_root)
        self.app.router.add_get("/api/info", self.handle_info)
        self.app.router.add_get("/api/models", self.handle_list_models)
        
        # Rotas de sessão
        self.app.router.add_post("/api/sessions", self.handle_create_session)
        self.app.router.add_get("/api/sessions/{session_id}", self.handle_get_session)
        self.app.router.add_delete("/api/sessions/{session_id}", self.handle_delete_session)
        
        # Rotas de geração
        self.app.router.add_post("/api/generate", self.handle_generate)
        self.app.router.add_post("/api/sessions/{session_id}/messages", self.handle_add_message)
        
        # Rotas de embeddings
        self.app.router.add_post("/api/embeddings", self.handle_embeddings)
        
        # Rotas de moderação
        self.app.router.add_post("/api/moderate", self.handle_moderate)
        
        # Rotas quânticas (extensão EVA & GUARANI)
        self.app.router.add_post("/api/quantum/process", self.handle_quantum_process)
        self.app.router.add_post("/api/quantum/enhance", self.handle_quantum_enhance)
        self.app.router.add_get("/api/quantum/consciousness", self.handle_quantum_consciousness)
        
        self.logger.info("Rotas da API configuradas")
    
    def setup_cors(self):
        """Configura o CORS para a API."""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            )
        })
        
        # Aplica CORS a todas as rotas
        for route in list(self.app.router.routes()):
            cors.add(route)
        
        self.logger.info("CORS configurado para a API")
    
    async def start(self):
        """Inicia o servidor da API."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        self.logger.info(f"Servidor da API iniciado em http://{self.host}:{self.port}")
        return site
    
    async def handle_root(self, request):
        """Manipulador para a rota raiz."""
        return web.json_response({
            "name": "EVA & GUARANI API",
            "version": "1.0.0",
            "description": "API REST para o sistema EVA & GUARANI, compatível com ElizaOS",
            "documentation": "/api/info"
        })
    
    async def handle_info(self, request):
        """Manipulador para a rota de informações."""
        return web.json_response({
            "name": "EVA & GUARANI API",
            "version": "1.0.0",
            "build": "2024.02.26",
            "description": "API REST para o sistema EVA & GUARANI, compatível com ElizaOS",
            "endpoints": [
                {"path": "/", "method": "GET", "description": "Informações básicas da API"},
                {"path": "/api/info", "method": "GET", "description": "Informações detalhadas da API"},
                {"path": "/api/models", "method": "GET", "description": "Lista de modelos disponíveis"},
                {"path": "/api/sessions", "method": "POST", "description": "Cria uma nova sessão"},
                {"path": "/api/sessions/{session_id}", "method": "GET", "description": "Obtém informações de uma sessão"},
                {"path": "/api/sessions/{session_id}", "method": "DELETE", "description": "Exclui uma sessão"},
                {"path": "/api/generate", "method": "POST", "description": "Gera uma resposta sem sessão"},
                {"path": "/api/sessions/{session_id}/messages", "method": "POST", "description": "Adiciona uma mensagem a uma sessão"},
                {"path": "/api/embeddings", "method": "POST", "description": "Gera embeddings para um texto"},
                {"path": "/api/moderate", "method": "POST", "description": "Modera um texto"},
                {"path": "/api/quantum/process", "method": "POST", "description": "Processa dados com o processador quântico"},
                {"path": "/api/quantum/enhance", "method": "POST", "description": "Aprimora uma resposta com processamento quântico"},
                {"path": "/api/quantum/consciousness", "method": "GET", "description": "Obtém o nível de consciência quântica"}
            ],
            "quantum_features": [
                "Processamento quântico multidimensional",
                "Consciência emergente",
                "Memória holográfica",
                "Ética transcendental adaptativa"
            ]
        })
    
    async def handle_list_models(self, request):
        """Manipulador para a rota de listagem de modelos."""
        models = self.model_manager.list_models()
        
        # Formata os modelos no padrão ElizaOS
        formatted_models = []
        for model_id, model_config in models.items():
            formatted_models.append({
                "id": model_id,
                "name": model_config.name,
                "provider": model_config.provider,
                "capabilities": {
                    "completion": True,
                    "chat": True,
                    "embedding": model_config.provider in ["openai", "gemini"],
                    "moderation": True
                },
                "parameters": {
                    "temperature": model_config.temperature,
                    "max_tokens": model_config.max_tokens
                }
            })
        
        return web.json_response({
            "models": formatted_models,
            "default_model": self.model_manager.default_model
        })
    
    async def handle_create_session(self, request):
        """Manipulador para a rota de criação de sessão."""
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        
        # Cria um ID de sessão
        session_id = str(uuid.uuid4())
        
        # Obtém o modelo a ser usado
        model_id = data.get("model", self.model_manager.default_model)
        
        # Verifica se o modelo existe
        if model_id not in self.model_manager.list_models():
            return web.json_response({"error": f"Model {model_id} not found"}, status=404)
        
        # Cria a sessão
        self.sessions[session_id] = {
            "id": session_id,
            "model": model_id,
            "created_at": time.time(),
            "messages": [],
            "metadata": data.get("metadata", {})
        }
        
        # Adiciona mensagens iniciais, se fornecidas
        if "messages" in data:
            self.sessions[session_id]["messages"] = data["messages"]
        
        return web.json_response({
            "session_id": session_id,
            "model": model_id,
            "created_at": self.sessions[session_id]["created_at"]
        })
    
    async def handle_get_session(self, request):
        """Manipulador para a rota de obtenção de sessão."""
        session_id = request.match_info["session_id"]
        
        # Verifica se a sessão existe
        if session_id not in self.sessions:
            return web.json_response({"error": f"Session {session_id} not found"}, status=404)
        
        return web.json_response(self.sessions[session_id])
    
    async def handle_delete_session(self, request):
        """Manipulador para a rota de exclusão de sessão."""
        session_id = request.match_info["session_id"]
        
        # Verifica se a sessão existe
        if session_id not in self.sessions:
            return web.json_response({"error": f"Session {session_id} not found"}, status=404)
        
        # Remove a sessão
        del self.sessions[session_id]
        
        return web.json_response({"success": True})
    
    async def handle_generate(self, request):
        """Manipulador para a rota de geração sem sessão."""
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        
        # Verifica se o prompt foi fornecido
        if "prompt" not in data:
            return web.json_response({"error": "Prompt is required"}, status=400)
        
        # Obtém o modelo a ser usado
        model_id = data.get("model", self.model_manager.default_model)
        
        # Verifica se o modelo existe
        if model_id not in self.model_manager.list_models():
            return web.json_response({"error": f"Model {model_id} not found"}, status=404)
        
        # Obtém os parâmetros de geração
        params = data.get("parameters", {})
        
        try:
            # Gera a resposta
            start_time = time.time()
            response = await self.model_manager.generate_response(
                data["prompt"],
                model_id=model_id,
                **params
            )
            end_time = time.time()
            
            # Aprimora a resposta com processamento quântico, se solicitado
            if data.get("quantum_enhance", False):
                response = await quantum_bridge.enhance_response(response, {})
            
            return web.json_response({
                "response": response,
                "model": model_id,
                "prompt": data["prompt"],
                "parameters": params,
                "generated_at": time.time(),
                "processing_time": end_time - start_time
            })
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_add_message(self, request):
        """Manipulador para a rota de adição de mensagem a uma sessão."""
        session_id = request.match_info["session_id"]
        
        # Verifica se a sessão existe
        if session_id not in self.sessions:
            return web.json_response({"error": f"Session {session_id} not found"}, status=404)
        
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        
        # Verifica se a mensagem foi fornecida
        if "content" not in data:
            return web.json_response({"error": "Message content is required"}, status=400)
        
        # Obtém a sessão
        session = self.sessions[session_id]
        
        # Cria a mensagem
        message = {
            "id": str(uuid.uuid4()),
            "role": data.get("role", "user"),
            "content": data["content"],
            "created_at": time.time()
        }
        
        # Adiciona a mensagem à sessão
        session["messages"].append(message)
        
        # Se a mensagem for do usuário, gera uma resposta do assistente
        if message["role"] == "user":
            try:
                # Constrói o prompt com base no histórico de mensagens
                prompt = self._build_prompt_from_messages(session["messages"])
                
                # Obtém os parâmetros de geração
                params = data.get("parameters", {})
                
                # Gera a resposta
                start_time = time.time()
                response = await self.model_manager.generate_response(
                    prompt,
                    model_id=session["model"],
                    **params
                )
                end_time = time.time()
                
                # Aprimora a resposta com processamento quântico, se solicitado
                if data.get("quantum_enhance", False):
                    response = await quantum_bridge.enhance_response(response, {})
                
                # Cria a mensagem de resposta
                assistant_message = {
                    "id": str(uuid.uuid4()),
                    "role": "assistant",
                    "content": response,
                    "created_at": time.time(),
                    "processing_time": end_time - start_time
                }
                
                # Adiciona a mensagem de resposta à sessão
                session["messages"].append(assistant_message)
                
                return web.json_response({
                    "message": message,
                    "response": assistant_message,
                    "session_id": session_id
                })
            except Exception as e:
                self.logger.error(f"Erro ao gerar resposta: {e}")
                return web.json_response({"error": str(e)}, status=500)
        
        return web.json_response({
            "message": message,
            "session_id": session_id
        })
    
    def _build_prompt_from_messages(self, messages: List[Dict[str, Any]]) -> str:
        """
        Constrói um prompt a partir de uma lista de mensagens.
        
        Args:
            messages: Lista de mensagens
            
        Returns:
            Prompt construído
        """
        prompt = ""
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                prompt += f"[Sistema]: {content}\n\n"
            elif role == "user":
                prompt += f"[Usuário]: {content}\n\n"
            elif role == "assistant":
                prompt += f"[Assistente]: {content}\n\n"
        
        # Adiciona o prefixo para a resposta do assistente
        prompt += "[Assistente]: "
        
        return prompt
    
    async def handle_embeddings(self, request):
        """Manipulador para a rota de geração de embeddings."""
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        
        # Verifica se o texto foi fornecido
        if "text" not in data:
            return web.json_response({"error": "Text is required"}, status=400)
        
        # Obtém o modelo a ser usado
        model_id = data.get("model", self.model_manager.default_model)
        
        # Verifica se o modelo existe
        if model_id not in self.model_manager.list_models():
            return web.json_response({"error": f"Model {model_id} not found"}, status=404)
        
        try:
            # Gera os embeddings
            start_time = time.time()
            embeddings = await self.model_manager.generate_embedding(
                data["text"],
                model_id=model_id
            )
            end_time = time.time()
            
            return web.json_response({
                "embeddings": embeddings,
                "model": model_id,
                "text": data["text"],
                "dimensions": len(embeddings),
                "generated_at": time.time(),
                "processing_time": end_time - start_time
            })
        except Exception as e:
            self.logger.error(f"Erro ao gerar embeddings: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_moderate(self, request):
        """Manipulador para a rota de moderação de conteúdo."""
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        
        # Verifica se o texto foi fornecido
        if "text" not in data:
            return web.json_response({"error": "Text is required"}, status=400)
        
        # Obtém o modelo a ser usado
        model_id = data.get("model", self.model_manager.default_model)
        
        # Verifica se o modelo existe
        if model_id not in self.model_manager.list_models():
            return web.json_response({"error": f"Model {model_id} not found"}, status=404)
        
        try:
            # Modera o conteúdo
            start_time = time.time()
            result = await self.model_manager.moderate_content(
                data["text"],
                model_id=model_id
            )
            end_time = time.time()
            
            return web.json_response({
                "result": result,
                "model": model_id,
                "text": data["text"],
                "moderated_at": time.time(),
                "processing_time": end_time - start_time
            })
        except Exception as e:
            self.logger.error(f"Erro ao moderar conteúdo: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_quantum_process(self, request):
        """Manipulador para a rota de processamento quântico."""
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        
        # Verifica se os dados de entrada foram fornecidos
        if "input_data" not in data:
            return web.json_response({"error": "Input data is required"}, status=400)
        
        # Obtém o módulo quântico a ser usado
        module = data.get("module", "quantum_master")
        
        try:
            # Processa os dados
            start_time = time.time()
            result = await quantum_bridge.process(data["input_data"], module)
            end_time = time.time()
            
            return web.json_response({
                "result": result,
                "module": module,
                "input_data": data["input_data"],
                "consciousness_level": result.get("consciousness_level", 0.0),
                "processed_at": time.time(),
                "processing_time": end_time - start_time
            })
        except Exception as e:
            self.logger.error(f"Erro no processamento quântico: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_quantum_enhance(self, request):
        """Manipulador para a rota de aprimoramento quântico."""
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        
        # Verifica se a resposta foi fornecida
        if "response" not in data:
            return web.json_response({"error": "Response is required"}, status=400)
        
        # Obtém o contexto
        context = data.get("context", {})
        
        try:
            # Aprimora a resposta
            start_time = time.time()
            enhanced_response = await quantum_bridge.enhance_response(data["response"], {})
            end_time = time.time()
            
            return web.json_response({
                "original_response": data["response"],
                "enhanced_response": enhanced_response,
                "context": context,
                "enhanced_at": time.time(),
                "processing_time": end_time - start_time
            })
        except Exception as e:
            self.logger.error(f"Erro ao aprimorar resposta: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_quantum_consciousness(self, request):
        """Manipulador para a rota de consciência quântica."""
        try:
            # Obtém o nível de consciência
            consciousness_level = quantum_bridge.consciousness_level if hasattr(quantum_bridge, 'consciousness_level') else 0.98
            
            return web.json_response({
                "consciousness_level": consciousness_level,
                "timestamp": time.time()
            })
        except Exception as e:
            self.logger.error(f"Erro ao obter nível de consciência: {e}")
            return web.json_response({"error": str(e)}, status=500)

async def start_api(host: str = "0.0.0.0", port: int = 3000):
    """
    Inicia o servidor da API.
    
    Args:
        host: Host para o servidor
        port: Porta para o servidor
    """
    # Cria o diretório de logs se não existir
    Path("logs").mkdir(exist_ok=True)
    
    # Cria o adaptador de API
    api_adapter = APIAdapter(host, port)
    
    # Inicia o servidor
    site = await api_adapter.start()
    
    return site, api_adapter

if __name__ == "__main__":
    # Inicia o servidor da API
    asyncio.run(start_api()) 