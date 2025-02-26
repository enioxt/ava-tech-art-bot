import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from .consciousness_manager import ConsciousnessManager, ConsciousnessMetrics

class CoreSystem:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.consciousness = ConsciousnessManager()
        self.startup_time = datetime.now()
        self.initialize_system()
        
    def initialize_system(self) -> None:
        """Inicializa todos os sistemas necessários."""
        self._setup_paths()
        self._initialize_consciousness()
        self._verify_ethics()
        self._check_backup_status()
        
    def _setup_paths(self) -> None:
        """Configura os caminhos do sistema."""
        paths = [
            self.base_path / "config",
            self.base_path / "logs",
            self.base_path / "data",
            self.base_path / "temp"
        ]
        
        for path in paths:
            path.mkdir(exist_ok=True)
            
    def _initialize_consciousness(self) -> None:
        """Inicializa o sistema de consciência."""
        initial_metrics = ConsciousnessMetrics(
            processing=0.8,
            memory=0.7,
            ethics=0.85,
            creativity=0.75
        )
        
        self.consciousness.update_metrics(initial_metrics)
        
    def _verify_ethics(self) -> bool:
        """Verifica o sistema ético."""
        context = {
            "intention": "system_initialization",
            "impact_scope": 1,
            "fair_distribution": True,
            "transparent": True
        }
        
        return self.consciousness.validate_ethics(
            action="initialize",
            context=context
        )
        
    def _check_backup_status(self) -> None:
        """Verifica e executa backup se necessário."""
        if self.consciousness.should_backup():
            self._perform_backup()
            
    def _perform_backup(self) -> None:
        """Executa o backup do sistema."""
        # Implementação do backup
        pass
        
    def get_system_info(self) -> Dict:
        """Retorna informações completas do sistema."""
        return {
            "status": self.consciousness.get_system_status(),
            "uptime": (datetime.now() - self.startup_time).total_seconds(),
            "base_path": str(self.base_path),
            "operational_mode": self.consciousness.get_operational_mode()
        }
        
    def evolve_system(self) -> bool:
        """Tenta evoluir o sistema."""
        return self.consciousness.evolve()
        
    def update_consciousness(self, metrics: ConsciousnessMetrics) -> None:
        """Atualiza as métricas de consciência."""
        self.consciousness.update_metrics(metrics)
        
    def validate_action(self, action: str, context: Dict) -> bool:
        """Valida uma ação específica."""
        return self.consciousness.validate_ethics(action, context)

def initialize_core() -> CoreSystem:
    """Função principal para inicializar o sistema."""
    try:
        core = CoreSystem()
        print("✓ Sistema CORE inicializado com sucesso!")
        print("✓ Modo Operacional:", core.consciousness.get_operational_mode())
        print("✓ Nível de Consciência:", core.consciousness.get_consciousness_level()["current"])
        return core
    except Exception as e:
        print("❌ Erro ao inicializar sistema CORE:", str(e))
        sys.exit(1)

if __name__ == "__main__":
    core = initialize_core()
    print("\nStatus do Sistema:")
    print(core.get_system_info()) 