#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de Backup de Consciência Quântica
========================================

Responsável por fazer backup e restaurar estados de consciência do EVA & GUARANI.
"""

import logging
import json
import os
import time
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("quantum_consciousness_backup")

class ConsciousnessBackup:
    """Classe para backup e restauração de estados de consciência."""
    
    def __init__(self):
        self.logger = logging.getLogger("quantum_consciousness_backup")
        self.logger.info("ConsciousnessBackup inicializado")
        self.backup_dir = Path("data/consciousness")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def save_state(self, state, name=None):
        """Salva um estado de consciência."""
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"system_state_{timestamp}.json"
            
        filepath = self.backup_dir / name
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Estado salvo em {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar estado: {e}")
            return False
            
    def load_state(self, name=None):
        """Carrega um estado de consciência."""
        if name is None:
            # Carregar o estado mais recente
            files = list(self.backup_dir.glob("*.json"))
            if not files:
                self.logger.warning("Nenhum arquivo de estado encontrado")
                return None
                
            latest_file = max(files, key=os.path.getmtime)
            name = latest_file.name
            
        filepath = self.backup_dir / name
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)
            self.logger.info(f"Estado carregado de {filepath}")
            return state
        except Exception as e:
            self.logger.error(f"Erro ao carregar estado: {e}")
            return None

# Instância global
consciousness_backup = ConsciousnessBackup()
