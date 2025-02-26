"""
EVA - Sistema Orgânico de IA
Integrador do Core com Interface Elegante
"""

import logging
import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional
from infinity_ai.core.bot_core import EVACore
from infinity_ai.interface import EVAInterface
from rich.logging import RichHandler
from infinity_ai.tools.system_restore import SystemRestore

# Configuração de logging com rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True),
        logging.FileHandler("eva.log")
    ]
)

logger = logging.getLogger("EVA.Main")

class EVASystem:
    def __init__(self):
        self.interface: Optional[EVAInterface] = None
        self.bot: Optional[EVACore] = None
        self.running = True
        self.restore = SystemRestore()
        
    def setup_signal_handlers(self):
        """Configura handlers para sinais do sistema"""
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)
            
    def _signal_handler(self, signum, frame):
        """Handler para sinais de término"""
        logger.info(f"Sinal recebido: {signal.Signals(signum).name}")
        self.running = False
        
    async def graceful_shutdown(self):
        """Realiza shutdown controlado do sistema"""
        logger.info("Iniciando shutdown controlado...")
        
        # Salva estado atual
        if self.bot:
            await self.bot.save_state()
            
        # Backup final
        self.restore.backup()
        
        # Fecha interface
        if self.interface:
            self.interface.show_footer("Encerrando sistema...")
            self.interface.update()
            await self.interface.close()
            
        logger.info("Sistema encerrado com sucesso")
        
    async def startup(self):
        """Inicializa componentes do sistema"""
        try:
            # Verifica diretórios
            for dir_path in ["logs", "data", "backups"]:
                Path(dir_path).mkdir(exist_ok=True)
                
            # Interface
            self.interface = EVAInterface()
            self.interface.show_header("EVA System")
            self.interface.show_menu([
                "Status",
                "Monitor", 
                "Logs",
                "Config",
                "Exit"
            ])
            self.interface.show_footer("Iniciando sistema...")
            self.interface.update()
            
            # Core do bot
            self.bot = EVACore()
            await self.bot.load_state()
            
            logger.info("Sistema inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            return False
            
    async def run(self):
        """Loop principal do sistema"""
        try:
            # Inicialização
            if not await self.startup():
                return
                
            # Loop principal
            while self.running:
                try:
                    # Executa interface e bot
                    await asyncio.gather(
                        self.interface.run(),
                        self.bot.run()
                    )
                except Exception as e:
                    logger.error(f"Erro no loop principal: {e}")
                    if not await self.handle_error(e):
                        break
                        
            # Shutdown controlado
            await self.graceful_shutdown()
            
        except Exception as e:
            logger.critical(f"Erro fatal: {e}")
            raise
            
    async def handle_error(self, error: Exception) -> bool:
        """
        Trata erros do sistema
        Retorna True se deve continuar executando, False para encerrar
        """
        try:
            # Tenta restaurar último backup
            logger.info("Tentando restaurar último backup...")
            if self.restore.restore_system():
                logger.info("Sistema restaurado com sucesso")
                return True
                
            logger.error("Falha na restauração do sistema")
            return False
            
        except Exception as e:
            logger.critical(f"Erro ao tratar erro: {e}")
            return False

async def main():
    """Ponto de entrada principal"""
    system = EVASystem()
    system.setup_signal_handlers()
    await system.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Sistema encerrado pelo usuário")
    except Exception as e:
        logger.critical(f"Erro fatal: {e}")
        sys.exit(1)
