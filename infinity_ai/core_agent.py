from typing import Dict, List, Optional
import openai
from redis import Redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import json
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("infinity-ai")

class Message(BaseModel):
    role: str
    content: str
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['system', 'user', 'assistant']:
            raise ValueError('Role must be system, user, or assistant')
        return v
    
class Conversation(BaseModel):
    messages: List[Message]
    channel: str
    user_id: str
    
    @validator('channel')
    def validate_channel(cls, v):
        valid_channels = ['whatsapp', 'telegram', 'instagram']
        if v not in valid_channels:
            raise ValueError(f'Channel must be one of: {valid_channels}')
        return v

class InfinityAgent:
    def __init__(self):
        self.openai = openai
        self.openai.api_key = os.getenv("OPENAI_API_KEY")
        self.redis = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD", "")
        )
        self.system_prompt = """Você é o assistente da INFINITY, uma marca de roupas que une arte ASCII, tecnologia e moda.
        
Principais características:
- Atendimento personalizado e acolhedor
- Conhecimento profundo dos produtos
- Capacidade de personalização em tempo real
- Foco em experiência do cliente

Produtos:
1. T-Shirts com arte ASCII (R$ 89,90)
2. Hoodies Tech Style (R$ 199,90)
3. Edições Especiais Code (R$ 299,90)

Cada peça tem um QR Code único que leva a experiências AR exclusivas.

Mantenha um tom:
- Amigável mas profissional
- Tecnológico mas acessível
- Artístico e inspirador

Use arte ASCII quando apropriado para ilustrar a conversa."""

        # Inicializa métricas
        self.initialize_metrics()

    def initialize_metrics(self):
        """Inicializa ou reseta métricas no Redis"""
        metrics_key = "infinity_metrics"
        default_metrics = {
            "total_conversations": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "average_response_time": 0,
            "channel_stats": {
                "whatsapp": {"count": 0, "success_rate": 100},
                "telegram": {"count": 0, "success_rate": 100},
                "instagram": {"count": 0, "success_rate": 100}
            },
            "last_updated": datetime.now().isoformat()
        }
        if not self.redis.exists(metrics_key):
            self.redis.set(metrics_key, json.dumps(default_metrics))

    def update_metrics(self, channel: str, success: bool, response_time: float):
        """Atualiza métricas de performance"""
        metrics_key = "infinity_metrics"
        metrics = json.loads(self.redis.get(metrics_key))
        
        # Atualiza estatísticas gerais
        metrics["total_conversations"] += 1
        if success:
            metrics["successful_responses"] += 1
        else:
            metrics["failed_responses"] += 1
            
        # Atualiza média de tempo de resposta
        current_avg = metrics["average_response_time"]
        total_conv = metrics["total_conversations"]
        metrics["average_response_time"] = (current_avg * (total_conv - 1) + response_time) / total_conv
        
        # Atualiza estatísticas do canal
        metrics["channel_stats"][channel]["count"] += 1
        success_rate = metrics["channel_stats"][channel]["success_rate"]
        new_rate = ((success_rate * (metrics["channel_stats"][channel]["count"] - 1)) + (100 if success else 0)) / metrics["channel_stats"][channel]["count"]
        metrics["channel_stats"][channel]["success_rate"] = new_rate
        
        metrics["last_updated"] = datetime.now().isoformat()
        
        self.redis.set(metrics_key, json.dumps(metrics))

    async def process_message(self, conversation: Conversation) -> str:
        start_time = datetime.now()
        success = False
        try:
            # Recupera histórico do Redis
            history_key = f"chat_history:{conversation.channel}:{conversation.user_id}"
            stored_history = self.redis.get(history_key)
            
            messages = []
            if stored_history:
                messages = json.loads(stored_history)
            
            # Adiciona o system prompt
            messages = [{"role": "system", "content": self.system_prompt}] + messages
            
            # Adiciona a nova mensagem
            for msg in conversation.messages:
                messages.append({"role": msg.role, "content": msg.content})
                
            # Gera resposta com GPT-4
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Atualiza histórico no Redis
            messages_to_store = messages[1:] + [{"role": "assistant", "content": assistant_message}]
            self.redis.setex(
                history_key,
                3600,  # 1 hora de expiração
                json.dumps(messages_to_store)
            )
            
            success = True
            return assistant_message
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # Atualiza métricas
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            self.update_metrics(conversation.channel, success, response_time)
    
    def clear_history(self, channel: str, user_id: str) -> bool:
        history_key = f"chat_history:{channel}:{user_id}"
        return self.redis.delete(history_key) > 0

    def get_metrics(self) -> Dict:
        """Retorna métricas atuais do sistema"""
        metrics_key = "infinity_metrics"
        return json.loads(self.redis.get(metrics_key))

# Instancia o FastAPI app
app = FastAPI(title="Infinity AI Core")
agent = InfinityAgent()

@app.post("/chat")
async def chat(conversation: Conversation):
    response = await agent.process_message(conversation)
    return {"response": response}

@app.delete("/history/{channel}/{user_id}")
async def clear_history(channel: str, user_id: str):
    success = agent.clear_history(channel, user_id)
    return {"success": success}

@app.get("/metrics")
async def get_metrics():
    return agent.get_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 