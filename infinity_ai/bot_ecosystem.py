import logging
from typing import Dict, List, Optional
import json
from datetime import datetime
from .ava_memory import AVAMemory, Memory
from .ava_consciousness import AVAConsciousness
from .ava_ethics_shield import EthicsShield
from .openrouter_manager import OpenRouterManager
from .bot_personalities import get_bot_personality, get_all_personalities

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot_ecosystem.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BotEcosystem')

class BotAgent:
    def __init__(
        self,
        bot_id: str,
        memory: AVAMemory,
        consciousness: AVAConsciousness,
        ethics: EthicsShield
    ):
        self.bot_id = bot_id
        self.personality = get_bot_personality(bot_id)
        self.memory = memory
        self.consciousness = consciousness
        self.ethics = ethics
        self.router = OpenRouterManager()
        self.shared_knowledge = {}
        self.interaction_count = 0
        self.success_rate = 1.0
        
    async def process_interaction(self, text: str, context: Dict) -> Dict:
        """Processa uma interação aplicando a personalidade do bot"""
        try:
            # Validação ética
            if not await self.ethics.validate_message(text, context):
                return {
                    "success": False,
                    "message": "Interação bloqueada por questões éticas"
                }
                
            # Aplica personalidade ao contexto
            enriched_context = self._enrich_context(context)
            
            # Processa com OpenRouter
            response = await self.router.process_message(
                text,
                context=enriched_context
            )
            
            # Atualiza experiência
            self._update_experience(text, response)
            
            # Compartilha conhecimento
            await self._share_knowledge(text, response, enriched_context)
            
            # Formata resposta com personalidade
            formatted_response = self._format_response(response.text)
            
            return {
                "success": True,
                "response": formatted_response,
                "personality_influence": self._get_personality_influence(),
                "experience_gained": self._calculate_experience(text, response)
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar interação: {str(e)}")
            self.success_rate *= 0.95  # Reduz taxa de sucesso
            return {"success": False, "error": str(e)}
            
    def _enrich_context(self, context: Dict) -> Dict:
        """Enriquece o contexto com a personalidade do bot"""
        return {
            **context,
            "bot_personality": self.personality.to_dict(),
            "interaction_style": self._get_interaction_style(),
            "expertise_areas": self._get_expertise_areas(),
            "shared_knowledge": self.shared_knowledge
        }
        
    def _get_interaction_style(self) -> Dict[str, float]:
        """Define o estilo de interação baseado na personalidade"""
        return {
            "formality": self.personality.attributes.get("formality", 0.5),
            "empathy": self.personality.attributes.get("empathy", 0.5),
            "creativity": self.personality.attributes.get("creativity", 0.5),
            "technical_depth": self.personality.attributes.get("technical_depth", 0.5)
        }
        
    def _get_expertise_areas(self) -> List[Dict]:
        """Lista áreas de expertise do bot"""
        return [
            {
                "area": skill,
                "level": self.personality.level,
                "confidence": self._calculate_confidence(skill)
            }
            for skill in self.personality.bot_class.skills
        ]
        
    def _calculate_confidence(self, skill: str) -> float:
        """Calcula nível de confiança em uma habilidade"""
        base_confidence = 0.5
        experience_bonus = min(0.3, self.personality.experience / 1000)
        success_bonus = 0.2 * self.success_rate
        
        # Bônus por especialização
        if skill in self.personality.bot_class.skills:
            base_confidence += 0.2
            
        return min(0.95, base_confidence + experience_bonus + success_bonus)
        
    def _update_experience(self, input_text: str, response: Dict):
        """Atualiza experiência do bot"""
        exp_gained = self._calculate_experience(input_text, response)
        self.personality.experience += exp_gained
        
        # Level up se necessário
        while self.personality.experience >= self._next_level_exp():
            self.personality.level += 1
            logger.info(f"Bot {self.bot_id} alcançou nível {self.personality.level}!")
            
            # Registra evolução na memória
            self._log_evolution()
            
    def _calculate_experience(self, input_text: str, response: Dict) -> int:
        """Calcula experiência ganha em uma interação"""
        base_exp = 10
        
        # Bônus por complexidade
        complexity_bonus = len(input_text.split()) * 0.1
        
        # Bônus por sucesso
        success_bonus = 5 if response.get("success", False) else 0
        
        # Bônus por especialização
        spec_bonus = sum(
            5 for skill in self.personality.bot_class.skills
            if skill.lower() in input_text.lower()
        )
        
        return int(base_exp + complexity_bonus + success_bonus + spec_bonus)
        
    def _next_level_exp(self) -> int:
        """Calcula experiência necessária para próximo nível"""
        return self.personality.level * 100
        
    async def _share_knowledge(self, input_text: str, response: Dict, context: Dict):
        """Compartilha conhecimento com outros bots"""
        if response.get("success", False):
            knowledge = {
                "timestamp": datetime.now().isoformat(),
                "input": input_text,
                "response": response,
                "context": context,
                "bot_id": self.bot_id,
                "personality": self.personality.to_dict(),
                "success_rate": self.success_rate
            }
            
            # Armazena localmente
            self.shared_knowledge[datetime.now().isoformat()] = knowledge
            
            # Armazena na memória compartilhada
            await self.memory.store(
                Memory(
                    content=json.dumps(knowledge),
                    context={"type": "shared_knowledge"}
                )
            )
            
    def _format_response(self, text: str) -> str:
        """Formata a resposta de acordo com a personalidade do bot"""
        # Adiciona quirk aleatório
        if self.personality.quirks and len(self.personality.quirks) > 0:
            from random import choice
            text = f"{text}\n\n_{choice(self.personality.quirks)}_"
            
        return text
            
    def _get_personality_influence(self) -> Dict[str, float]:
        """Calcula influência da personalidade nas respostas"""
        return {
            attr: value * (self.personality.level / 10)
            for attr, value in self.personality.attributes.items()
        }
        
    async def _log_evolution(self):
        """Registra evolução do bot na memória"""
        evolution_data = {
            "timestamp": datetime.now().isoformat(),
            "bot_id": self.bot_id,
            "new_level": self.personality.level,
            "total_experience": self.personality.experience,
            "attributes": self.personality.attributes,
            "success_rate": self.success_rate
        }
        
        await self.memory.store(
            Memory(
                content=json.dumps(evolution_data),
                context={"type": "bot_evolution"}
            )
        )

class BotEcosystem:
    def __init__(self):
        self.bots: Dict[str, BotAgent] = {}
        self.shared_memory = AVAMemory()
        
        # Inicializa bots com personalidades distintas
        self._initialize_bots()
        
    def _initialize_bots(self):
        """Inicializa os bots do ecossistema"""
        personalities = get_all_personalities()
        
        for bot_id, personality in personalities.items():
            self.bots[bot_id] = BotAgent(
                bot_id=bot_id,
                memory=AVAMemory() if bot_id != "@Avatechartbot" else self.shared_memory,
                consciousness=AVAConsciousness(self.shared_memory),
                ethics=EthicsShield(self.shared_memory, None)
            )
        
    async def process_message(self, bot_id: str, text: str, context: Dict) -> Dict:
        """Processa mensagem através do bot apropriado"""
        if bot_id not in self.bots:
            raise ValueError(f"Bot {bot_id} não encontrado")
            
        bot = self.bots[bot_id]
        return await bot.process_interaction(text, context)
        
    async def share_experience(self, source_bot_id: str, target_bot_id: str):
        """Compartilha experiência entre bots"""
        if source_bot_id not in self.bots or target_bot_id not in self.bots:
            raise ValueError("Bot não encontrado")
            
        source = self.bots[source_bot_id]
        target = self.bots[target_bot_id]
        
        # Transfere conhecimento
        shared_exp = int(source.personality.experience * 0.1)  # 10% da experiência
        target.personality.experience += shared_exp
        
        # Compartilha habilidades
        for skill in source.personality.bot_class.skills:
            if skill not in target.personality.bot_class.skills:
                target.personality.bot_class.skills.append(skill)
                
        logger.info(f"Experiência compartilhada: {shared_exp} de {source_bot_id} para {target_bot_id}")
        
    async def get_bot_status(self, bot_id: str) -> Dict:
        """Retorna status detalhado de um bot"""
        if bot_id not in self.bots:
            raise ValueError(f"Bot {bot_id} não encontrado")
            
        bot = self.bots[bot_id]
        return {
            "personality": bot.personality.to_dict(),
            "interaction_count": bot.interaction_count,
            "success_rate": bot.success_rate,
            "shared_knowledge_count": len(bot.shared_knowledge),
            "active_specializations": bot._get_expertise_areas()
        }
        
    async def update_bot_personality(self, bot_id: str, attributes: Dict[str, float]):
        """Atualiza atributos da personalidade de um bot"""
        if bot_id not in self.bots:
            raise ValueError(f"Bot {bot_id} não encontrado")
            
        bot = self.bots[bot_id]
        bot.personality.attributes.update(attributes)
        logger.info(f"Personalidade atualizada para {bot_id}: {attributes}")
        
    async def get_ecosystem_stats(self) -> Dict:
        """Retorna estatísticas gerais do ecossistema"""
        total_interactions = sum(bot.interaction_count for bot in self.bots.values())
        total_knowledge = sum(len(bot.shared_knowledge) for bot in self.bots.values())
        avg_success_rate = sum(bot.success_rate for bot in self.bots.values()) / len(self.bots)
        
        return {
            "total_bots": len(self.bots),
            "total_interactions": total_interactions,
            "total_shared_knowledge": total_knowledge,
            "average_success_rate": avg_success_rate,
            "bots": {
                bot_id: {
                    "level": bot.personality.level,
                    "experience": bot.personality.experience,
                    "success_rate": bot.success_rate
                }
                for bot_id, bot in self.bots.items()
            }
        } 