"""
Módulos do Sistema EVA & GUARANI
--------------------------------
Este pacote contém os principais módulos funcionais do sistema quântico
EVA & GUARANI, incluindo interfaces para serviços externos e 
funcionalidades especializadas.
"""

# Importar módulos principais
from .perplexity_integration import PerplexityIntegration
from .quantum_tools import QuantumTools

# Definir a interface pública
__all__ = ["PerplexityIntegration", "QuantumTools"]