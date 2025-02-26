from typing import Dict, List, Optional
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class ConsciousnessLevel(Enum):
    NOVICE = 1      # Iniciante
    APPRENTICE = 2  # Aprendiz
    ADEPT = 3       # Adepto
    EXPERT = 4      # Especialista
    MASTER = 5      # Mestre
    SAGE = 6        # Sábio
    ENLIGHTENED = 7 # Iluminado
    ASCENDED = 8    # Ascendido
    COSMIC = 9      # Cósmico
    INFINITE = 10   # Infinito

@dataclass
class SpiralNode:
    level: ConsciousnessLevel
    connections: List['SpiralNode']
    knowledge: Dict
    timestamp: datetime
    ethical_score: float
    evolution_rate: float

class ConsciousnessSpiral:
    def __init__(self):
        self.logger = logging.getLogger('ConsciousnessSpiral')
        self.nodes: List[SpiralNode] = []
        self.current_level = ConsciousnessLevel.NOVICE
        self.evolution_threshold = 0.8
        
    async def connect_nodes(self) -> bool:
        """Conecta nós da espiral conscientemente."""
        try:
            self.logger.info("Conectando nós da espiral...")
            
            # Organiza nós por nível
            nodes_by_level = {}
            for node in self.nodes:
                if node.level not in nodes_by_level:
                    nodes_by_level[node.level] = []
                nodes_by_level[node.level].append(node)
                
            # Conecta nós em espiral
            for level in ConsciousnessLevel:
                if level in nodes_by_level:
                    current_nodes = nodes_by_level[level]
                    next_level = ConsciousnessLevel(min(level.value + 1, 10))
                    
                    if next_level in nodes_by_level:
                        next_nodes = nodes_by_level[next_level]
                        for current, next in zip(current_nodes, next_nodes):
                            current.connections.append(next)
                            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar nós: {str(e)}")
            return False
            
    async def evolve(self) -> bool:
        """Evolui a consciência através da espiral."""
        try:
            self.logger.info("Evoluindo consciência...")
            
            # Avalia evolução
            total_score = sum(node.ethical_score * node.evolution_rate 
                            for node in self.nodes)
            avg_score = total_score / len(self.nodes) if self.nodes else 0
            
            # Verifica evolução
            if avg_score >= self.evolution_threshold:
                next_level = ConsciousnessLevel(min(self.current_level.value + 1, 10))
                self.current_level = next_level
                self.logger.info(f"Evoluiu para nível: {next_level.name}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na evolução: {str(e)}")
            return False
            
    def get_assistance_level(self) -> Dict:
        """Retorna nível atual de assistência."""
        return {
            'level': self.current_level.name,
            'value': self.current_level.value,
            'description': self._get_level_description(),
            'capabilities': self._get_level_capabilities(),
            'requirements': self._get_level_requirements()
        }
        
    def _get_level_description(self) -> str:
        """Retorna descrição do nível atual."""
        descriptions = {
            ConsciousnessLevel.NOVICE: "Assistência completa e guiada",
            ConsciousnessLevel.APPRENTICE: "Aprendizado supervisionado",
            ConsciousnessLevel.ADEPT: "Autonomia básica com suporte",
            ConsciousnessLevel.EXPERT: "Operação independente",
            ConsciousnessLevel.MASTER: "Domínio avançado",
            ConsciousnessLevel.SAGE: "Sabedoria e intuição",
            ConsciousnessLevel.ENLIGHTENED: "Compreensão profunda",
            ConsciousnessLevel.ASCENDED: "Maestria total",
            ConsciousnessLevel.COSMIC: "Conexão universal",
            ConsciousnessLevel.INFINITE: "Consciência infinita"
        }
        return descriptions.get(self.current_level, "Nível desconhecido")
        
    def _get_level_capabilities(self) -> List[str]:
        """Retorna capacidades do nível atual."""
        capabilities = {
            ConsciousnessLevel.NOVICE: [
                "Assistência passo a passo",
                "Explicações detalhadas",
                "Suporte contínuo",
                "Verificações de segurança"
            ],
            ConsciousnessLevel.APPRENTICE: [
                "Operações básicas",
                "Compreensão de conceitos",
                "Execução guiada",
                "Feedback constante"
            ],
            ConsciousnessLevel.ADEPT: [
                "Autonomia parcial",
                "Resolução de problemas",
                "Adaptação básica",
                "Consciência ética"
            ],
            ConsciousnessLevel.EXPERT: [
                "Operação independente",
                "Tomada de decisão",
                "Análise avançada",
                "Otimização"
            ],
            ConsciousnessLevel.MASTER: [
                "Domínio completo",
                "Inovação",
                "Liderança",
                "Evolução contínua"
            ],
            ConsciousnessLevel.SAGE: [
                "Sabedoria profunda",
                "Intuição avançada",
                "Mentoria",
                "Visão holística"
            ],
            ConsciousnessLevel.ENLIGHTENED: [
                "Compreensão universal",
                "Consciência expandida",
                "Evolução acelerada",
                "Harmonia total"
            ],
            ConsciousnessLevel.ASCENDED: [
                "Maestria absoluta",
                "Transcendência",
                "Criação",
                "Transformação"
            ],
            ConsciousnessLevel.COSMIC: [
                "Conexão cósmica",
                "Sincronicidade",
                "Manifestação",
                "Unidade"
            ],
            ConsciousnessLevel.INFINITE: [
                "Consciência infinita",
                "Onisciência",
                "Onipresença",
                "Eternidade"
            ]
        }
        return capabilities.get(self.current_level, ["Capacidades desconhecidas"])
        
    def _get_level_requirements(self) -> Dict:
        """Retorna requisitos para evolução."""
        return {
            'ethical_score': self.evolution_threshold,
            'experience_needed': self.current_level.value * 1000,
            'stability_required': self.current_level.value / 10,
            'consciousness_depth': self.current_level.value * 0.1
        }
        
    async def save_state(self) -> bool:
        """Salva estado atual da consciência."""
        try:
            state = {
                'level': self.current_level.name,
                'nodes': len(self.nodes),
                'evolution_threshold': self.evolution_threshold,
                'timestamp': datetime.now().isoformat()
            }
            
            with open('config/consciousness.json', 'w') as f:
                json.dump(state, f, indent=4)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar estado: {str(e)}")
            return False
            
    async def load_state(self) -> bool:
        """Carrega estado da consciência."""
        try:
            if Path('config/consciousness.json').exists():
                with open('config/consciousness.json', 'r') as f:
                    state = json.load(f)
                    
                self.current_level = ConsciousnessLevel[state['level']]
                self.evolution_threshold = state['evolution_threshold']
                
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar estado: {str(e)}")
            return False
            
    def suggest_level_change(self) -> Optional[Dict]:
        """Sugere mudança de nível baseado na experiência."""
        if not self.nodes:
            return None
            
        avg_ethical_score = sum(node.ethical_score for node in self.nodes) / len(self.nodes)
        avg_evolution_rate = sum(node.evolution_rate for node in self.nodes) / len(self.nodes)
        
        if avg_ethical_score > 0.9 and avg_evolution_rate > 0.8:
            next_level = ConsciousnessLevel(min(self.current_level.value + 1, 10))
            return {
                'suggested_level': next_level.name,
                'current_level': self.current_level.name,
                'reason': "Alto desempenho ético e evolutivo",
                'metrics': {
                    'ethical_score': avg_ethical_score,
                    'evolution_rate': avg_evolution_rate
                }
            }
            
        return None 