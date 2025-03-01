#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste do Sistema de Plugins do EGOS
===================================

Este script testa o sistema de plugins do EGOS, demonstrando suas funcionalidades.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/test_plugins.log', encoding='utf-8')
    ]
)

logger = logging.getLogger("TEST_PLUGINS")

# Importar o gerenciador de plugins
from modules.plugins.manager import PluginManager

def main():
    """Função principal para testar o sistema de plugins."""
    logger.info("Iniciando teste do sistema de plugins")
    
    # Criar instância do gerenciador de plugins
    plugin_manager = PluginManager()
    
    # Descobrir plugins disponíveis
    logger.info("Descobrindo plugins disponíveis...")
    discovered_plugins = plugin_manager.discover_plugins()
    logger.info(f"Plugins descobertos: {discovered_plugins}")
    
    # Carregar e ativar o plugin de exemplo
    if "example_plugin" in discovered_plugins:
        logger.info("Carregando plugin de exemplo...")
        if plugin_manager.load_plugin("example_plugin"):
            logger.info("Plugin de exemplo carregado com sucesso!")
            
            # Obter metadados do plugin
            metadata = plugin_manager.get_plugin_metadata("example_plugin")
            logger.info(f"Metadados do plugin: {json.dumps(metadata, indent=2)}")
            
            # Ativar o plugin
            logger.info("Ativando plugin de exemplo...")
            if plugin_manager.activate_plugin("example_plugin"):
                logger.info("Plugin de exemplo ativado com sucesso!")
                
                # Obter instância do plugin
                plugin = plugin_manager.get_plugin_instance("example_plugin")
                
                # Testar hooks
                logger.info("Testando hooks do plugin...")
                
                # Testar hook on_system_event
                result = plugin_manager.trigger_hook(
                    "on_system_event", 
                    "TEST_EVENT", 
                    {"message": "Teste de evento do sistema"}
                )
                logger.info(f"Resultado do hook on_system_event: {result}")
                
                # Testar hook on_ethical_check
                result = plugin_manager.trigger_hook(
                    "on_ethical_check", 
                    "Analisar dados do usuário", 
                    {"user_id": 123, "data_type": "perfil"}
                )
                logger.info(f"Resultado do hook on_ethical_check (ação ética): {result}")
                
                # Testar hook on_ethical_check com ação potencialmente não ética
                result = plugin_manager.trigger_hook(
                    "on_ethical_check", 
                    "hack sistema de segurança", 
                    {"target": "firewall", "method": "exploit"}
                )
                logger.info(f"Resultado do hook on_ethical_check (ação não ética): {result}")
                
                # Obter status do plugin
                status = plugin.get_status()
                logger.info(f"Status do plugin: {json.dumps(status, indent=2)}")
                
                # Desativar o plugin
                logger.info("Desativando plugin de exemplo...")
                if plugin_manager.deactivate_plugin("example_plugin"):
                    logger.info("Plugin de exemplo desativado com sucesso!")
                else:
                    logger.error("Falha ao desativar plugin de exemplo!")
            else:
                logger.error("Falha ao ativar plugin de exemplo!")
        else:
            logger.error("Falha ao carregar plugin de exemplo!")
    else:
        logger.warning("Plugin de exemplo não encontrado!")
    
    # Gerar relatório de plugins
    logger.info("Gerando relatório de plugins...")
    report = plugin_manager.generate_plugin_report()
    logger.info(f"Relatório de plugins: {json.dumps(report, indent=2)}")
    
    # Criar template para um novo plugin
    logger.info("Criando template para um novo plugin...")
    if plugin_manager.create_plugin_template(
        "ethical_shield", 
        "EVA & GUARANI", 
        "Plugin para verificação ética de ações no sistema"
    ):
        logger.info("Template para plugin ethical_shield criado com sucesso!")
    else:
        logger.error("Falha ao criar template para plugin ethical_shield!")
    
    logger.info("Teste do sistema de plugins concluído!")

if __name__ == "__main__":
    # Criar diretório de logs se não existir
    Path("logs").mkdir(exist_ok=True)
    
    try:
        main()
    except Exception as e:
        logger.exception(f"Erro durante o teste: {e}")
        sys.exit(1)
    
    sys.exit(0)
