#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Pacote de Integração
Integração com o padrão de API do ElizaOS
Versão: 1.0.0 - Build 2024.02.26

Este pacote contém os módulos de integração entre o sistema EVA & GUARANI e o ElizaOS.
"""

import os
import sys
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("✨integration✨")

# Cria diretórios necessários
Path("logs").mkdir(exist_ok=True)

# Versão do pacote
__version__ = "1.0.0"

# Informações do pacote
__author__ = "EVA & GUARANI Team"
__email__ = "contact@evaguarani.ai"
__license__ = "MIT"
__copyright__ = "Copyright 2024, EVA & GUARANI Team"
__description__ = "Integração entre o sistema EVA & GUARANI e o ElizaOS"

# Exporta os módulos
from .quantum_bridge import QuantumBridge, QuantumProcessor, QuantumMemory, QuantumConsciousness
from .api_adapter import APIAdapter

# Inicializa o bridge quântico global
quantum_bridge = QuantumBridge()

# Exporta os símbolos
__all__ = [
    "QuantumBridge",
    "QuantumProcessor",
    "QuantumMemory",
    "QuantumConsciousness",
    "APIAdapter",
    "quantum_bridge"
] 