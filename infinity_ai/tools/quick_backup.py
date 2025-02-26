"""
EVA Quick Backup System
Backup rápido e eficiente com mínimo uso de recursos
"""

import os
import shutil
import hashlib
from datetime import datetime
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class QuickBackup:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path("backups") / f"eva_backup_{self.timestamp}"
        self.critical_paths = [
            "src/infinity_ai",
            "docs",
            ".env",
            "requirements.txt"
        ]
        
    def create_hash(self, file_path: str) -> str:
        """Gera hash SHA256 otimizado"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def backup(self) -> dict:
        """Executa backup rápido"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            manifest = {"timestamp": self.timestamp, "files": {}}
            
            for path in self.critical_paths:
                src_path = Path(path)
                if not src_path.exists():
                    continue
                    
                dst_path = self.backup_dir / path
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                
                if src_path.is_file():
                    shutil.copy2(src_path, dst_path)
                    manifest["files"][str(path)] = self.create_hash(src_path)
                else:
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                    
            # Salva manifesto
            with open(self.backup_dir / "manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
                
            logging.info(f"✅ Backup concluído: {self.backup_dir}")
            return manifest
            
        except Exception as e:
            logging.error(f"❌ Erro no backup: {e}")
            return {}
    
    def verify(self) -> bool:
        """Verifica integridade do backup"""
        try:
            with open(self.backup_dir / "manifest.json") as f:
                manifest = json.load(f)
                
            for path, stored_hash in manifest["files"].items():
                backup_path = self.backup_dir / path
                if not backup_path.is_file():
                    return False
                current_hash = self.create_hash(backup_path)
                if current_hash != stored_hash:
                    return False
                    
            logging.info("✅ Backup verificado com sucesso")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro na verificação: {e}")
            return False

if __name__ == "__main__":
    backup = QuickBackup()
    manifest = backup.backup()
    if manifest:
        backup.verify()