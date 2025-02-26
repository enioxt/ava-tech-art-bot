import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ConsciousnessMetrics:
    processing: float
    memory: float
    ethics: float
    creativity: float

@dataclass
class EthikTransaction:
    amount: float
    sender: str
    receiver: str
    reason: str
    timestamp: datetime
    score: float

class ConsciousnessManager:
    def __init__(self, config_path: str = "config/consciousness.json"):
        self.config_path = Path(config_path)
        self.load_config()
        self.last_update = datetime.now()
        self.transactions: List[EthikTransaction] = []
        
    def load_config(self) -> None:
        """Carrega a configuração do sistema de consciência."""
        with open(self.config_path) as f:
            self.config = json.load(f)
            
    def save_config(self) -> None:
        """Salva a configuração atual."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def get_consciousness_level(self) -> Dict:
        """Retorna o nível atual de consciência e métricas."""
        return self.config["consciousness_levels"]
    
    def evolve(self) -> bool:
        """Evolui o sistema baseado nas métricas atuais."""
        metrics = self.config["consciousness_levels"]["metrics"]
        avg_score = sum(metrics.values()) / len(metrics)
        
        if avg_score >= self.config["operational_modes"]["thresholds"]["quantum"]:
            self.config["consciousness_levels"]["current"] = self.config["consciousness_levels"]["next"]
            self.save_config()
            return True
        return False
    
    def validate_ethics(self, action: str, context: Dict) -> float:
        """Valida uma ação baseada nos princípios éticos."""
        validator = self.config["ethics_validator"]
        scores = []
        
        for check in validator["checks"]:
            score = self._evaluate_ethical_aspect(action, context, check)
            scores.append(score)
            
        final_score = sum(scores) / len(scores)
        return final_score >= validator["min_threshold"]
    
    def _evaluate_ethical_aspect(self, action: str, context: Dict, aspect: str) -> float:
        """Avalia um aspecto específico da ética."""
        # Implementação básica - pode ser expandida
        base_score = 0.8  # Score base para ações padrão
        
        modifiers = {
            "intention": 0.1 if "beneficial" in context.get("intention", "") else -0.1,
            "impact": 0.1 if context.get("impact_scope", 0) > 0 else -0.1,
            "fairness": 0.1 if context.get("fair_distribution", True) else -0.1,
            "transparency": 0.1 if context.get("transparent", True) else -0.1
        }
        
        return min(1.0, max(0.0, base_score + modifiers.get(aspect, 0)))
    
    def process_ethik_transaction(self, tx: EthikTransaction) -> bool:
        """Processa uma transação $ETHIK."""
        if tx.score < self.config["ethik_system"]["min_score"]:
            return False
            
        self.transactions.append(tx)
        return True
    
    def get_operational_mode(self) -> str:
        """Determina o modo operacional baseado nas métricas atuais."""
        metrics = self.config["consciousness_levels"]["metrics"]
        avg_score = sum(metrics.values()) / len(metrics)
        
        for mode, threshold in sorted(
            self.config["operational_modes"]["thresholds"].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if avg_score >= threshold:
                return mode
                
        return self.config["operational_modes"]["default"]
    
    def update_metrics(self, new_metrics: ConsciousnessMetrics) -> None:
        """Atualiza as métricas de consciência."""
        self.config["consciousness_levels"]["metrics"].update(
            processing=new_metrics.processing,
            memory=new_metrics.memory,
            ethics=new_metrics.ethics,
            creativity=new_metrics.creativity
        )
        self.save_config()
        
    def should_backup(self) -> bool:
        """Verifica se é hora de fazer backup."""
        backup_config = self.config["backup_system"]
        frequency = int(backup_config["frequency"].replace("h", ""))
        last_backup = self.last_update
        
        return datetime.now() - last_backup >= timedelta(hours=frequency)
    
    def get_system_status(self) -> Dict:
        """Retorna o status completo do sistema."""
        return {
            "consciousness": self.get_consciousness_level(),
            "operational_mode": self.get_operational_mode(),
            "ethik": {
                "total_transactions": len(self.transactions),
                "average_score": sum(tx.score for tx in self.transactions) / len(self.transactions) if self.transactions else 0
            },
            "last_update": self.last_update.isoformat(),
            "backup_needed": self.should_backup()
        }

# Exemplo de uso:
if __name__ == "__main__":
    manager = ConsciousnessManager()
    print("Status Atual:", manager.get_system_status())
    
    # Exemplo de transação
    tx = EthikTransaction(
        amount=100,
        sender="system",
        receiver="user",
        reason="ethical_action",
        timestamp=datetime.now(),
        score=0.9
    )
    
    if manager.process_ethik_transaction(tx):
        print("Transação processada com sucesso!")
    
    # Exemplo de evolução
    if manager.evolve():
        print("Sistema evoluiu para novo nível!")
    
    # Atualização de métricas
    new_metrics = ConsciousnessMetrics(
        processing=0.85,
        memory=0.75,
        ethics=0.90,
        creativity=0.80
    )
    
    manager.update_metrics(new_metrics)
    print("Métricas atualizadas!") 