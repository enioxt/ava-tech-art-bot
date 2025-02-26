"""
EVA & GUARANI - Sistema Principal
"""

import os
import sys
import asyncio
import signal
from pathlib import Path
from typing import Optional

# Adiciona src ao PYTHONPATH
src_dir = str(Path(__file__).parent.parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from infinity_os.core.config import ConfigManager
from infinity_os.core.interface_manager import interface

class BotRunner:
    def __init__(self):
        """Inicializa o runner do bot"""
        self._shutdown_event = None
        self._config_manager = ConfigManager()
        
    async def start(self, config_path: str) -> None:
        """Inicia o bot com barra de progresso"""
        try:
            # Mostra mensagem inicial
            interface.show_status("🚀 Iniciando EVA & GUARANI")
            
            # Cria barra de progresso
            with interface.create_progress() as progress:
                # Adiciona tarefas
                init_task = progress.add_task("Inicializando...", total=100)
                
                # Carrega configuração
                progress.update(init_task, advance=20, description="Carregando configuração...")
                await self._config_manager.initialize()
                
                # Configura eventos
                progress.update(init_task, advance=20, description="Configurando eventos...")
                self._shutdown_event = asyncio.Event()
                signal.signal(signal.SIGINT, self.handle_shutdown)
                signal.signal(signal.SIGTERM, self.handle_shutdown)
                
                # Inicializa sistemas
                progress.update(init_task, advance=30, description="Inicializando sistemas...")
                # TODO: Adicionar inicialização de outros sistemas
                
                # Finaliza inicialização
                progress.update(init_task, advance=30, description="Concluindo...")
                await asyncio.sleep(1)  # Pausa para visualização
                
            # Mostra mensagem de sucesso
            interface.show_success("Sistema iniciado com sucesso!")
            
            # Aguarda sinal de desligamento
            await self._shutdown_event.wait()
            
        except Exception as e:
            interface.show_error(str(e))
            raise
            
    def handle_shutdown(self, signum, frame):
        """Manipula sinal de desligamento"""
        if self._shutdown_event:
            interface.show_status("🛑 Desligando sistema...", style="warning")
            self._shutdown_event.set()

def setup_environment() -> None:
    """Configura o ambiente"""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def run_bot(config_path: str) -> None:
    """Executa o bot"""
    runner = BotRunner()
    try:
        asyncio.run(runner.start(config_path))
    except KeyboardInterrupt:
        interface.show_status("Sistema interrompido pelo usuário", style="warning")
    except Exception as e:
        interface.show_error(f"Erro fatal: {e}")
        sys.exit(1)

def main() -> None:
    """Função principal"""
    setup_environment()
    config_path = os.getenv("CONFIG_PATH", "config/system.json")
    run_bot(config_path)

if __name__ == "__main__":
    main()