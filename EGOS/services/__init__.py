"""
Pacote de Serviços Externos - EVA & GUARANI
-------------------------------------------
Este pacote contém módulos para interação com serviços e APIs externas,
incluindo gerenciamento de configuração e integração com provedores de IA.
"""

from .config import config_manager
from .perplexity_service import PerplexityService

__all__ = ['config_manager', 'PerplexityService'] 