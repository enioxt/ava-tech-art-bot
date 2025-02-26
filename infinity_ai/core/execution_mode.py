"""
Sistema de Gerenciamento de Modo de Execução
Controla como os comandos devem ser executados (terminal integrado vs externo)
"""

from enum import Enum
from typing import Optional
from pathlib import Path
import json

class ExecutionMode(Enum):
    INTEGRATED = "integrated"  # Usa terminal integrado do Cursor
    EXTERNAL = "external"      # Usa PowerShell externo
    AUTO = "auto"             # Decide automaticamente

class ExecutionManager:
    def __init__(self):
        self.mode = ExecutionMode.INTEGRATED
        self.config_file = Path("config/execution_mode.json")
        self.load_config()
        
    def load_config(self):
        """Carrega configuração do arquivo"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                self.mode = ExecutionMode(config.get("mode", "integrated"))
            except Exception:
                self.mode = ExecutionMode.INTEGRATED
                
    def save_config(self):
        """Salva configuração no arquivo"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump({"mode": self.mode.value}, f, indent=2)
            
    def set_mode(self, mode: str) -> bool:
        """Define o modo de execução"""
        try:
            self.mode = ExecutionMode(mode.lower())
            self.save_config()
            return True
        except ValueError:
            return False
            
    def get_mode(self) -> str:
        """Retorna o modo atual"""
        return self.mode.value
        
    def format_command(self, command: str) -> str:
        """Formata comando de acordo com o modo"""
        if self.mode == ExecutionMode.EXTERNAL:
            # Para PowerShell externo
            return f"PowerShell: {command}"
        else:
            # Para terminal integrado
            return command
            
    def should_execute_integrated(self) -> bool:
        """Verifica se deve executar no terminal integrado"""
        return self.mode == ExecutionMode.INTEGRATED

# Instância global
execution_manager = ExecutionManager()