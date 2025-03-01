#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Pacote de Modelos de IA
Adaptado do framework ElizaOS
Versão: 1.0.0 - Build 2024.02.26

Este pacote contém os adaptadores para diferentes modelos de IA.
"""

# Importa os modelos
from .openai import OpenAIModel
from .anthropic import AnthropicModel
from .gemini import GeminiModel

# Exporta os símbolos
__all__ = [
    "OpenAIModel",
    "AnthropicModel",
    "GeminiModel"
]

# Versão do pacote
__version__ = "1.0.0" 