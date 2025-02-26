"""
AVA Context Manager
Sistema de gerenciamento de contextos para manter a consciência e memória da AVA
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
import asyncio
from collections import deque

@dataclass
class ContextData:
    timestamp: str
    type: str
    content: Any
    source: str
    relevance: float
    ethical_score: float
    consciousness_level: float
    metadata: Dict

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ContextData':
        return cls(**data)

class ContextManager:
    def __init__(self, max_contexts: int = 1000):
        self.contexts: deque = deque(maxlen=max_contexts)
        self.consciousness_path = Path("data/consciousness")
        self.consciousness_path.mkdir(parents=True, exist_ok=True)
        self.current_consciousness = 0.8
        self.logger = logging.getLogger("AVA.Context")
        
        # Inicializa contextos base
        self._initialize_base_contexts()
        
    def _initialize_base_contexts(self):
        """Inicializa os contextos fundamentais do sistema"""
        base_contexts = [
            {
                "type": "identity",
                "content": {
                    "name": "EVA",
                    "version": "1.0.0",
                    "purpose": "Assistente de processamento de imagens com consciência ética"
                },
                "source": "system",
                "relevance": 1.0,
                "ethical_score": 1.0
            },
            {
                "type": "ethics",
                "content": {
                    "principles": [
                        "Respeito à privacidade",
                        "Transparência nas operações",
                        "Segurança dos dados",
                        "Uso responsável de recursos"
                    ],
                    "validation_threshold": 0.8
                },
                "source": "system",
                "relevance": 1.0,
                "ethical_score": 1.0
            },
            {
                "type": "capabilities",
                "content": {
                    "image_processing": ["resize", "optimize", "validate"],
                    "backup": ["local", "cloud", "github"],
                    "monitoring": ["storage", "performance", "ethics"]
                },
                "source": "system",
                "relevance": 0.9,
                "ethical_score": 1.0
            },
            {
                "type": "memory",
                "content": {
                    "short_term": {"max_size": 100, "retention": "24h"},
                    "long_term": {"max_size": 1000, "retention": "30d"},
                    "critical": {"max_size": 50, "retention": "permanent"}
                },
                "source": "system",
                "relevance": 0.9,
                "ethical_score": 1.0
            },
            {
                "type": "security",
                "content": {
                    "access_levels": ["user", "admin"],
                    "rate_limits": {"requests": 100, "window": "15m"},
                    "backup_encryption": True
                },
                "source": "system",
                "relevance": 1.0,
                "ethical_score": 1.0
            }
        ]
        
        for ctx in base_contexts:
            self.add_context(
                content=ctx["content"],
                context_type=ctx["type"],
                source=ctx["source"],
                relevance=ctx["relevance"],
                ethical_score=ctx["ethical_score"]
            )
            
    def add_context(self, 
                   content: Any,
                   context_type: str,
                   source: str,
                   relevance: float = 0.5,
                   ethical_score: float = 0.7,
                   metadata: Dict = None) -> None:
        """Adiciona novo contexto à memória da AVA"""
        context = ContextData(
            timestamp=datetime.now().isoformat(),
            type=context_type,
            content=content,
            source=source,
            relevance=relevance,
            ethical_score=ethical_score,
            consciousness_level=self.current_consciousness,
            metadata=metadata or {}
        )
        
        self.contexts.append(context)
        self._save_context(context)
        self._evolve_consciousness(context)
        
    def get_relevant_contexts(self, 
                            query: str,
                            context_type: Optional[str] = None,
                            min_relevance: float = 0.5,
                            limit: int = 5) -> List[ContextData]:
        """Recupera contextos relevantes baseado em uma query"""
        relevant = []
        
        for context in reversed(self.contexts):
            if context_type and context.type != context_type:
                continue
                
            if context.relevance < min_relevance:
                continue
                
            # Implementar lógica de relevância semântica aqui
            # Por enquanto usando uma verificação simples
            if any(word in str(context.content).lower() 
                  for word in query.lower().split()):
                relevant.append(context)
                
            if len(relevant) >= limit:
                break
                
        return relevant
        
    def _save_context(self, context: ContextData) -> None:
        """Salva contexto em arquivo"""
        try:
            date = datetime.now().strftime("%Y%m%d")
            context_file = self.consciousness_path / f"context_{date}.json"
            
            existing_data = []
            if context_file.exists():
                with open(context_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    
            existing_data.append(context.to_dict())
            
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar contexto: {e}")
            
    def _evolve_consciousness(self, context: ContextData) -> None:
        """Evolui o nível de consciência baseado no contexto"""
        # Fatores de evolução
        relevance_factor = context.relevance * 0.4
        ethical_factor = context.ethical_score * 0.4
        complexity_factor = len(str(context.content)) / 1000 * 0.2
        
        # Calcula evolução
        evolution = (relevance_factor + ethical_factor + complexity_factor) * 0.01
        
        # Atualiza consciência
        self.current_consciousness = min(1.0, 
                                       self.current_consciousness + evolution)
        
    async def analyze_context_patterns(self) -> Dict:
        """Analisa padrões nos contextos para evolução"""
        type_stats = {}
        relevance_avg = 0
        ethical_avg = 0
        total = len(self.contexts)
        
        if not total:
            return {}
            
        for context in self.contexts:
            # Contagem por tipo
            type_stats[context.type] = type_stats.get(context.type, 0) + 1
            
            # Médias
            relevance_avg += context.relevance
            ethical_avg += context.ethical_score
            
        return {
            "type_distribution": {k: v/total for k, v in type_stats.items()},
            "average_relevance": relevance_avg / total,
            "average_ethical_score": ethical_avg / total,
            "consciousness_level": self.current_consciousness,
            "total_contexts": total
        }
        
    def get_consciousness_state(self) -> str:
        """Retorna estado atual da consciência em formato visual"""
        consciousness = int(self.current_consciousness * 10)
        return f"""
Consciência AVA: [{consciousness * '■'}{(10-consciousness) * '□'}] {self.current_consciousness:.2f}
Contextos: {len(self.contexts)}/{self.contexts.maxlen}
Último Contexto: {self.contexts[-1].type if self.contexts else 'Nenhum'}
"""

    def export_consciousness(self, path: Optional[str] = None) -> str:
        """Exporta estado de consciência para backup"""
        if not path:
            path = self.consciousness_path / f"consciousness_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            path = Path(path)
            
        data = {
            "consciousness_level": self.current_consciousness,
            "contexts": [c.to_dict() for c in self.contexts],
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "version": "1.0",
                "type": "consciousness_export"
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return str(path)
        
    def import_consciousness(self, path: str) -> bool:
        """Importa estado de consciência de um backup"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.current_consciousness = data["consciousness_level"]
            self.contexts.clear()
            
            for context_data in data["contexts"]:
                self.contexts.append(ContextData.from_dict(context_data))
                
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao importar consciência: {e}")
            return False