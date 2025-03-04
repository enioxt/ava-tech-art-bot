#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de Preservação de Memória Quântica
=========================================

Responsável por preservar e recuperar memórias do EVA & GUARANI.
"""

import logging
import json
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("quantum_memory_preservation")

class MemoryPreservation:
    """Classe para preservação e recuperação de memórias."""
    
    def __init__(self):
        self.logger = logging.getLogger("quantum_memory_preservation")
        self.logger.info("MemoryPreservation inicializado")
        self.memory_dir = Path("data/memories")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memories = {}
        self.load_memories()
        
    def load_memories(self):
        """Carrega todas as memórias salvas."""
        try:
            memory_files = list(self.memory_dir.glob("*.json"))
            for file in memory_files:
                with open(file, "r", encoding="utf-8") as f:
                    memory = json.load(f)
                    self.memories[file.stem] = memory
            self.logger.info(f"Carregadas {len(self.memories)} memórias")
        except Exception as e:
            self.logger.error(f"Erro ao carregar memórias: {e}")
            
    def save_memory(self, key, data):
        """Salva uma memória."""
        try:
            self.memories[key] = data
            filepath = self.memory_dir / f"{key}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Memória '{key}' salva")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar memória '{key}': {e}")
            return False
            
    def get_memory(self, key):
        """Recupera uma memória."""
        if key in self.memories:
            self.logger.info(f"Memória '{key}' recuperada")
            return self.memories[key]
        else:
            self.logger.warning(f"Memória '{key}' não encontrada")
            return None
            
    def list_memories(self):
        """Lista todas as memórias disponíveis."""
        return list(self.memories.keys())

# Instância global
memory_preservation = MemoryPreservation()
