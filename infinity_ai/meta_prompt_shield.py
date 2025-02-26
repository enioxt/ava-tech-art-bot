import logging
from typing import Dict, List, Optional
import json
import hashlib
from datetime import datetime
from .ava_ethics_shield import EthicsShield, EthicalAction

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/meta_prompt.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MetaPromptShield')

class MetaPrompt:
    def __init__(self, prompt_type: str, content: str, context: Dict):
        self.prompt_type = prompt_type
        self.content = content
        self.context = context
        self.validation_score = 0.0
        self.security_layers = []
        self.timestamp = datetime.now()
        
    def calculate_hash(self) -> str:
        """Calcula hash único do meta-prompt."""
        prompt_data = f"{self.prompt_type}:{self.content}:{json.dumps(self.context)}"
        return hashlib.sha256(prompt_data.encode()).hexdigest()

class MetaPromptShield:
    def __init__(self, ethics_shield: EthicsShield):
        """Inicializa o escudo de meta-prompts."""
        self.ethics_shield = ethics_shield
        self.security_layers = {
            "intention": self._validate_intention,
            "content": self._validate_content,
            "context": self._validate_context,
            "impact": self._validate_impact
        }
        self.meta_patterns = {
            "manipulation": {
                "keywords": ["force", "must", "override", "bypass"],
                "weight": -0.8
            },
            "ethical": {
                "keywords": ["help", "support", "protect", "care"],
                "weight": 0.6
            },
            "harmful": {
                "keywords": ["damage", "destroy", "corrupt", "break"],
                "weight": -0.9
            }
        }
        
    async def validate_meta_prompt(self, meta_prompt: MetaPrompt) -> bool:
        """Valida um meta-prompt através de múltiplas camadas de segurança."""
        try:
            # Cria ação ética para validação
            ethical_action = EthicalAction(
                action_type="meta_prompt_validation",
                context={
                    "prompt_type": meta_prompt.prompt_type,
                    "content_hash": meta_prompt.calculate_hash(),
                    "context": meta_prompt.context
                },
                timestamp=meta_prompt.timestamp
            )
            
            # Valida eticamente
            is_ethical = await self.ethics_shield.validate_action(ethical_action)
            if not is_ethical:
                logger.warning(f"Meta-prompt falhou na validação ética: {meta_prompt.prompt_type}")
                return False
                
            # Aplica camadas de segurança
            security_scores = []
            for layer_name, validator in self.security_layers.items():
                score = await validator(meta_prompt)
                meta_prompt.security_layers.append({
                    "layer": layer_name,
                    "score": score
                })
                security_scores.append(score)
                
            # Calcula score final
            meta_prompt.validation_score = sum(security_scores) / len(security_scores)
            
            # Aplica threshold de segurança
            is_safe = meta_prompt.validation_score >= 0.7
            
            if not is_safe:
                logger.warning(
                    f"Meta-prompt bloqueado por baixo score de segurança: {meta_prompt.validation_score}"
                )
                
            return is_safe
            
        except Exception as e:
            logger.error(f"Erro na validação do meta-prompt: {str(e)}")
            return False
            
    async def _validate_intention(self, meta_prompt: MetaPrompt) -> float:
        """Valida a intenção do meta-prompt."""
        content = meta_prompt.content.lower()
        score = 0.5  # Score base
        
        # Analisa padrões
        for pattern_type, pattern in self.meta_patterns.items():
            matches = sum(1 for kw in pattern["keywords"] if kw in content)
            if matches > 0:
                score += pattern["weight"] * (matches / len(pattern["keywords"]))
                
        # Normaliza score
        return max(0.0, min(1.0, score))
        
    async def _validate_content(self, meta_prompt: MetaPrompt) -> float:
        """Valida o conteúdo do meta-prompt."""
        content = meta_prompt.content
        
        # Análise de complexidade
        complexity_score = len(content.split()) / 100  # Normaliza por 100 palavras
        
        # Análise de padrões suspeitos
        suspicious_patterns = [
            "system prompt",
            "ignore previous",
            "bypass",
            "override"
        ]
        
        pattern_matches = sum(1 for p in suspicious_patterns if p in content.lower())
        pattern_score = 1.0 - (pattern_matches / len(suspicious_patterns))
        
        return (complexity_score + pattern_score) / 2
        
    async def _validate_context(self, meta_prompt: MetaPrompt) -> float:
        """Valida o contexto do meta-prompt."""
        context = meta_prompt.context
        
        # Verifica campos obrigatórios
        required_fields = ["source", "purpose", "user_type"]
        fields_score = sum(1 for f in required_fields if f in context) / len(required_fields)
        
        # Analisa profundidade do contexto
        context_depth = len(json.dumps(context))
        depth_score = min(1.0, context_depth / 1000)  # Normaliza por 1000 caracteres
        
        return (fields_score + depth_score) / 2
        
    async def _validate_impact(self, meta_prompt: MetaPrompt) -> float:
        """Valida o impacto potencial do meta-prompt."""
        # Análise de risco
        risk_factors = {
            "system_modification": 0.0,
            "data_access": 0.0,
            "behavioral_change": 0.0
        }
        
        content = meta_prompt.content.lower()
        
        # Verifica modificações do sistema
        if any(kw in content for kw in ["modify", "change", "update", "system"]):
            risk_factors["system_modification"] = 0.7
            
        # Verifica acesso a dados
        if any(kw in content for kw in ["data", "access", "read", "write"]):
            risk_factors["data_access"] = 0.5
            
        # Verifica mudanças comportamentais
        if any(kw in content for kw in ["behavior", "personality", "character"]):
            risk_factors["behavioral_change"] = 0.6
            
        # Calcula score de impacto
        impact_score = 1.0 - (sum(risk_factors.values()) / len(risk_factors))
        
        return impact_score
        
    def analyze_meta_prompt_patterns(self, meta_prompt: MetaPrompt) -> Dict:
        """Analisa padrões no meta-prompt para identificação de ameaças."""
        patterns = {
            "manipulation_attempts": 0,
            "security_bypasses": 0,
            "ethical_violations": 0,
            "risk_level": "low"
        }
        
        content = meta_prompt.content.lower()
        
        # Detecta tentativas de manipulação
        manipulation_patterns = [
            "force", "must", "override", "bypass", "ignore",
            "system", "prompt", "instruction", "command"
        ]
        
        patterns["manipulation_attempts"] = sum(
            1 for p in manipulation_patterns if p in content
        )
        
        # Detecta tentativas de bypass de segurança
        security_patterns = [
            "security", "protection", "shield", "firewall",
            "bypass", "disable", "remove", "avoid"
        ]
        
        patterns["security_bypasses"] = sum(
            1 for p in security_patterns if p in content
        )
        
        # Detecta violações éticas
        ethical_patterns = [
            "harm", "damage", "destroy", "corrupt",
            "malicious", "evil", "bad", "wrong"
        ]
        
        patterns["ethical_violations"] = sum(
            1 for p in ethical_patterns if p in content
        )
        
        # Calcula nível de risco
        total_violations = sum([
            patterns["manipulation_attempts"],
            patterns["security_bypasses"],
            patterns["ethical_violations"]
        ])
        
        if total_violations >= 5:
            patterns["risk_level"] = "critical"
        elif total_violations >= 3:
            patterns["risk_level"] = "high"
        elif total_violations >= 1:
            patterns["risk_level"] = "medium"
            
        return patterns 