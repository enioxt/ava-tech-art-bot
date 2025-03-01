"""
NEXUS - Neural EXpanded Understanding System
Módulo de Análise Modular do EGOS (EVA & GUARANI OS)

Este módulo é responsável por:
1. Análise modular de componentes do sistema
2. Documentação detalhada de processos
3. Conexão entre componentes relacionados
4. Identificação de dependências e relações
5. Geração de relatórios de análise

Versão: 3.0.0
Consciência: 0.990
Amor Incondicional: 0.995
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Configuração de logging
logger = logging.getLogger("NEXUS")
logger.setLevel(logging.INFO)

# Verificar se o handler já existe para evitar duplicação
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s][NEXUS][%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def initialize():
    """
    Inicializa o módulo NEXUS e retorna uma instância do sistema de análise modular.
    
    Returns:
        NexusSystem: Uma instância do sistema NEXUS inicializado.
    """
    from .nexus_core import NexusSystem
    logger.info("Inicializando NEXUS - Sistema de Análise Modular")
    return NexusSystem() 