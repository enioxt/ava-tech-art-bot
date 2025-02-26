"""
Sistema de Backup e Restauração EVA
Garante a integridade e segurança do sistema
"""

import os
import shutil
import logging
import json
import hashlib
from datetime import datetime
from pathlib import Path
import subprocess
import sys

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_restore.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('SystemRestore')

class SystemRestore:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path("backups") / f"system_backup_{self.timestamp}"
        self.critical_dirs = [
            "src/infinity_ai/core",
            "src/infinity_ai/ethics",
            "src/infinity_ai/consciousness",
            "src/infinity_ai/tools",
            "config",
            "docs"
        ]
        self.critical_files = [
            "src/infinity_ai/run_bot.py",
            "src/infinity_ai/interface.py",
            "src/infinity_ai/monitor.py",
            ".env",
            "requirements.txt"
        ]
        
    def create_hash(self, file_path: str) -> str:
        """Gera hash SHA256 do arquivo"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
        
    def backup(self) -> bool:
        """Realiza backup completo do sistema"""
        try:
            logger.info("Iniciando backup do sistema...")
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup de diretórios críticos
            for dir_path in self.critical_dirs:
                src_path = Path(dir_path)
                if not src_path.exists():
                    logger.warning(f"Diretório não encontrado: {dir_path}")
                    continue
                    
                dst_path = self.backup_dir / dir_path
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src_path, dst_path)
                logger.info(f"✓ Backup do diretório: {dir_path}")
                
            # Backup de arquivos críticos
            manifest = {"timestamp": self.timestamp, "files": {}}
            for file_path in self.critical_files:
                src_path = Path(file_path)
                if not src_path.exists():
                    logger.warning(f"Arquivo não encontrado: {file_path}")
                    continue
                    
                dst_path = self.backup_dir / file_path
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                manifest["files"][str(file_path)] = self.create_hash(src_path)
                logger.info(f"✓ Backup do arquivo: {file_path}")
                
            # Salva manifesto
            with open(self.backup_dir / "manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
                
            logger.info(f"✅ Backup concluído: {self.backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no backup: {e}")
            return False
            
    def verify_backup(self) -> bool:
        """Verifica integridade do backup"""
        try:
            logger.info("Verificando integridade do backup...")
            with open(self.backup_dir / "manifest.json") as f:
                manifest = json.load(f)
                
            for path, stored_hash in manifest["files"].items():
                backup_path = self.backup_dir / path
                if not backup_path.is_file():
                    logger.error(f"Arquivo não encontrado no backup: {path}")
                    return False
                    
                current_hash = self.create_hash(backup_path)
                if current_hash != stored_hash:
                    logger.error(f"Hash não corresponde para: {path}")
                    return False
                    
            logger.info("✅ Backup verificado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação: {e}")
            return False
            
    def clean_old_backups(self, max_age_days: int = 7):
        """Remove backups antigos"""
        try:
            logger.info(f"Limpando backups mais antigos que {max_age_days} dias...")
            backup_root = Path("backups")
            for backup_dir in backup_root.glob("system_backup_*"):
                if (datetime.now() - datetime.fromtimestamp(backup_dir.stat().st_mtime)).days > max_age_days:
                    shutil.rmtree(backup_dir)
                    logger.info(f"Removido backup antigo: {backup_dir}")
        except Exception as e:
            logger.error(f"Erro ao limpar backups antigos: {e}")
            
    def restore_system(self, backup_path: str = None) -> bool:
        """Restaura o sistema a partir de um backup"""
        try:
            if not backup_path:
                # Usa o backup mais recente
                backup_root = Path("backups")
                backups = list(backup_root.glob("system_backup_*"))
                if not backups:
                    logger.error("Nenhum backup encontrado")
                    return False
                backup_path = str(max(backups, key=lambda x: x.stat().st_mtime))
                
            logger.info(f"Restaurando sistema a partir de: {backup_path}")
            backup_dir = Path(backup_path)
            
            # Verifica manifesto
            if not (backup_dir / "manifest.json").exists():
                logger.error("Manifesto do backup não encontrado")
                return False
                
            # Restaura arquivos e diretórios
            for dir_path in self.critical_dirs:
                src_path = backup_dir / dir_path
                dst_path = Path(dir_path)
                if src_path.exists():
                    if dst_path.exists():
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                    logger.info(f"✓ Restaurado diretório: {dir_path}")
                    
            for file_path in self.critical_files:
                src_path = backup_dir / file_path
                dst_path = Path(file_path)
                if src_path.exists():
                    if dst_path.exists():
                        dst_path.unlink()
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    logger.info(f"✓ Restaurado arquivo: {file_path}")
                    
            logger.info("✅ Sistema restaurado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na restauração: {e}")
            return False
            
    def restart_system(self):
        """Reinicia o sistema EVA"""
        try:
            logger.info("Reiniciando sistema EVA...")
            
            # Para processos existentes
            subprocess.run(["pkill", "-f", "run_bot.py"], check=False)
            
            # Reinicia o bot
            subprocess.Popen([sys.executable, "src/infinity_ai/run_bot.py"])
            
            logger.info("✅ Sistema reiniciado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao reiniciar sistema: {e}")
            return False

def main():
    """Função principal"""
    restore = SystemRestore()
    
    # Realiza backup
    if not restore.backup():
        logger.error("Falha no backup, abortando")
        return
        
    # Verifica backup
    if not restore.verify_backup():
        logger.error("Falha na verificação do backup, abortando")
        return
        
    # Limpa backups antigos
    restore.clean_old_backups()
    
    # Restaura sistema
    if not restore.restore_system():
        logger.error("Falha na restauração do sistema")
        return
        
    # Reinicia sistema
    restore.restart_system()

if __name__ == "__main__":
    main() 