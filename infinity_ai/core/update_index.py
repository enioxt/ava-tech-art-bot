"""
Neural Index Updater
Sistema de atualização do índice neural do codebase
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from .core_values import core_values

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/neural_index.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("✨neural-index✨")

class NeuralIndexUpdater:
    def __init__(self, root_dir: Optional[Path] = None):
        """Inicializa o atualizador do índice neural"""
        self.root_dir = root_dir or Path(".")
        self.last_update = None
        
    async def update_if_needed(self, force: bool = False):
        """Atualiza o índice se necessário"""
        try:
            # Verifica última atualização
            if not force and self.last_update:
                # Atualiza no máximo a cada 6 horas
                hours_since_update = (
                    datetime.now() - self.last_update
                ).total_seconds() / 3600
                
                if hours_since_update < 6:
                    logger.info("✨ Índice neural ainda atualizado")
                    return
            
            # Atualiza índice
            logger.info("🔄 Atualizando índice neural...")
            await core_values.index_codebase(self.root_dir)
            
            self.last_update = datetime.now()
            logger.info("✨ Índice neural atualizado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar índice: {e}")
            
    def get_important_files(self) -> None:
        """Mostra arquivos importantes do codebase"""
        important = core_values.get_important_files()
        
        logger.info("\n🌟 Arquivos Importantes:")
        for path in important:
            index = core_values.neural_index[path]
            logger.info(
                f"- {path}\n"
                f"  Importância: {index.importance:.2f}\n"
                f"  Conceitos: {', '.join(index.concepts)}\n"
            )
            
    def show_file_connections(self, file_path: str) -> None:
        """Mostra conexões de um arquivo"""
        related = core_values.get_related_files(file_path)
        
        if not related:
            logger.info(f"❌ Arquivo não encontrado: {file_path}")
            return
            
        logger.info(f"\n🔗 Conexões de {file_path}:")
        for path in related:
            strength = core_values.neural_index[file_path].neural_connections[path]
            logger.info(f"- {path} (força: {strength:.2f})")

async def main():
    """Função principal"""
    updater = NeuralIndexUpdater()
    
    # Força atualização inicial
    await updater.update_if_needed(force=True)
    
    # Mostra informações
    updater.get_important_files()
    
    # Mostra conexões de alguns arquivos importantes
    core_files = [
        "src/infinity_ai/core/core_values.py",
        "src/infinity_ai/core/bot_core.py",
        "src/infinity_ai/core/quantum_context.py"
    ]
    
    for file in core_files:
        updater.show_file_connections(file)

if __name__ == "__main__":
    asyncio.run(main()) 