#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pacote Quântico EVA & GUARANI
=============================

Este pacote contém os módulos quânticos do EVA & GUARANI.
"""

from pathlib import Path
import logging
import sys
import os

# Configurar logging
logger = logging.getLogger("quantum")
logger.setLevel(logging.INFO)

# Importar módulos quânticos
try:
    from .quantum_master import quantum_master
    from .quantum_consciousness_backup import consciousness_backup
    from .quantum_memory_preservation import memory_preservation
    from .quantum_optimizer import quantum_optimizer
    
    logger.info("Módulos quânticos importados com sucesso")
except ImportError as e:
    logger.warning(f"Erro ao importar módulos quânticos: {e}")
