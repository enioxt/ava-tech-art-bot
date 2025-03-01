#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Pacote Principal
Integração com o padrão de API do ElizaOS
Versão: 1.0.0 - Build 2024.02.26

Este pacote contém os módulos do sistema EVA & GUARANI.
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
        logging.FileHandler("logs/modules.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("✨modules✨")

# Cria diretórios necessários
Path("logs").mkdir(exist_ok=True)

# Versão do pacote
__version__ = "1.0.0"

# Informações do pacote
__author__ = "EVA & GUARANI Team"
__email__ = "contact@evaguarani.ai"
__license__ = "MIT"
__copyright__ = "Copyright 2024, EVA & GUARANI Team"
__description__ = "Sistema EVA & GUARANI"

# Exporta os módulos
from . import integration

# Exporta os símbolos
__all__ = [
    "integration"
] 