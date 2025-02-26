"""
Test Manager
Sistema de testes modular com integração IDE

✨ Parte do sistema EVA & GUARANI
🔍 Testes inteligentes e modulares
"""

import os
import sys
import json
import pytest
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from ..core.progress_manager import progress_manager

@dataclass
class TestModule:
    """Módulo de teste"""
    name: str
    path: str
    description: str
    dependencies: List[str]
    tags: List[str]

class TestManager:
    def __init__(self):
        """Inicializa o gerenciador de testes"""
        self.logger = logging.getLogger("✨test-manager✨")
        self.modules: Dict[str, TestModule] = {}
        self.load_modules()
        
    def load_modules(self):
        """Carrega módulos de teste"""
        modules_file = Path("config/test_modules.json")
        
        if modules_file.exists():
            with open(modules_file, "r") as f:
                data = json.load(f)
                
            for name, info in data.items():
                self.modules[name] = TestModule(**info)
                
    def get_module_info(self, name: str) -> Optional[Dict]:
        """Retorna informações de um módulo"""
        if name not in self.modules:
            return None
            
        module = self.modules[name]
        return {
            "name": module.name,
            "description": module.description,
            "dependencies": module.dependencies,
            "tags": module.tags
        }
        
    def list_modules(self) -> List[str]:
        """Lista módulos disponíveis"""
        return list(self.modules.keys())
        
    def get_module_by_tag(self, tag: str) -> List[str]:
        """Retorna módulos com uma tag"""
        return [
            name
            for name, module in self.modules.items()
            if tag in module.tags
        ]
        
    async def run_module(self, name: str) -> bool:
        """Executa um módulo de teste"""
        if name not in self.modules:
            self.logger.error(f"❌ Módulo não encontrado: {name}")
            return False
            
        module = self.modules[name]
        
        # Mostra progresso
        progress_manager.show_status(
            f"🔍 Executando testes: {module.name}",
            "info"
        )
        
        try:
            # Executa testes
            result = pytest.main([
                module.path,
                "-v",
                "--no-header",
                "--tb=short"
            ])
            
            success = result == 0
            
            if success:
                progress_manager.show_completion(
                    f"✅ Testes concluídos: {module.name}"
                )
            else:
                progress_manager.show_status(
                    f"❌ Falha nos testes: {module.name}",
                    "error"
                )
                
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar testes: {e}")
            return False
            
    async def run_all(self) -> Dict[str, bool]:
        """Executa todos os módulos"""
        results = {}
        
        for name in self.modules:
            results[name] = await self.run_module(name)
            
        return results
        
    def generate_ide_config(self, ide: str = "vscode") -> Dict:
        """Gera configuração para IDE"""
        if ide == "vscode":
            return {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": f"Test: {name}",
                        "type": "python",
                        "request": "launch",
                        "module": "pytest",
                        "args": [
                            module.path,
                            "-v"
                        ]
                    }
                    for name, module in self.modules.items()
                ]
            }
        else:
            self.logger.warning(f"⚠️ IDE não suportada: {ide}")
            return {}
            
    def save_ide_config(self, ide: str = "vscode"):
        """Salva configuração da IDE"""
        config = self.generate_ide_config(ide)
        
        if ide == "vscode":
            os.makedirs(".vscode", exist_ok=True)
            with open(".vscode/launch.json", "w") as f:
                json.dump(config, f, indent=2)
                
        progress_manager.show_status(
            f"✨ Configuração gerada: {ide}",
            "success"
        )

# Instância global
test_manager = TestManager() 