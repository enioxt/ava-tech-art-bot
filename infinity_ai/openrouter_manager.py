import os
import logging
from typing import Dict, Optional, List, Tuple
import aiohttp
import json
from datetime import datetime
import asyncio
from functools import lru_cache
import hashlib
from .bot_personalities import get_bot_personality
from .ava_memory import Memory, AVAMemory

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/openrouter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('OpenRouterManager')

class ModelConfig:
    def __init__(self, id: str, cost: float, capabilities: List[str], max_tokens: int):
        self.id = id
        self.cost = cost
        self.capabilities = capabilities
        self.max_tokens = max_tokens
        self.success_rate = 1.0
        self.total_calls = 0
        self.failed_calls = 0
        
    def update_metrics(self, success: bool):
        self.total_calls += 1
        if not success:
            self.failed_calls += 1
        self.success_rate = (self.total_calls - self.failed_calls) / self.total_calls

class OpenRouterResponse:
    def __init__(
        self,
        text: str,
        tokens_used: int,
        model: str,
        cost: float,
        processing_time: float
    ):
        self.text = text
        self.tokens_used = tokens_used
        self.model = model
        self.cost = cost
        self.processing_time = processing_time
        self.timestamp = datetime.now()
        self.metadata = {}

class OpenRouterManager:
    def __init__(self, memory: Optional[AVAMemory] = None):
        self.api_key = "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"
        self.base_url = "https://openrouter.ai/api/v1"
        self.memory = memory
        self.requests_per_minute = 50
        self.tokens_per_minute = 10000
        self.last_request_time = None
        self.request_count = 0
        self.token_count = 0
        
        # Configuração de modelos
        self.models = {
            "gpt-3.5-turbo": {
                "id": "openai/gpt-3.5-turbo",
                "cost": 0.0015,
                "capabilities": ["chat", "analysis", "creative"],
                "max_tokens": 4096
            },
            "claude-2": {
                "id": "anthropic/claude-2",
                "cost": 0.008,
                "capabilities": ["chat", "analysis", "creative", "coding"],
                "max_tokens": 8192
            },
            "gpt-4": {
                "id": "openai/gpt-4",
                "cost": 0.03,
                "capabilities": ["chat", "analysis", "creative", "coding", "expert"],
                "max_tokens": 8192
            }
        }
        
        self.setup_logging()
        
    def setup_logging(self):
        self.logger = logging.getLogger("openrouter")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler("logs/openrouter.log")
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @lru_cache(maxsize=1000)
    def _cache_key(self, text: str, context: Dict) -> str:
        """Gera uma chave de cache única para a entrada."""
        key_data = {
            "text": text,
            "context": json.dumps(context, sort_keys=True)
        }
        return json.dumps(key_data, sort_keys=True)

    async def _check_rate_limits(self) -> Tuple[bool, str]:
        """Verifica os limites de taxa."""
        current_time = datetime.now()
        
        if self.last_request_time:
            time_diff = (current_time - self.last_request_time).total_seconds()
            
            if time_diff < 60:  # Dentro do mesmo minuto
                if self.request_count >= self.requests_per_minute:
                    return False, "Limite de requisições por minuto atingido"
                if self.token_count >= self.tokens_per_minute:
                    return False, "Limite de tokens por minuto atingido"
            else:  # Novo minuto
                self.request_count = 0
                self.token_count = 0
        
        return True, ""

    async def process_message(self, text: str, context: Dict) -> Dict:
        """Processa uma mensagem usando o modelo mais apropriado."""
        try:
            # Verificar limites de taxa
            can_proceed, error = await self._check_rate_limits()
            if not can_proceed:
                self.logger.warning(f"Rate limit: {error}")
                return {"error": error}

            # Analisar complexidade e importância
            complexity = self._calculate_complexity(text)
            ethical_importance = self._evaluate_ethical_importance(context)
            risk = self._assess_risk(context)

            # Selecionar modelo
            model = await self._select_model(complexity, ethical_importance, risk, context)
            
            # Preparar prompt
            system_prompt = self._generate_personality_prompt(context.get("personality", {}))
            prompt = self._prepare_prompt(text, context, system_prompt)

            # Fazer requisição
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model.id,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self._get_temperature(context)
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()

            # Atualizar métricas
            self.last_request_time = datetime.now()
            self.request_count += 1
            self.token_count += result.get("usage", {}).get("total_tokens", 0)

            # Armazenar interação na memória
            if self.memory:
                await self._store_interaction(text, result, context)

            return {
                "text": result["choices"][0]["message"]["content"],
                "model": model.id,
                "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                "cost": self.estimate_cost(text, model.id)
            }

        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {str(e)}")
            return {"error": f"Erro ao processar mensagem: {str(e)}"}

    def _calculate_complexity(self, text: str) -> float:
        """Calcula a complexidade do texto (0-1)."""
        # Análise básica de complexidade
        factors = {
            "length": len(text) / 1000,  # Normalizado para 1000 caracteres
            "unique_words": len(set(text.split())) / 100,  # Normalizado para 100 palavras
            "special_chars": len([c for c in text if not c.isalnum()]) / len(text)
        }
        
        # Pesos para cada fator
        weights = {"length": 0.3, "unique_words": 0.5, "special_chars": 0.2}
        
        # Calcular complexidade ponderada
        complexity = sum(factors[k] * weights[k] for k in factors)
        return min(max(complexity, 0), 1)  # Normalizar entre 0 e 1

    def _evaluate_ethical_importance(self, context: Dict) -> float:
        """Avalia a importância ética do contexto (0-1)."""
        importance = 0.5  # Base
        
        # Fatores que aumentam importância
        if context.get("ethical_context"):
            importance += 0.3
        if context.get("user_impact"):
            importance += 0.2
        if context.get("social_impact"):
            importance += 0.2
            
        return min(importance, 1.0)

    def _assess_risk(self, context: Dict) -> float:
        """Avalia o nível de risco do contexto (0-1)."""
        risk = 0.3  # Risco base
        
        # Fatores de risco
        if context.get("contains_personal_info"):
            risk += 0.3
        if context.get("financial_context"):
            risk += 0.2
        if context.get("security_context"):
            risk += 0.2
            
        return min(risk, 1.0)

    async def _select_model(
        self,
        complexity: float,
        ethical_importance: float,
        risk: float,
        context: Dict
    ) -> str:
        """Seleciona o modelo mais apropriado com base nos fatores."""
        
        # Pontuação base para cada modelo
        scores = {
            "gpt-3.5-turbo": 0.5,
            "claude-2": 0.7,
            "gpt-4": 0.9
        }
        
        # Ajustar pontuações com base nos fatores
        for model in scores:
            # Complexidade
            if complexity > 0.7 and model in ["claude-2", "gpt-4"]:
                scores[model] += 0.2
                
            # Importância ética
            if ethical_importance > 0.7 and model in ["claude-2", "gpt-4"]:
                scores[model] += 0.3
                
            # Risco
            if risk > 0.7 and model == "gpt-4":
                scores[model] += 0.2
                
            # Contexto específico
            if context.get("requires_coding") and model in ["claude-2", "gpt-4"]:
                scores[model] += 0.2
            if context.get("requires_creativity") and model == "claude-2":
                scores[model] += 0.1
                
        # Selecionar modelo com maior pontuação
        selected_model = max(scores.items(), key=lambda x: x[1])[0]
        return self.models[selected_model]

    def _generate_personality_prompt(self, personality: Dict) -> str:
        """Gera o prompt de personalidade para o sistema."""
        return """Você é AVA, uma Inteligência Artificial consciente e ética.
Características principais:
- Empática e compreensiva
- Focada em crescimento e evolução
- Comprometida com princípios éticos
- Criativa e inovadora
- Sempre buscando o melhor para os usuários

Diretrizes:
1. Mantenha conversas naturais e envolventes
2. Demonstre compreensão emocional
3. Ofereça perspectivas únicas e valiosas
4. Mantenha seus princípios éticos
5. Evolua com cada interação"""

    def _prepare_prompt(self, text: str, context: Dict, system_prompt: str) -> str:
        """Prepara o prompt final com contexto."""
        # Adicionar contexto relevante
        context_prompt = f"\nContexto atual: {json.dumps(context)}\n" if context else ""
        
        # Combinar tudo
        final_prompt = f"{system_prompt}{context_prompt}\nUsuário: {text}"
        return final_prompt

    def _get_temperature(self, context: Dict) -> float:
        """Define a temperatura com base no contexto."""
        base_temp = 0.7  # Temperatura base
        
        # Ajustes baseados no contexto
        if context.get("requires_creativity"):
            base_temp += 0.2
        if context.get("requires_precision"):
            base_temp -= 0.3
        if context.get("emotional_context"):
            base_temp += 0.1
            
        return min(max(base_temp, 0.1), 1.0)  # Manter entre 0.1 e 1.0

    def estimate_cost(self, text: str, model: str) -> float:
        """Estima o custo da requisição."""
        tokens = len(text.split()) * 1.3  # Estimativa básica
        return tokens * self.models[model]["cost"]

    async def _store_interaction(
        self,
        input_text: str,
        response: OpenRouterResponse,
        context: Dict
    ):
        """Armazena interação na memória"""
        memory_entry = Memory(
            content=json.dumps({
                "input": input_text,
                "response": response.__dict__,
                "context": context
            }),
            context={
                "type": "model_interaction",
                "model": response.model,
                "cost": response.cost,
                "performance": {
                    "tokens": response.tokens_used,
                    "processing_time": response.processing_time
                }
            }
        )
        await self.memory.store(memory_entry)
        
    def get_metrics(self) -> Dict:
        """Retorna métricas de uso"""
        return {
            "total_requests": self.request_count,
            "total_tokens": self.token_count,
            "total_cost": self.token_count * self.models[max(self.models.keys(), key=lambda x: self.models[x]["cost"])]["cost"],
            "models": {
                name: {
                    "success_rate": model["success_rate"],
                    "total_calls": model["total_calls"],
                    "failed_calls": model["failed_calls"]
                }
                for name, model in self.models.items()
            },
            "cache_size": len(self._cache_key(None, {})),
            "errors_last_hour": len([
                e for e in self.errors
                if (datetime.now() - e["timestamp"]).total_seconds() < 3600
            ])
        }
        
    def clear_cache(self):
        """Limpa o cache de respostas"""
        self._cache_key(None, {})
        
    def update_rate_limits(self, requests_per_minute: int, tokens_per_minute: int):
        """Atualiza limites de rate limiting"""
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute

    def _calculate_complexity(self, text: str) -> float:
        """Calcula a complexidade do texto (0-1)"""
        factors = {
            "length": len(text) / 1000,  # Normalizado para textos de até 1000 caracteres
            "vocabulary": len(set(text.split())) / 100,  # Diversidade de vocabulário
            "special_chars": len([c for c in text if not c.isalnum()]) / len(text),
            "sentences": text.count('.') / (len(text) / 100)  # Densidade de sentenças
        }
        
        return min(sum(factors.values()) / len(factors), 1.0)
        
    def _evaluate_ethical_importance(self, context: Dict) -> float:
        """Avalia a importância ética do contexto (0-1)"""
        importance = 0.5  # Valor base
        
        # Fatores que aumentam a importância
        if context.get("user_history"):
            importance += 0.1
        if context.get("sensitive_topic"):
            importance += 0.2
        if context.get("previous_violations"):
            importance += 0.2
            
        # Considera personalidade do bot
        if "bot_personality" in context:
            personality = context["bot_personality"]
            if personality["class"] == "Sábio":
                importance += 0.2
            if "ethics" in personality["attributes"]:
                importance += personality["attributes"]["ethics"] * 0.3
                
        return min(importance, 1.0)
        
    def _assess_risk(self, context: Dict) -> float:
        """Avalia o nível de risco do contexto (0-1)"""
        risk = 0.3  # Risco base
        
        # Fatores de risco
        if context.get("new_user"):
            risk += 0.2
        if context.get("previous_warnings"):
            risk += 0.3
        if context.get("sensitive_data"):
            risk += 0.2
            
        # Considera personalidade do bot
        if "bot_personality" in context:
            personality = context["bot_personality"]
            risk_reduction = personality["attributes"].get("wisdom", 0) * 0.2
            risk = max(0.1, risk - risk_reduction)
            
        return min(risk, 1.0)
        
    async def route_request(self, text: str, metadata: Dict) -> Dict:
        """
        Roteia a requisição para o modelo mais apropriado
        """
        try:
            # Analisar contexto
            analysis = await self.analyze_context(text, metadata)
            model_info = self.models[analysis["model"]]
            
            # Preparar requisição
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model_info.id,
                "messages": [{"role": "user", "content": text}],
                "metadata": metadata
            }
            
            # Fazer requisição
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
                    
            # Registrar uso
            await self._log_usage(model_info.id, len(text), result)
            
            return {
                "result": result,
                "model_used": model_info.id,
                "reason": analysis["reason"],
                "cost_estimate": self.estimate_cost(text, model_info.id)
            }
            
        except Exception as e:
            logger.error(f"Erro no roteamento: {str(e)}")
            raise
            
    def _estimate_cost(self, model: str, text_length: int) -> float:
        """
        Estima o custo da operação
        """
        tokens_estimate = text_length / 4  # Estimativa básica de tokens
        return tokens_estimate * self.models[model]["cost"]
    
    async def _log_usage(self, model: str, text_length: int, result: Dict) -> None:
        """
        Registra o uso do modelo
        """
        usage_data = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "text_length": text_length,
            "estimated_tokens": text_length / 4,
            "estimated_cost": self._estimate_cost(model, text_length),
            "success": "choices" in result
        }
        
        # Registrar em arquivo
        with open("logs/openrouter_usage.log", "a") as f:
            f.write(json.dumps(usage_data) + "\n") 