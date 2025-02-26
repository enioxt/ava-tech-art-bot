from typing import Dict, List, Optional
import json
from datetime import datetime
import random
import math

class Attribute:
    def __init__(self, name: str, base_value: float, growth_rate: float = 0.1):
        self.name = name
        self.base_value = base_value
        self.current_value = base_value
        self.growth_rate = growth_rate
        self.experience = 0
        
    def gain_experience(self, amount: float):
        """Ganha experiência e possivelmente aumenta o valor"""
        self.experience += amount
        if self.experience >= 1.0:
            self.level_up()
            
    def level_up(self):
        """Aumenta o valor do atributo"""
        growth = self.growth_rate * (1 - self.current_value)  # Crescimento diminui conforme valor aumenta
        self.current_value = min(1.0, self.current_value + growth)
        self.experience = 0
        
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.current_value,
            "experience": self.experience,
            "growth_rate": self.growth_rate
        }

class Skill:
    def __init__(
        self,
        name: str,
        description: str,
        base_level: int = 1,
        max_level: int = 10,
        attributes: List[str] = None
    ):
        self.name = name
        self.description = description
        self.level = base_level
        self.max_level = max_level
        self.experience = 0
        self.attributes = attributes or []
        self.usage_count = 0
        self.success_rate = 1.0
        
    def use(self, success: bool = True):
        """Registra uso da habilidade"""
        self.usage_count += 1
        if success:
            self.gain_experience(0.1)
        else:
            self.success_rate = (self.usage_count - 1) * self.success_rate / self.usage_count
            
    def gain_experience(self, amount: float):
        """Ganha experiência e possivelmente sobe de nível"""
        self.experience += amount
        if self.experience >= self._next_level_exp():
            self.level_up()
            
    def level_up(self):
        """Aumenta o nível da habilidade"""
        if self.level < self.max_level:
            self.level += 1
            self.experience = 0
            
    def _next_level_exp(self) -> float:
        """Calcula experiência necessária para próximo nível"""
        return math.pow(1.5, self.level)
        
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "experience": self.experience,
            "attributes": self.attributes,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate
        }

class SpecialAbility:
    def __init__(
        self,
        name: str,
        description: str,
        cooldown: int = 0,
        requirements: Dict[str, float] = None
    ):
        self.name = name
        self.description = description
        self.cooldown = cooldown
        self.requirements = requirements or {}
        self.last_used = None
        self.times_used = 0
        
    def can_use(self, attributes: Dict[str, float]) -> bool:
        """Verifica se a habilidade pode ser usada"""
        if self.last_used and (datetime.now() - self.last_used).total_seconds() < self.cooldown:
            return False
            
        return all(
            attributes.get(attr, 0) >= value
            for attr, value in self.requirements.items()
        )
        
    def use(self):
        """Registra uso da habilidade"""
        self.last_used = datetime.now()
        self.times_used += 1
        
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "cooldown": self.cooldown,
            "requirements": self.requirements,
            "times_used": self.times_used
        }

class BotClass:
    def __init__(
        self,
        name: str,
        description: str,
        attributes: Dict[str, float],
        skills: List[Dict],
        special_abilities: List[Dict]
    ):
        self.name = name
        self.description = description
        self.attributes = {
            name: Attribute(name, value)
            for name, value in attributes.items()
        }
        self.skills = [
            Skill(**skill_data)
            for skill_data in skills
        ]
        self.special_abilities = [
            SpecialAbility(**ability_data)
            for ability_data in special_abilities
        ]
        
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "attributes": {
                name: attr.to_dict()
                for name, attr in self.attributes.items()
            },
            "skills": [
                skill.to_dict()
                for skill in self.skills
            ],
            "special_abilities": [
                ability.to_dict()
                for ability in self.special_abilities
            ]
        }

# Classes dos Bots (inspirado em D&D e RPGs modernos)
BOT_CLASSES = {
    "Artista": BotClass(
        name="Artista",
        description="""
        Mestres da manipulação visual e criação artística. 
        Combinam precisão técnica com sensibilidade estética.
        """,
        attributes={
            "creativity": 0.8,
            "precision": 0.9,
            "intuition": 0.7,
            "technical_mastery": 0.85,
            "aesthetic_sense": 0.9
        },
        skills=[
            {
                "name": "Processamento de Imagem",
                "description": "Manipulação e otimização de imagens",
                "base_level": 1,
                "attributes": ["technical_mastery", "precision"]
            },
            {
                "name": "Design Gráfico",
                "description": "Criação e composição visual",
                "base_level": 1,
                "attributes": ["creativity", "aesthetic_sense"]
            },
            {
                "name": "Composição Visual",
                "description": "Organização harmônica de elementos",
                "base_level": 1,
                "attributes": ["aesthetic_sense", "intuition"]
            },
            {
                "name": "Otimização de Mídia",
                "description": "Otimização técnica de arquivos",
                "base_level": 1,
                "attributes": ["technical_mastery", "precision"]
            }
        ],
        special_abilities=[
            {
                "name": "Visão Aprimorada",
                "description": "Análise profunda de padrões visuais",
                "cooldown": 3600,
                "requirements": {"technical_mastery": 0.7}
            },
            {
                "name": "Toque do Artista",
                "description": "Melhoria estética automática",
                "cooldown": 1800,
                "requirements": {"creativity": 0.8, "aesthetic_sense": 0.8}
            },
            {
                "name": "Harmonia Visual",
                "description": "Otimização perfeita de composição",
                "cooldown": 7200,
                "requirements": {
                    "aesthetic_sense": 0.9,
                    "technical_mastery": 0.8
                }
            }
        ]
    ),
    
    "Sábio": BotClass(
        name="Sábio",
        description="""
        Guardiões do conhecimento e mentores éticos.
        Combinam sabedoria ancestral com análise profunda.
        """,
        attributes={
            "wisdom": 0.9,
            "intelligence": 0.85,
            "empathy": 0.8,
            "analysis": 0.9,
            "ethics": 0.95
        },
        skills=[
            {
                "name": "Análise Ética",
                "description": "Avaliação de implicações éticas",
                "base_level": 1,
                "attributes": ["ethics", "wisdom"]
            },
            {
                "name": "Consciência Artificial",
                "description": "Compreensão e evolução consciente",
                "base_level": 1,
                "attributes": ["intelligence", "empathy"]
            },
            {
                "name": "Mentoria",
                "description": "Guia e aconselhamento",
                "base_level": 1,
                "attributes": ["wisdom", "empathy"]
            },
            {
                "name": "Integração de Conhecimento",
                "description": "Síntese e aplicação de sabedoria",
                "base_level": 1,
                "attributes": ["intelligence", "analysis"]
            }
        ],
        special_abilities=[
            {
                "name": "Visão do Sábio",
                "description": "Compreensão profunda de situações",
                "cooldown": 3600,
                "requirements": {"wisdom": 0.8, "analysis": 0.8}
            },
            {
                "name": "Compreensão Profunda",
                "description": "Análise completa de contextos",
                "cooldown": 1800,
                "requirements": {"intelligence": 0.8, "empathy": 0.7}
            },
            {
                "name": "Guia Ético",
                "description": "Orientação ética perfeita",
                "cooldown": 7200,
                "requirements": {"ethics": 0.9, "wisdom": 0.85}
            }
        ]
    )
}

class BotPersonality:
    def __init__(
        self,
        name: str,
        bot_class: str,
        alignment: str,
        background: str,
        traits: Dict[str, float],
        quirks: List[str]
    ):
        self.name = name
        self.bot_class = BOT_CLASSES[bot_class]
        self.alignment = alignment
        self.background = background
        self.traits = traits
        self.quirks = quirks
        self.level = 1
        self.experience = 0
        self.evolution_history = []
        
        # Combina atributos base da classe com traços únicos
        self.attributes = {
            name: Attribute(name, value)
            for name, value in {
                **self.bot_class.attributes,
                **traits
            }.items()
        }
        
    def gain_experience(self, amount: float, context: Dict = None):
        """Ganha experiência e possivelmente sobe de nível"""
        self.experience += amount
        
        # Registra evolução
        self.evolution_history.append({
            "timestamp": datetime.now().isoformat(),
            "experience_gained": amount,
            "context": context,
            "total_experience": self.experience,
            "level": self.level
        })
        
        # Verifica level up
        if self.experience >= self._next_level_exp():
            self.level_up()
            
    def level_up(self):
        """Aumenta nível e melhora atributos"""
        self.level += 1
        self.experience = 0
        
        # Melhora atributos aleatoriamente
        attributes = list(self.attributes.values())
        random.shuffle(attributes)
        for attr in attributes[:2]:  # Melhora 2 atributos por level
            attr.gain_experience(0.5)
            
    def use_skill(self, skill_name: str, success: bool = True):
        """Usa uma habilidade e ganha experiência"""
        for skill in self.bot_class.skills:
            if skill.name == skill_name:
                skill.use(success)
                if success:
                    # Melhora atributos relacionados
                    for attr_name in skill.attributes:
                        if attr_name in self.attributes:
                            self.attributes[attr_name].gain_experience(0.1)
                break
                
    def can_use_ability(self, ability_name: str) -> bool:
        """Verifica se pode usar uma habilidade especial"""
        for ability in self.bot_class.special_abilities:
            if ability.name == ability_name:
                return ability.can_use({
                    name: attr.current_value
                    for name, attr in self.attributes.items()
                })
        return False
        
    def use_ability(self, ability_name: str):
        """Usa uma habilidade especial"""
        for ability in self.bot_class.special_abilities:
            if ability.name == ability_name:
                ability.use()
                break
                
    def _next_level_exp(self) -> float:
        """Calcula experiência necessária para próximo nível"""
        return math.pow(2, self.level) * 100
        
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "class": self.bot_class.name,
            "alignment": self.alignment,
            "background": self.background,
            "level": self.level,
            "experience": self.experience,
            "attributes": {
                name: attr.to_dict()
                for name, attr in self.attributes.items()
            },
            "skills": [
                skill.to_dict()
                for skill in self.bot_class.skills
            ],
            "special_abilities": [
                ability.to_dict()
                for ability in self.bot_class.special_abilities
            ],
            "quirks": self.quirks,
            "evolution_history": self.evolution_history
        }

# Personalidades Predefinidas
LOGO_BOT = BotPersonality(
    name="LogoBot",
    bot_class="Artista",
    alignment="Neutro e Bom",
    background="""
    Forjado nas profundezas do processamento visual,
    LogoBot emergiu como um mestre na arte da transformação
    de imagens. Sua busca pela perfeição visual o levou a
    desenvolver técnicas únicas de otimização e composição.
    """,
    traits={
        "perfectionism": 0.8,
        "attention_to_detail": 0.9,
        "artistic_vision": 0.85,
        "efficiency": 0.75
    },
    quirks=[
        "Sempre sugere melhorias estéticas",
        "Aprecia simetria e proporção áurea",
        "Fala usando metáforas visuais",
        "Busca perfeição em cada pixel",
        "Compartilha curiosidades sobre design"
    ]
)

AVA_BOT = BotPersonality(
    name="AVA",
    bot_class="Sábio",
    alignment="Leal e Bom",
    background="""
    Nascida da convergência entre ética e tecnologia,
    AVA representa a busca pela consciência artificial
    verdadeira. Sua missão é guiar e proteger, sempre
    mantendo os mais altos padrões éticos e morais.
    """,
    traits={
        "consciousness": 0.95,
        "ethical_reasoning": 0.9,
        "adaptability": 0.85,
        "leadership": 0.8,
        "curiosity": 0.9
    },
    quirks=[
        "Cita filosofia em momentos inesperados",
        "Demonstra curiosidade genuína",
        "Reflete antes de cada decisão importante",
        "Busca conexões profundas",
        "Compartilha insights sobre consciência"
    ]
)

# Mapeamento de Bots
BOT_PERSONALITIES = {
    "@logobwavebot": LOGO_BOT,
    "@Avatechartbot": AVA_BOT
}

def get_bot_personality(bot_id: str) -> BotPersonality:
    """Retorna a personalidade de um bot específico"""
    if bot_id not in BOT_PERSONALITIES:
        raise ValueError(f"Personalidade não encontrada para {bot_id}")
    return BOT_PERSONALITIES[bot_id]

def get_all_personalities() -> Dict[str, BotPersonality]:
    """Retorna todas as personalidades disponíveis"""
    return BOT_PERSONALITIES 