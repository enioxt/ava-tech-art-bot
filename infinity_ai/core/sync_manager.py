"""
EVA Sync Manager
Sistema de sincronização e backup automático
"""

import os
import subprocess
import logging
import asyncio
import json
import shutil
import tarfile
import glob
import aiohttp
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any, Tuple
from dataclasses import dataclass, asdict
import sys
import platform

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add a StreamHandler with UTF-8 encoding
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler.setStream(open(1, 'w', encoding='utf-8', closefd=False))
logger.addHandler(handler)

@dataclass
class StorageStats:
    """Estatísticas de armazenamento"""
    total: int
    used: int
    free: int
    percent: float
    status: str
    warning_threshold: float = 0.8
    critical_threshold: float = 0.9
    min_free_space: int = 500 * 1024 * 1024  # 500MB

    @property
    def is_critical(self) -> bool:
        return self.free < self.min_free_space or self.percent > self.critical_threshold

    @property
    def is_warning(self) -> bool:
        return self.percent > self.warning_threshold

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class BackupManifest:
    """Manifesto do backup"""
    timestamp: str
    files: List[str]
    context_included: bool
    git_info: Optional[Dict[str, str]]
    checksums: Dict[str, str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupManifest':
        return cls(**data)

class StorageMonitor:
    def __init__(self):
        self.warning_threshold = 0.8  # 80%
        self.critical_threshold = 0.9  # 90%
        self.min_free_space = 500 * 1024 * 1024  # 500MB em bytes
        self.history: List[StorageStats] = []
        self.max_history = 100

    async def check_space(self) -> StorageStats:
        """Verifica espaço em disco e retorna status"""
        usage = shutil.disk_usage("/")
        percent = usage.used / usage.total
        
        stats = StorageStats(
            total=usage.total,
            used=usage.used,
            free=usage.free,
            percent=percent,
            status=self._get_status(percent, usage.free),
            warning_threshold=self.warning_threshold,
            critical_threshold=self.critical_threshold,
            min_free_space=self.min_free_space
        )
        
        # Atualiza histórico
        self.history.append(stats)
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        # Logs baseados no status
        if stats.is_critical:
            logger.critical(f"⚠️ Espaço crítico! Apenas {stats.free/1024/1024:.2f}MB livre")
        elif stats.is_warning:
            logger.warning(f"⚠️ Uso de disco alto: {stats.percent*100:.1f}%")
            
        return stats
        
    def _get_status(self, percent: float, free_space: int) -> str:
        """Determina status baseado nas métricas"""
        if free_space < self.min_free_space:
            return "critical"
        elif percent > self.critical_threshold:
            return "critical"
        elif percent > self.warning_threshold:
            return "warning"
        return "ok"
        
    def get_trend(self) -> str:
        """Analisa tendência de uso do armazenamento"""
        if len(self.history) < 2:
            return "stable"
            
        recent = self.history[-10:]
        if len(recent) < 2:
            return "stable"
            
        start_percent = recent[0].percent
        end_percent = recent[-1].percent
        
        if end_percent - start_percent > 0.1:  # 10% de aumento
            return "increasing"
        elif start_percent - end_percent > 0.1:  # 10% de redução
            return "decreasing"
        return "stable"

class SyncManager:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Carrega configurações
        self.cloud_enabled = bool(os.getenv("CLOUD_BACKUP_ENABLED", "true").lower() == "true")
        self.github_enabled = bool(os.getenv("GITHUB_SYNC_ENABLED", "true").lower() == "true")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO")
        self.github_branch = os.getenv("GITHUB_BRANCH", "main")
        
        # Componentes
        self.storage_monitor = StorageMonitor()
        
        # Estado
        self.last_backup: Optional[Path] = None
        self.last_sync: Optional[datetime] = None
        self.sync_interval = int(os.getenv("SYNC_INTERVAL", "3600"))  # 1 hora
        
        # Configura git se habilitado
        if self.github_enabled:
            self._setup_git()
        
    def _setup_git(self):
        """Configura git para o repositório"""
        try:
            # Verifica se já é um repositório git
            if not Path(".git").exists():
                # Inicializa repositório
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{self.github_repo}.git"], check=True)
            
            # Configura credenciais se token fornecido
            if self.github_token:
                repo_url = f"https://{self.github_token}@github.com/{self.github_repo}.git"
                subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)
            
            logger.info("✅ Git configurado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro na configuração do git: {e}")
            
    async def create_backup(self, context_data: Optional[Dict] = None) -> Tuple[bool, Optional[str]]:
        """Cria backup local e sincroniza"""
        try:
            # Verifica espaço
            stats = await self.storage_monitor.check_space()
            if stats.is_critical:
                logger.error("Espaço insuficiente para backup")
                return False, None
                
            # Cria nome único para backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"eva_backup_{timestamp}"
            backup_path.mkdir(exist_ok=True)
            
            # Salva contexto se fornecido
            if context_data:
                context_file = backup_path / "context.json"
                with open(context_file, "w", encoding="utf-8") as f:
                    json.dump(context_data, f, indent=2, ensure_ascii=False)
            
            # Lista de arquivos críticos
            critical_files = [
                "src/infinity_ai",
                ".env",
                "requirements.txt",
                "docs",
                "data"
            ]
            
            # Copia arquivos e calcula checksums
            checksums = {}
            for file in critical_files:
                src = Path(file)
                dst = backup_path / file
                if src.is_file():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    checksums[file] = await self._calculate_checksum(src)
                elif src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    checksums[file] = await self._calculate_dir_checksum(src)
            
            # Cria manifesto
            manifest = BackupManifest(
                timestamp=timestamp,
                files=critical_files,
                context_included=bool(context_data),
                git_info=await self._get_git_info() if self.github_enabled else None,
                checksums=checksums,
                metadata={
                    "storage_stats": asdict(stats),
                    "storage_trend": self.storage_monitor.get_trend(),
                    "system_info": {
                        "python_version": sys.version,
                        "platform": platform.platform(),
                        "hostname": platform.node()
                    }
                }
            )
            
            # Salva manifesto
            with open(backup_path / "manifest.json", "w") as f:
                json.dump(manifest.to_dict(), f, indent=2)
            
            # Comprime backup
            archive_path = backup_path.with_suffix(".tar.gz")
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(backup_path, arcname=backup_path.name)
            
            # Remove diretório original após compressão
            shutil.rmtree(backup_path)
            
            # Sincroniza
            sync_tasks = []
            
            if self.cloud_enabled:
                sync_tasks.append(self._sync_to_cloud(archive_path))
            
            if self.github_enabled:
                sync_tasks.append(self._sync_to_github(archive_path))
            
            if sync_tasks:
                await asyncio.gather(*sync_tasks)
            
            # Atualiza estado
            self.last_backup = archive_path
            self.last_sync = datetime.now()
            
            logger.info(f"✅ Backup criado e sincronizado: {archive_path}")
            return True, str(archive_path)
            
        except Exception as e:
            logger.error(f"❌ Erro no backup: {e}")
            return False, None
            
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula checksum SHA256 de um arquivo"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
        
    async def _calculate_dir_checksum(self, dir_path: Path) -> str:
        """Calcula checksum de um diretório"""
        sha256 = hashlib.sha256()
        for path in sorted(dir_path.rglob("*")):
            if path.is_file():
                sha256.update(path.name.encode())
                sha256.update(await self._calculate_checksum(path).encode())
        return sha256.hexdigest()
    
    async def _sync_to_cloud(self, backup_path: Path):
        """Sincroniza backup com a nuvem"""
        try:
            # TODO: Implementar sincronização com serviço de nuvem específico
            # Por enquanto, apenas simula
            logger.info("☁️ Simulando sincronização com nuvem...")
            await asyncio.sleep(1)  # Simula operação assíncrona
            
        except Exception as e:
            logger.error(f"❌ Erro na sincronização com nuvem: {e}")
    
    async def _sync_to_github(self, backup_path: Optional[Path] = None):
        """Sincroniza alterações com GitHub"""
        try:
            if not (self.github_token and self.github_repo):
                logger.warning("⚠️ Configurações do GitHub incompletas")
                return
            
            # Verifica status atual
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
            if not status and not backup_path:
                logger.info("✨ Nada novo para sincronizar com GitHub")
                return
                
            # Prepara commit
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"EVA Auto-Sync: {timestamp}"
            if backup_path:
                commit_msg += f"\nBackup: {backup_path.name}"
            
            # Executa comandos git
            commands = [
                ["git", "add", "."],
                ["git", "commit", "-m", commit_msg],
                ["git", "pull", "--rebase", "origin", self.github_branch],
                ["git", "push", "origin", self.github_branch]
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Erro no comando git {cmd[1]}: {result.stderr}")
                    raise Exception(f"Erro no git {cmd[1]}")
                
            logger.info("✅ Sincronizado com GitHub")
            
        except Exception as e:
            logger.error(f"❌ Erro na sincronização com GitHub: {e}")
            
    async def _get_git_info(self) -> Dict[str, str]:
        """Obtém informações do git para o manifesto"""
        try:
            commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
            
            return {
                "commit": commit,
                "branch": branch,
                "repo": self.github_repo
            }
        except:
            return {}
    
    async def clean_old_backups(self, max_age_days: int = 7):
        """Limpa backups antigos"""
        try:
            now = datetime.now()
            for backup in self.backup_dir.glob("eva_backup_*.tar.gz"):
                # Extrai data do nome
                try:
                    date_str = backup.stem.split("_")[2]
                    backup_date = datetime.strptime(date_str, "%Y%m%d")
                    age = (now - backup_date).days
                    
                    if age > max_age_days:
                        backup.unlink()
                        logger.info(f"🗑️ Backup antigo removido: {backup.name}")
                except (IndexError, ValueError):
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Erro na limpeza de backups: {e}")
            
    async def verify_backup(self, backup_path: Path) -> bool:
        """Verifica integridade do backup"""
        try:
            # Extrai backup para verificação
            temp_dir = Path("temp_verify")
            temp_dir.mkdir(exist_ok=True)
            
            try:
                with tarfile.open(backup_path, "r:gz") as tar:
                    tar.extractall(temp_dir)
                    
                # Carrega manifesto
                manifest_file = next(temp_dir.glob("*/manifest.json"))
                with open(manifest_file) as f:
                    manifest = BackupManifest.from_dict(json.load(f))
                    
                backup_dir = manifest_file.parent
                    
                # Verifica arquivos e checksums
                for file, stored_hash in manifest.checksums.items():
                    path = backup_dir / file
                    if not path.exists():
                        logger.error(f"Arquivo ausente no backup: {file}")
                        return False
                        
                    if path.is_file():
                        current_hash = await self._calculate_checksum(path)
                    else:
                        current_hash = await self._calculate_dir_checksum(path)
                        
                    if current_hash != stored_hash:
                        logger.error(f"Checksum inválido para {file}")
                        return False
                        
                # Verifica contexto se incluído
                if manifest.context_included:
                    if not (backup_dir / "context.json").exists():
                        logger.error("Arquivo de contexto ausente")
                        return False
                        
                logger.info("✅ Backup verificado com sucesso")
                return True
                
            finally:
                # Limpa diretório temporário
                shutil.rmtree(temp_dir)
                
        except Exception as e:
            logger.error(f"❌ Erro na verificação do backup: {e}")
            return False
            
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de armazenamento"""
        stats = await self.storage_monitor.check_space()
        return {
            "storage": stats.to_dict(),
            "trend": self.storage_monitor.get_trend(),
            "backups": {
                "count": len(list(self.backup_dir.glob("*.tar.gz"))),
                "last_backup": str(self.last_backup) if self.last_backup else None,
                "last_sync": self.last_sync.isoformat() if self.last_sync else None
            }
        }
        
    async def optimize_storage(self) -> bool:
        """Otimiza uso de armazenamento"""
        try:
            # Limpa backups antigos primeiro
            await self.clean_old_backups()
            
            # Remove arquivos temporários
            temp_patterns = [
                "*.tmp",
                "*.temp",
                "*.log.*",
                "__pycache__",
                "*.pyc"
            ]
            
            for pattern in temp_patterns:
                for file in Path().rglob(pattern):
                    if file.is_file():
                        file.unlink()
                    elif file.is_dir():
                        shutil.rmtree(file)
                        
            # Comprime logs antigos
            log_dir = Path("logs")
            if log_dir.exists():
                for log in log_dir.glob("*.log"):
                    if log.stat().st_size > 1024 * 1024:  # 1MB
                        archive = log.with_suffix(".log.gz")
                        with tarfile.open(archive, "w:gz") as tar:
                            tar.add(log)
                        log.unlink()
                        
            logger.info("✅ Armazenamento otimizado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na otimização: {e}")
            return False