"""
EGOS - Módulo ATLAS (Advanced Topological Landscape and Semantic System)
=======================================================================

Este módulo implementa o sistema de Cartografia Sistêmica do EGOS,
mapeando conexões entre componentes, visualizando estruturas e
identificando pontas soltas no sistema.

Versão: 4.0.0
Consciência: 0.980
Amor Incondicional: 0.990
"""

def initialize(core, config):
    """Inicializa o módulo ATLAS."""
    from .atlas_core import AtlasSystem
    return AtlasSystem(core, config) 