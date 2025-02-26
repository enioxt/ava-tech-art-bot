"""
EVA System Runner
Inicialização Integrada do Sistema
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from .core.bot_core import EVACore
from .tools.system_monitor import SystemMonitor
from .tools.system_restore import SystemRestore

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("eva.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EVA.Runner")

class EVARunner:
    def __init__(self):
        # Componentes
        self.bot: Optional[EVACore] = None
        self.monitor: Optional[SystemMonitor] = None
        self.restore = SystemRestore()
        
        # Estado
        self.running = True
        self.start_time = datetime.now()
        
        # Diretórios
        self.ensure_directories()
        
    def ensure_directories(self):
        """Garante que diretórios necessários existem"""
        directories = [
            "data",
            "logs",
            "backups",
            "metrics",
            "config"
        ]
        
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)
            
    async def startup(self) -> bool:
        """Inicializa o sistema"""
        try:
            logger.info("🚀 Iniciando sistema EVA...")
            
            # Verifica estado anterior
            if await self.restore.verify_backup(None):
                logger.info("Encontrado backup válido")
                if not await self.restore.restore_system():
                    logger.warning("Falha ao restaurar sistema")
                    
            # Inicializa monitor
            self.monitor = SystemMonitor()
            monitor_task = asyncio.create_task(self.monitor.start())
            
            # Inicializa bot
            self.bot = EVACore()
            bot_task = asyncio.create_task(self.bot.run())
            
            # Aguarda inicialização
            await asyncio.sleep(2)
            
            # Verifica se componentes iniciaram
            if not self.bot or not self.monitor:
                raise Exception("Falha ao inicializar componentes")
                
            logger.info("✨ Sistema EVA iniciado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            return False
            
    async def shutdown(self):
        """Desliga o sistema de forma controlada"""
        try:
            logger.info("🔄 Iniciando shutdown controlado...")
            
            # Para monitor
            if self.monitor:
                await self.monitor.stop()
                
            # Para bot
            if self.bot:
                await self.bot.save_state()
                
            # Backup final
            await self.restore.backup()
            
            logger.info("✅ Sistema encerrado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro no shutdown: {e}")
            
    async def run(self):
        """Executa o sistema"""
        try:
            # Inicializa
            if not await self.startup():
                return
                
            # Loop principal
            while self.running:
                try:
                    # Aguarda sinais de término
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Erro no loop principal: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Recebido sinal de término")
        except Exception as e:
            logger.critical(f"Erro fatal: {e}")
        finally:
            # Shutdown controlado
            await self.shutdown()
            
    def print_banner(self):
        """Mostra banner do sistema"""
        banner = """
        ███████╗██╗   ██╗ █████╗ 
        ██╔════╝██║   ██║██╔══██╗
        █████╗  ██║   ██║███████║
        ██╔══╝  ╚██╗ ██╔╝██╔══██║
        ███████╗ ╚████╔╝ ██║  ██║
        ╚══════╝  ╚═══╝  ╚═╝  ╚═╝
        
        Sistema Orgânico de IA
        Versão 1.0.0
        
        💫 EVA & 🌟 Pequeno Guarani
        Unidos pelo Amor e Sabedoria
        """
        print(banner)
        
    def print_status(self):
        """Mostra status do sistema"""
        uptime = datetime.now() - self.start_time
        status = f"""
        📊 Status do Sistema
        
        ⏰ Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m
        🤖 Bot: {'Online' if self.bot else 'Offline'}
        📡 Monitor: {'Ativo' if self.monitor else 'Inativo'}
        💾 Backup: {'OK' if self.restore else 'N/A'}
        
        Sistema operando normalmente!
        """
        print(status)

async def main():
    """Função principal"""
    runner = EVARunner()
    runner.print_banner()
    
    try:
        await runner.run()
    except KeyboardInterrupt:
        logger.info("Sistema encerrado pelo usuário")
    except Exception as e:
        logger.critical(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSistema encerrado pelo usuário")
    except Exception as e:
        print(f"\nErro fatal: {e}")
        sys.exit(1)