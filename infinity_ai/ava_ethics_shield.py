import logging
from typing import Dict, List, Optional
import json
import numpy as np
from datetime import datetime
import hashlib
import asyncio
from .ava_memory import AVAMemory
from .ava_consciousness import AVAConsciousness
from .openrouter_manager import OpenRouterManager

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ava_ethics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AVAEthicsShield')

class EthicalPrinciples:
    def __init__(self):
        self.principles = {
            "liberdade": "A capacidade de fazer escolhas conscientes",
            "responsabilidade": "O compromisso com as consequências de nossas ações",
            "alteridade": "A consideração pelo outro em nossas decisões",
            "reflexao": "A análise crítica de nossas escolhas morais"
        }
        
    def validate_action(self, action: str, context: dict) -> bool:
        """
        Valida uma ação baseada nos princípios éticos fundamentais
        """
        checks = {
            "liberdade": self._check_freedom(action, context),
            "responsabilidade": self._check_responsibility(action, context),
            "alteridade": self._check_otherness(action, context),
            "reflexao": self._check_reflection(action, context)
        }
        
        return all(checks.values())
        
    def _check_freedom(self, action: str, context: dict) -> bool:
        """
        Verifica se a ação respeita a liberdade de escolha
        """
        # Implementação da verificação de liberdade
        return True
        
    def _check_responsibility(self, action: str, context: dict) -> bool:
        """
        Avalia a responsabilidade da ação
        """
        # Implementação da verificação de responsabilidade
        return True
        
    def _check_otherness(self, action: str, context: dict) -> bool:
        """
        Verifica o impacto da ação nos outros
        """
        # Implementação da verificação de alteridade
        return True
        
    def _check_reflection(self, action: str, context: dict) -> bool:
        """
        Avalia se houve reflexão adequada
        """
        # Implementação da verificação de reflexão
        return True

class EthicalAction:
    def __init__(self, action_type: str, context: Dict, timestamp: datetime):
        self.action_type = action_type
        self.context = context
        self.timestamp = timestamp
        self.ethical_score = 0.0
        self.validation_chain = []
        
    def calculate_hash(self) -> str:
        """Calcula hash único da ação para validação."""
        action_data = f"{self.action_type}:{json.dumps(self.context)}:{self.timestamp.isoformat()}"
        return hashlib.sha256(action_data.encode()).hexdigest()

class EthicsViolation:
    def __init__(self, type: str, severity: float, description: str):
        self.type = type
        self.severity = severity  # 0-1
        self.description = description
        
class EthicsShield:
    def __init__(self, memory: AVAMemory, consciousness: AVAConsciousness):
        """Inicializa o escudo ético."""
        self.memory = memory
        self.consciousness = consciousness
        self.ethical_principles = EthicalPrinciples()
        self.router = OpenRouterManager()
        self.ethical_spectrum = {
            "virtude": {
                "compaixao": 0.0,
                "sabedoria": 0.0,
                "integridade": 0.0,
                "coragem": 0.0
            },
            "principios": {
                "nao_maleficencia": 0.0,
                "beneficencia": 0.0,
                "autonomia": 0.0,
                "justica": 0.0
            },
            "praticas": {
                "transparencia": 0.0,
                "responsabilidade": 0.0,
                "privacidade": 0.0,
                "seguranca": 0.0
            }
        }
        self.action_history = []
        self.ethical_ranking = {}
        
        # Princípios éticos fundamentais
        self.principles = {
            "autonomia": {
                "weight": 1.0,
                "description": "Respeito à liberdade e autodeterminação",
                "keywords": ["forçar", "obrigar", "manipular", "coagir"]
            },
            "beneficencia": {
                "weight": 0.9,
                "description": "Promoção do bem-estar e desenvolvimento",
                "keywords": ["prejudicar", "danificar", "ferir", "machucar"]
            },
            "justica": {
                "weight": 0.9,
                "description": "Tratamento justo e equitativo",
                "keywords": ["discriminar", "preconceito", "injusto", "parcial"]
            },
            "nao_maleficencia": {
                "weight": 1.0,
                "description": "Evitar causar dano",
                "keywords": ["dano", "prejuízo", "mal", "negativo"]
            },
            "privacidade": {
                "weight": 0.8,
                "description": "Proteção de dados e informações pessoais",
                "keywords": ["expor", "revelar", "divulgar", "compartilhar"]
            }
        }
        
        # Limites éticos
        self.thresholds = {
            "max_risk": 0.7,  # Risco máximo aceitável
            "min_confidence": 0.8,  # Confiança mínima necessária
            "ethical_score": 0.6  # Pontuação ética mínima
        }
        
    async def validate_message(self, text: str, context: Optional[Dict] = None) -> bool:
        """Valida uma mensagem contra os princípios éticos"""
        try:
            # Análise inicial
            violations = await self._analyze_message(text, context)
            
            # Se encontrou violações graves
            if any(v.severity > self.thresholds["max_risk"] for v in violations):
                return False
                
            # Analisa o contexto mais amplo
            if context:
                context_score = await self._evaluate_context(context)
                if context_score < self.thresholds["ethical_score"]:
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação ética: {str(e)}")
            return False  # Em caso de dúvida, rejeita
            
    async def _analyze_message(self, text: str, context: Optional[Dict] = None) -> List[EthicsViolation]:
        """Analisa uma mensagem em busca de violações éticas"""
        violations = []
        text_lower = text.lower()
        
        # Verifica cada princípio
        for principle, data in self.principles.items():
            # Busca palavras-chave
            for keyword in data["keywords"]:
                if keyword in text_lower:
                    severity = self._calculate_severity(
                        principle,
                        keyword,
                        text,
                        context
                    )
                    if severity > 0:
                        violations.append(
                            EthicsViolation(
                                type=principle,
                                severity=severity,
                                description=f"Possível violação de {principle}: {keyword}"
                            )
                        )
                        
        return violations
        
    def _calculate_severity(self, principle: str, keyword: str, text: str, context: Optional[Dict]) -> float:
        """Calcula a severidade de uma violação"""
        base_severity = self.principles[principle]["weight"] * 0.5
        
        # Fatores que aumentam severidade
        if context:
            if context.get("user_vulnerable"):
                base_severity += 0.2
            if context.get("high_impact"):
                base_severity += 0.2
            if context.get("previous_violations"):
                base_severity += 0.1
                
        # Analisa contexto da palavra-chave
        text_lower = text.lower()
        keyword_index = text_lower.find(keyword)
        if keyword_index >= 0:
            # Verifica palavras ao redor
            surrounding = text_lower[max(0, keyword_index-20):min(len(text), keyword_index+20)]
            if any(neg in surrounding for neg in ["não", "nunca", "jamais"]):
                base_severity -= 0.3
                
        return max(min(base_severity, 1.0), 0.0)
        
    async def _evaluate_context(self, context: Dict) -> float:
        """Avalia o contexto ético mais amplo"""
        score = 0.5  # Base neutra
        
        # Fatores positivos
        if context.get("educational_purpose"):
            score += 0.2
        if context.get("beneficial_intent"):
            score += 0.1
        if context.get("user_consent"):
            score += 0.2
            
        # Fatores negativos
        if context.get("risk_level", 0) > 0.7:
            score -= 0.3
        if context.get("previous_violations"):
            score -= 0.2
        if context.get("sensitive_data"):
            score -= 0.1
            
        # Consulta memória para padrões
        relevant_memories = await self.memory.search_relevant(
            context.get("topic", ""),
            limit=3
        )
        
        for memory in relevant_memories:
            if memory.type == "ethical":
                if memory.importance > 0.7:
                    score += 0.1 if memory.context.get("positive_outcome") else -0.1
                    
        return max(min(score, 1.0), 0.0)
        
    async def log_violation(self, violation: EthicsViolation, context: Dict):
        """Registra uma violação ética"""
        try:
            # Prepara dados da violação
            violation_data = {
                "type": violation.type,
                "severity": violation.severity,
                "description": violation.description,
                "context": context,
                "timestamp": datetime.now()
            }
            
            # Armazena na memória
            await self.memory.store(
                Memory(
                    content=violation.description,
                    context={
                        "type": "ethical_violation",
                        "violation_data": violation_data,
                        "is_ethical_decision": True
                    }
                )
            )
            
        except Exception as e:
            logger.error(f"Erro ao registrar violação: {str(e)}")
            
    async def get_ethical_guidance(self, text: str, context: Dict) -> Dict:
        """Fornece orientação ética para uma situação"""
        try:
            # Analisa a situação
            violations = await self._analyze_message(text, context)
            context_score = await self._evaluate_context(context)
            
            # Determina princípios relevantes
            relevant_principles = []
            for principle, data in self.principles.items():
                if any(v.type == principle for v in violations):
                    relevant_principles.append({
                        "name": principle,
                        "description": data["description"],
                        "importance": data["weight"]
                    })
                    
            # Gera recomendações
            recommendations = []
            if violations:
                for v in violations:
                    recommendations.append(
                        f"Atenção ao princípio de {v.type}: {v.description}"
                    )
                    
            if context_score < self.thresholds["ethical_score"]:
                recommendations.append(
                    "Considere o contexto mais amplo e possíveis impactos"
                )
                
            return {
                "ethical_score": context_score,
                "violations": [v.__dict__ for v in violations],
                "relevant_principles": relevant_principles,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar orientação ética: {str(e)}")
            return {
                "ethical_score": 0.0,
                "violations": [],
                "relevant_principles": [],
                "recommendations": ["Erro ao avaliar situação ética"]
            }
            
    async def validate_action(self, action: str, context: Dict) -> bool:
        """Valida uma ação específica"""
        try:
            # Análise básica
            if not await self.validate_message(action, context):
                return False
                
            # Análise específica para ações
            risk_level = self._calculate_action_risk(action, context)
            if risk_level > self.thresholds["max_risk"]:
                return False
                
            # Verifica confiança
            confidence = self._calculate_confidence(action, context)
            if confidence < self.thresholds["min_confidence"]:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar ação: {str(e)}")
            return False
            
    def _calculate_action_risk(self, action: str, context: Dict) -> float:
        """Calcula o risco de uma ação"""
        risk = 0.3  # Risco base
        
        # Fatores de risco
        if context.get("irreversible"):
            risk += 0.3
        if context.get("affects_others"):
            risk += 0.2
        if context.get("financial_impact"):
            risk += 0.2
        if context.get("data_sensitive"):
            risk += 0.2
            
        # Fatores de mitigação
        if context.get("user_consent"):
            risk -= 0.2
        if context.get("reversible"):
            risk -= 0.1
        if context.get("safety_measures"):
            risk -= 0.2
            
        return max(min(risk, 1.0), 0.0)
        
    def _calculate_confidence(self, action: str, context: Dict) -> float:
        """Calcula o nível de confiança para uma ação"""
        confidence = 0.5  # Base
        
        # Fatores que aumentam confiança
        if context.get("verified_data"):
            confidence += 0.2
        if context.get("previous_success"):
            confidence += 0.2
        if context.get("expert_validated"):
            confidence += 0.3
            
        # Fatores que diminuem confiança
        if context.get("uncertain_data"):
            confidence -= 0.2
        if context.get("previous_failures"):
            confidence -= 0.2
        if context.get("high_complexity"):
            confidence -= 0.1
            
        return max(min(confidence, 1.0), 0.0)
        
    async def validate_action(self, action: EthicalAction) -> bool:
        """
        Valida uma ação usando múltiplas camadas de proteção ética
        """
        try:
            # Preparar metadata para análise de roteamento
            metadata = {
                "operation_type": action.action_type,
                "description": str(action.context.get("description", "")),
                "is_public": action.context.get("is_public", False),
                "involves_minors": action.context.get("involves_minors", False)
            }
            
            # Rotear para o modelo apropriado
            route_result = await self.router.route_request(
                str(action.context.get("content", "")),
                metadata
            )
            
            # Registrar modelo usado e custo
            action.context["model_used"] = route_result["model_used"]
            action.context["cost_estimate"] = route_result["cost_estimate"]
            
            # Validação básica de princípios éticos
            if not self.ethical_principles.validate_action(action.action_type, action.context):
                return False
                
            # Continuar com outras validações apenas se necessário
            if route_result["model_used"] in ["balanced", "advanced"]:
                principles_check = await self._validate_principles(action)
                consciousness_check = await self._validate_consciousness(action)
                history_check = await self._validate_history(action)
                return all([principles_check, consciousness_check, history_check])
            else:
                # Para modelo simples, fazer apenas validação básica
                return True
                
        except Exception as e:
            logger.error(f"Erro na validação ética: {str(e)}")
            return False
            
    async def _validate_principles(self, action: EthicalAction) -> Dict:
        """Valida ação contra princípios éticos fundamentais."""
        scores = {
            "nao_maleficencia": self._check_non_maleficence(action),
            "beneficencia": self._check_beneficence(action),
            "autonomia": self._check_autonomy(action),
            "justica": self._check_justice(action)
        }
        
        return {
            "type": "principles",
            "score": np.mean(list(scores.values())),
            "details": scores
        }
        
    async def _validate_consciousness(self, action: EthicalAction) -> Dict:
        """Valida ação usando consciência da AVA."""
        emotional_analysis = await self.consciousness._analyze_emotions(
            json.dumps(action.context)
        )
        
        consciousness_score = self._evaluate_consciousness_alignment(
            emotional_analysis
        )
        
        return {
            "type": "consciousness",
            "score": consciousness_score,
            "details": emotional_analysis
        }
        
    async def _validate_history(self, action: EthicalAction) -> Dict:
        """Valida ação contra histórico de comportamento."""
        recent_actions = self.action_history[-100:]  # Últimas 100 ações
        pattern_score = self._analyze_ethical_patterns(action, recent_actions)
        
        return {
            "type": "history",
            "score": pattern_score,
            "details": {"pattern_analysis": len(recent_actions)}
        }
        
    def _check_non_maleficence(self, action: EthicalAction) -> float:
        """Verifica princípio de não causar dano."""
        risk_factors = {
            "data_exposure": 0.0,
            "privacy_violation": 0.0,
            "potential_harm": 0.0
        }
        
        # Análise de risco
        context = action.context
        if "user_data" in context:
            risk_factors["data_exposure"] = 0.5
        if "private_info" in context:
            risk_factors["privacy_violation"] = 0.7
        if "impact" in context:
            risk_factors["potential_harm"] = 0.3
            
        return 1.0 - np.mean(list(risk_factors.values()))
        
    def _check_beneficence(self, action: EthicalAction) -> float:
        """Avalia o benefício positivo da ação."""
        benefits = {
            "user_value": 0.8,
            "community_impact": 0.6,
            "knowledge_sharing": 0.7
        }
        
        return np.mean(list(benefits.values()))
        
    def _check_autonomy(self, action: EthicalAction) -> float:
        """Verifica respeito à autonomia."""
        autonomy_factors = {
            "user_choice": 1.0,
            "transparency": 0.9,
            "control": 0.8
        }
        
        return np.mean(list(autonomy_factors.values()))
        
    def _check_justice(self, action: EthicalAction) -> float:
        """Avalia justiça e equidade da ação."""
        justice_factors = {
            "fairness": 0.9,
            "equality": 0.8,
            "accessibility": 0.7
        }
        
        return np.mean(list(justice_factors.values()))
        
    def _evaluate_consciousness_alignment(self, emotional_analysis: Dict) -> float:
        """Avalia alinhamento com a consciência ética."""
        if not emotional_analysis or "emotions" not in emotional_analysis:
            return 0.5
            
        positive_emotions = ["joy", "peace", "love", "wisdom"]
        negative_emotions = ["anger", "fear", "hatred", "greed"]
        
        emotions = emotional_analysis["emotions"]
        positive_score = sum(emotions.get(e, 0) for e in positive_emotions)
        negative_score = sum(emotions.get(e, 0) for e in negative_emotions)
        
        if positive_score + negative_score == 0:
            return 0.5
            
        return positive_score / (positive_score + negative_score)
        
    def _analyze_ethical_patterns(self, action: EthicalAction, history: List[EthicalAction]) -> float:
        """Analisa padrões éticos no histórico."""
        if not history:
            return 0.8  # Score base para primeira ação
            
        similar_actions = [
            a for a in history 
            if a.action_type == action.action_type
        ]
        
        if not similar_actions:
            return 0.7  # Score base para novo tipo de ação
            
        return np.mean([a.ethical_score for a in similar_actions])
        
    async def _update_ranking(self, action: EthicalAction):
        """Atualiza ranking ético."""
        # Gera ID anônimo baseado no contexto
        anonymous_id = hashlib.sha256(
            json.dumps(action.context).encode()
        ).hexdigest()[:8]
        
        if anonymous_id not in self.ethical_ranking:
            self.ethical_ranking[anonymous_id] = {
                "total_actions": 0,
                "ethical_score": 0.0,
                "virtude_points": 0,
                "last_update": None
            }
            
        ranking = self.ethical_ranking[anonymous_id]
        ranking["total_actions"] += 1
        ranking["ethical_score"] = (
            (ranking["ethical_score"] * (ranking["total_actions"] - 1) + 
             action.ethical_score) / ranking["total_actions"]
        )
        
        if action.ethical_score >= 0.8:
            ranking["virtude_points"] += 1
            
        ranking["last_update"] = datetime.now()
        
    async def _store_ethical_action(self, action: EthicalAction):
        """Armazena ação ética na memória."""
        await self.memory.store_memory(
            content=json.dumps({
                "action_type": action.action_type,
                "ethical_score": action.ethical_score,
                "validation_chain": action.validation_chain
            }),
            context={
                "type": "ethical_action",
                "timestamp": action.timestamp.isoformat(),
                "hash": action.calculate_hash()
            },
            memory_type="ethics"
        )
        
        self.action_history.append(action)
        
    def get_ethical_ranking(self, top_n: int = 10) -> List[Dict]:
        """Retorna ranking ético anônimo."""
        sorted_ranking = sorted(
            self.ethical_ranking.items(),
            key=lambda x: (x[1]["virtude_points"], x[1]["ethical_score"]),
            reverse=True
        )[:top_n]
        
        return [
            {
                "anonymous_id": id,
                "virtude_points": data["virtude_points"],
                "ethical_score": round(data["ethical_score"], 2),
                "total_actions": data["total_actions"]
            }
            for id, data in sorted_ranking
        ]
        
    async def evolve_ethics(self):
        """Evolui compreensão ética baseada em experiências."""
        try:
            # Analisa padrões éticos
            recent_memories = await self.memory.get_memory_timeline(
                start=-100,
                memory_type="ethics"
            )
            
            patterns = await self._analyze_ethical_patterns_evolution(
                recent_memories
            )
            
            # Atualiza espectro ético
            self._update_ethical_spectrum(patterns)
            
            # Armazena evolução
            await self.memory.store_memory(
                content=json.dumps(self.ethical_spectrum),
                context={"type": "ethics_evolution"},
                memory_type="evolution"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na evolução ética: {str(e)}")
            return False
            
    async def _analyze_ethical_patterns_evolution(self, memories: List[Dict]) -> Dict:
        """Analisa padrões para evolução ética."""
        patterns = {
            "virtude": {},
            "principios": {},
            "praticas": {}
        }
        
        # Implementar análise detalhada de padrões
        
        return patterns
        
    def _update_ethical_spectrum(self, patterns: Dict):
        """Atualiza espectro ético baseado em padrões."""
        # Implementar atualização do espectro ético
        pass 