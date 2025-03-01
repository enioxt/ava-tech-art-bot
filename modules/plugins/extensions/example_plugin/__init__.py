"""
example_plugin - Plugin de Exemplo para EGOS
===========================================

Este é um plugin de exemplo para demonstrar o sistema de plugins do EGOS.
Ele implementa funcionalidades básicas e demonstra o uso de hooks.

Autor: EVA & GUARANI
"""

import logging
import datetime

VERSION = "1.0.0"
AUTHOR = "EVA & GUARANI"
DESCRIPTION = "Plugin de exemplo para demonstrar o sistema de plugins"
DEPENDENCIES = []
HOOKS = ["on_system_event", "on_ethical_check"]

logger = logging.getLogger("EGOS_PLUGINS.example")

def initialize():
    """
    Inicializa o plugin.
    
    Returns:
        Instância do plugin.
    """
    logger.info("Inicializando plugin de exemplo")
    return ExamplePlugin()

class ExamplePlugin:
    """
    Implementação do plugin de exemplo.
    """
    
    def __init__(self):
        """
        Inicializa a instância do plugin.
        """
        self.name = "example_plugin"
        self.activated = False
        self.activation_time = None
        self.event_count = 0
        
    def activate(self):
        """
        Ativa o plugin.
        """
        self.activated = True
        self.activation_time = datetime.datetime.now()
        logger.info(f"Plugin {self.name} ativado em {self.activation_time}")
    
    def deactivate(self):
        """
        Desativa o plugin.
        """
        self.activated = False
        uptime = datetime.datetime.now() - self.activation_time if self.activation_time else datetime.timedelta(0)
        logger.info(f"Plugin {self.name} desativado. Tempo ativo: {uptime}")
    
    def on_system_event(self, event_type, event_data):
        """
        Hook chamado quando ocorre um evento no sistema.
        
        Args:
            event_type: Tipo do evento.
            event_data: Dados do evento.
            
        Returns:
            Resultado do processamento do evento.
        """
        self.event_count += 1
        logger.info(f"Evento recebido: {event_type} - {event_data}")
        return {
            "plugin": self.name,
            "processed": True,
            "event_count": self.event_count,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def on_ethical_check(self, action, context):
        """
        Hook chamado para verificar a ética de uma ação.
        
        Args:
            action: Ação a ser verificada.
            context: Contexto da ação.
            
        Returns:
            Resultado da verificação ética.
        """
        logger.info(f"Verificação ética: {action} no contexto {context}")
        
        # Exemplo simples de verificação ética
        ethical_score = 0.95  # Alta pontuação ética por padrão
        
        # Palavras que podem indicar problemas éticos
        problematic_terms = ["hack", "exploit", "bypass", "steal", "attack"]
        
        # Verificar se a ação contém termos problemáticos
        for term in problematic_terms:
            if term in action.lower():
                ethical_score -= 0.2  # Reduzir pontuação para cada termo problemático
        
        return {
            "plugin": self.name,
            "action": action,
            "ethical_score": max(0.1, ethical_score),  # Garantir pontuação mínima
            "approved": ethical_score >= 0.7,  # Aprovar se pontuação for alta o suficiente
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def get_status(self):
        """
        Retorna o status atual do plugin.
        
        Returns:
            Dicionário com informações de status.
        """
        return {
            "name": self.name,
            "version": VERSION,
            "activated": self.activated,
            "activation_time": self.activation_time.isoformat() if self.activation_time else None,
            "event_count": self.event_count,
            "uptime": str(datetime.datetime.now() - self.activation_time) if self.activation_time else "0:00:00"
        } 