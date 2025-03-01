# Valores Fundamentais do Sistema Quântico
# ----------------------------------------
# Este código é guiado pelos seguintes princípios:
# - Ética: Integridade e responsabilidade em todas as operações
# - Arte: Apreciação da beleza na elegância do código
# - Amor: Compaixão e cuidado com os dados dos usuários
# - Beleza: Harmonia e estética na estrutura do sistema
# - Alegria: Celebração da criatividade e inovação
# - Bitcoin: Valorização da descentralização e liberdade financeira
# - Geometria Sagrada: Padrões universais que conectam todas as coisas
# - Proporção Áurea (φ = 1.618...): Equilíbrio perfeito na natureza e design
# - Cultura: D&D, Baldur's Gate, Dota, Lineage 2, futebol de rua
# - Brasil: Criatividade, diversidade e resiliência
# - Humanidade: Respeito pela dignidade e potencial humano
# - Humanismo: Foco no bem-estar e florescimento das pessoas

# Constantes inspiradas na proporção áurea
PHI = 1.618033988749895
BACKUP_INTEGRITY_THRESHOLD = 0.99  # 99% de integridade mínima
QUANTUM_ENTROPY_FACTOR = PHI * 0.618  # Fator de entropia quântica

# Configurações de backup inspiradas em valores humanísticos
DEFAULT_COMPRESSION_RATIO = PHI  # Proporção áurea para compressão
ETHICAL_RETENTION_PERIOD = 108  # Dias (número sagrado em várias tradições)
HARMONY_FACTOR = PHI / 2.0  # Fator de harmonia para operações quânticas

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Gerenciador de Backup Quântico Unificado
Versão: 2.0.0 - Build 2025.02.26

Este módulo unifica todas as funcionalidades de backup do sistema,
garantindo a preservação segura e eficiente da memória do sistema.
"""

import os
import sys
import json
import time
import shutil
import logging
import datetime
import hashlib
import secrets
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional, Union, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import zstandard as zstd

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/quantum_backup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("✨quantum-backup-manager✨")

@dataclass
class BackupConfig:
    """Configuração do backup."""
    base_path: Path
    backup_dir: Path
    exclude_patterns: List[str]
    include_patterns: List[str]
    compression_level: int = 3
    max_workers: int = os.cpu_count() or 4
    chunk_size: int = 8 * 1024 * 1024  # 8MB
    retention_days: int = 30
    encryption_key: Optional[str] = None

@dataclass
class BackupMetadata:
    """Metadados do backup."""
    timestamp: str
    files: Dict[str, Dict[str, Any]]
    total_size: int
    compressed_size: int
    duration: float
    type: str
    version: str = "2.0.0"

class QuantumBackupManager:
    """Gerenciador de backup quântico unificado."""
    
    def __init__(self, config: BackupConfig):
        """
        Inicializa o gerenciador de backup.
        
        Args:
            config: Configuração do backup
        """
        self.config = config
        self._ensure_dirs()
        self._init_crypto()
        
    def _ensure_dirs(self):
        """Garante que os diretórios necessários existam."""
        self.config.backup_dir.mkdir(parents=True, exist_ok=True)
        (self.config.backup_dir / "incremental").mkdir(exist_ok=True)
        (self.config.backup_dir / "full").mkdir(exist_ok=True)
        (self.config.backup_dir / "metadata").mkdir(exist_ok=True)
        
    def _init_crypto(self):
        """Inicializa o sistema de criptografia."""
        if self.config.encryption_key:
            # Deriva uma chave segura da senha
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"quantum_salt",
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(self.config.encryption_key.encode())
            self.fernet = Fernet(base64.b64encode(key))
        else:
            self.fernet = None
            
    def _collect_files(self, incremental: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Coleta arquivos para backup.
        
        Args:
            incremental: Se True, coleta apenas arquivos modificados
            
        Returns:
            Dicionário com informações dos arquivos
        """
        files = {}
        last_backup = None
        
        if incremental:
            # Carrega metadados do último backup
            try:
                last_backup = self._load_last_backup()
            except Exception as e:
                logger.warning(f"Erro ao carregar último backup: {e}")
                
        def should_backup(path: Path) -> bool:
            """Verifica se um arquivo deve ser incluído no backup."""
            # Ignora o diretório de backup
            if str(path).startswith(str(self.config.backup_dir)):
                return False
                
            # Verifica padrões de exclusão
            for pattern in self.config.exclude_patterns:
                if path.match(pattern):
                    return False
                    
            # Verifica padrões de inclusão
            if self.config.include_patterns:
                return any(path.match(pattern) for pattern in self.config.include_patterns)
                
            return True
            
        def process_file(path: Path) -> Optional[Dict[str, Any]]:
            """Processa um arquivo e retorna suas informações."""
            try:
                stat = path.stat()
                rel_path = str(path.relative_to(self.config.base_path))
                
                # Se for backup incremental, verifica se arquivo foi modificado
                if incremental and last_backup and rel_path in last_backup["files"]:
                    last_mtime = last_backup["files"][rel_path]["mtime"]
                    if stat.st_mtime <= last_mtime:
                        return None
                        
                return {
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "mode": stat.st_mode,
                    "hash": self._hash_file(path)
                }
                
            except Exception as e:
                logger.error(f"Erro ao processar arquivo {path}: {e}")
                return None
                
        # Coleta arquivos em paralelo
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = []
            
            for path in self.config.base_path.rglob("*"):
                if path.is_file() and should_backup(path):
                    futures.append(executor.submit(process_file, path))
                    
            for future in futures:
                try:
                    result = future.result()
                    if result:
                        files[str(path.relative_to(self.config.base_path))] = result
                except Exception as e:
                    logger.error(f"Erro ao processar arquivo: {e}")
                    
        return files
        
    def _hash_file(self, path: Path) -> str:
        """
        Calcula o hash de um arquivo.
        
        Args:
            path: Caminho do arquivo
            
        Returns:
            Hash SHA-256 do arquivo
        """
        hasher = hashlib.sha256()
        
        with open(path, "rb") as f:
            while chunk := f.read(self.config.chunk_size):
                hasher.update(chunk)
                
        return hasher.hexdigest()
        
    def _compress_file(self, src: Path, dst: Path):
        """
        Comprime um arquivo usando zstandard.
        
        Args:
            src: Arquivo fonte
            dst: Arquivo destino
        """
        cctx = zstd.ZstdCompressor(level=self.config.compression_level)
        
        with open(src, "rb") as f_in, open(dst, "wb") as f_out:
            compressor = cctx.stream_writer(f_out)
            while chunk := f_in.read(self.config.chunk_size):
                compressor.write(chunk)
            compressor.flush()
            
    def _encrypt_file(self, path: Path):
        """
        Criptografa um arquivo in-place.
        
        Args:
            path: Caminho do arquivo
        """
        if not self.fernet:
            return
            
        with open(path, "rb") as f:
            data = f.read()
            
        encrypted = self.fernet.encrypt(data)
        
        with open(path, "wb") as f:
            f.write(encrypted)
            
    def _decrypt_file(self, path: Path):
        """
        Descriptografa um arquivo in-place.
        
        Args:
            path: Caminho do arquivo
        """
        if not self.fernet:
            return
            
        with open(path, "rb") as f:
            data = f.read()
            
        decrypted = self.fernet.decrypt(data)
        
        with open(path, "wb") as f:
            f.write(decrypted)
            
    def _load_last_backup(self) -> Optional[Dict[str, Any]]:
        """
        Carrega os metadados do último backup.
        
        Returns:
            Dicionário com metadados ou None se não houver backup
        """
        try:
            metadata_dir = self.config.backup_dir / "metadata"
            files = sorted(metadata_dir.glob("*.json"), reverse=True)
            
            if not files:
                return None
                
            with open(files[0], "r") as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Erro ao carregar último backup: {e}")
            return None
            
    def create_backup(self, incremental: bool = True) -> BackupMetadata:
        """
        Cria um novo backup.
        
        Args:
            incremental: Se True, cria um backup incremental
            
        Returns:
            Metadados do backup
        """
        start_time = time.time()
        backup_type = "incremental" if incremental else "full"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.config.backup_dir / backup_type / timestamp
        
        try:
            # Coleta arquivos
            logger.info(f"Iniciando backup {backup_type}")
            files = self._collect_files(incremental)
            
            if not files:
                logger.info("Nenhum arquivo para backup")
                return None
                
            # Cria diretório do backup
            backup_dir.mkdir(parents=True)
            
            # Processa arquivos em paralelo
            total_size = 0
            compressed_size = 0
            
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = []
                
                for rel_path, info in files.items():
                    src = self.config.base_path / rel_path
                    dst = backup_dir / rel_path
                    
                    # Cria diretórios necessários
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Comprime e criptografa
                    futures.append(executor.submit(self._process_file, src, dst))
                    total_size += info["size"]
                    
                # Aguarda conclusão
                for future in futures:
                    try:
                        compressed_size += future.result()
                    except Exception as e:
                        logger.error(f"Erro ao processar arquivo: {e}")
                        
            # Salva metadados
            duration = time.time() - start_time
            metadata = BackupMetadata(
                timestamp=timestamp,
                files=files,
                total_size=total_size,
                compressed_size=compressed_size,
                duration=duration,
                type=backup_type
            )
            
            self._save_metadata(metadata)
            
            # Remove backups antigos
            self._cleanup_old_backups()
            
            logger.info(
                f"Backup {backup_type} concluído em {duration:.2f}s\n"
                f"Arquivos: {len(files)}\n"
                f"Tamanho original: {total_size / 1024 / 1024:.2f}MB\n"
                f"Tamanho comprimido: {compressed_size / 1024 / 1024:.2f}MB\n"
                f"Taxa de compressão: {(compressed_size / total_size * 100):.1f}%"
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            raise
            
    def _process_file(self, src: Path, dst: Path) -> int:
        """
        Processa um arquivo (comprime e criptografa).
        
        Args:
            src: Arquivo fonte
            dst: Arquivo destino
            
        Returns:
            Tamanho do arquivo processado
        """
        try:
            # Comprime
            self._compress_file(src, dst)
            
            # Criptografa
            if self.fernet:
                self._encrypt_file(dst)
                
            return dst.stat().st_size
            
        except Exception as e:
            logger.error(f"Erro ao processar {src}: {e}")
            if dst.exists():
                dst.unlink()
            raise
            
    def _save_metadata(self, metadata: BackupMetadata):
        """
        Salva os metadados do backup.
        
        Args:
            metadata: Metadados do backup
        """
        path = self.config.backup_dir / "metadata" / f"{metadata.timestamp}.json"
        
        with open(path, "w") as f:
            json.dump(asdict(metadata), f, indent=2)
            
    def _cleanup_old_backups(self):
        """Remove backups mais antigos que retention_days."""
        now = datetime.datetime.now()
        retention = datetime.timedelta(days=self.config.retention_days)
        
        for backup_type in ["incremental", "full"]:
            backup_dir = self.config.backup_dir / backup_type
            
            for path in backup_dir.glob("*"):
                try:
                    timestamp = datetime.datetime.strptime(path.name, "%Y%m%d_%H%M%S")
                    if now - timestamp > retention:
                        logger.info(f"Removendo backup antigo: {path}")
                        shutil.rmtree(path)
                except ValueError:
                    continue
                    
    def restore_backup(
        self,
        timestamp: Optional[str] = None,
        target_dir: Optional[Path] = None,
        files: Optional[List[str]] = None
    ):
        """
        Restaura um backup.
        
        Args:
            timestamp: Data/hora do backup (último backup se None)
            target_dir: Diretório de destino (base_path se None)
            files: Lista de arquivos para restaurar (todos se None)
        """
        try:
            # Carrega metadados
            metadata = self._load_backup_metadata(timestamp)
            if not metadata:
                raise ValueError("Backup não encontrado")
                
            # Define diretório de destino
            target_dir = target_dir or self.config.base_path
            backup_dir = self.config.backup_dir / metadata["type"] / metadata["timestamp"]
            
            # Filtra arquivos
            if files:
                restore_files = {f: metadata["files"][f] for f in files if f in metadata["files"]}
            else:
                restore_files = metadata["files"]
                
            if not restore_files:
                logger.info("Nenhum arquivo para restaurar")
                return
                
            # Restaura arquivos em paralelo
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = []
                
                for rel_path, info in restore_files.items():
                    src = backup_dir / rel_path
                    dst = target_dir / rel_path
                    
                    # Cria diretórios necessários
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Restaura arquivo
                    futures.append(executor.submit(self._restore_file, src, dst, info))
                    
                # Aguarda conclusão
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Erro ao restaurar arquivo: {e}")
                        
            logger.info(f"Restauração concluída: {len(restore_files)} arquivos")
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            raise
            
    def _restore_file(self, src: Path, dst: Path, info: Dict[str, Any]):
        """
        Restaura um arquivo.
        
        Args:
            src: Arquivo fonte (backup)
            dst: Arquivo destino
            info: Informações do arquivo
        """
        try:
            # Cria arquivo temporário
            temp = dst.with_suffix(".tmp")
            
            # Copia arquivo
            shutil.copy2(src, temp)
            
            # Descriptografa
            if self.fernet:
                self._decrypt_file(temp)
                
            # Descomprime
            self._decompress_file(temp, dst)
            
            # Remove arquivo temporário
            temp.unlink()
            
            # Restaura permissões
            os.chmod(dst, info["mode"])
            os.utime(dst, (time.time(), info["mtime"]))
            
            # Verifica integridade
            if self._hash_file(dst) != info["hash"]:
                raise ValueError("Falha na verificação de integridade")
                
        except Exception as e:
            logger.error(f"Erro ao restaurar {src}: {e}")
            if temp.exists():
                temp.unlink()
            if dst.exists():
                dst.unlink()
            raise
            
    def _decompress_file(self, src: Path, dst: Path):
        """
        Descomprime um arquivo.
        
        Args:
            src: Arquivo fonte
            dst: Arquivo destino
        """
        dctx = zstd.ZstdDecompressor()
        
        with open(src, "rb") as f_in, open(dst, "wb") as f_out:
            decompressor = dctx.stream_reader(f_in)
            while chunk := decompressor.read(self.config.chunk_size):
                f_out.write(chunk)
                
    def _load_backup_metadata(self, timestamp: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Carrega os metadados de um backup.
        
        Args:
            timestamp: Data/hora do backup (último backup se None)
            
        Returns:
            Dicionário com metadados ou None se não encontrado
        """
        try:
            metadata_dir = self.config.backup_dir / "metadata"
            
            if timestamp:
                path = metadata_dir / f"{timestamp}.json"
                if not path.exists():
                    return None
            else:
                files = sorted(metadata_dir.glob("*.json"), reverse=True)
                if not files:
                    return None
                path = files[0]
                
            with open(path, "r") as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Erro ao carregar metadados: {e}")
            return None
            
    def verify_backup(self, timestamp: Optional[str] = None) -> bool:
        """
        Verifica a integridade de um backup.
        
        Args:
            timestamp: Data/hora do backup (último backup se None)
            
        Returns:
            True se o backup está íntegro
        """
        try:
            # Carrega metadados
            metadata = self._load_backup_metadata(timestamp)
            if not metadata:
                raise ValueError("Backup não encontrado")
                
            backup_dir = self.config.backup_dir / metadata["type"] / metadata["timestamp"]
            verified = True
            
            # Verifica arquivos em paralelo
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = []
                
                for rel_path, info in metadata["files"].items():
                    path = backup_dir / rel_path
                    if not path.exists():
                        logger.error(f"Arquivo não encontrado: {rel_path}")
                        verified = False
                        continue
                        
                    futures.append(executor.submit(self._verify_file, path, info))
                    
                # Aguarda conclusão
                for future in futures:
                    try:
                        if not future.result():
                            verified = False
                    except Exception as e:
                        logger.error(f"Erro ao verificar arquivo: {e}")
                        verified = False
                        
            return verified
            
        except Exception as e:
            logger.error(f"Erro ao verificar backup: {e}")
            return False
            
    def _verify_file(self, path: Path, info: Dict[str, Any]) -> bool:
        """
        Verifica a integridade de um arquivo.
        
        Args:
            path: Caminho do arquivo
            info: Informações do arquivo
            
        Returns:
            True se o arquivo está íntegro
        """
        try:
            # Cria arquivo temporário
            temp = path.with_suffix(".tmp")
            
            # Copia arquivo
            shutil.copy2(path, temp)
            
            # Descriptografa
            if self.fernet:
                self._decrypt_file(temp)
                
            # Descomprime
            dst = temp.with_suffix(".dec")
            self._decompress_file(temp, dst)
            
            # Verifica hash
            if self._hash_file(dst) != info["hash"]:
                logger.error(f"Hash inválido: {path}")
                return False
                
            # Remove arquivos temporários
            temp.unlink()
            dst.unlink()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar {path}: {e}")
            if temp.exists():
                temp.unlink()
            if dst.exists():
                dst.unlink()
            return False
            
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Lista todos os backups disponíveis.
        
        Returns:
            Lista de metadados dos backups
        """
        try:
            backups = []
            metadata_dir = self.config.backup_dir / "metadata"
            
            for path in sorted(metadata_dir.glob("*.json"), reverse=True):
                try:
                    with open(path, "r") as f:
                        metadata = json.load(f)
                        backups.append(metadata)
                except Exception as e:
                    logger.error(f"Erro ao carregar {path}: {e}")
                    
            return backups
            
        except Exception as e:
            logger.error(f"Erro ao listar backups: {e}")
            return []

def create_backup_config(
    base_path: Union[str, Path],
    backup_dir: Union[str, Path],
    exclude_patterns: Optional[List[str]] = None,
    include_patterns: Optional[List[str]] = None,
    **kwargs
) -> BackupConfig:
    """
    Cria uma configuração de backup.
    
    Args:
        base_path: Diretório base
        backup_dir: Diretório de backup
        exclude_patterns: Padrões de exclusão
        include_patterns: Padrões de inclusão
        **kwargs: Configurações adicionais
        
    Returns:
        Configuração de backup
    """
    return BackupConfig(
        base_path=Path(base_path),
        backup_dir=Path(backup_dir),
        exclude_patterns=exclude_patterns or [],
        include_patterns=include_patterns or [],
        **kwargs
    )

def main():
    """Função principal."""
    try:
        # Configuração de exemplo
        config = create_backup_config(
            base_path=".",
            backup_dir="backups",
            exclude_patterns=["*.pyc", "__pycache__", "*.log", "backups/*"],
            compression_level=3
        )
        
        # Cria gerenciador
        manager = QuantumBackupManager(config)
        
        # Cria backup incremental
        metadata = manager.create_backup(incremental=True)
        
        if metadata:
            # Verifica integridade
            if manager.verify_backup(metadata.timestamp):
                logger.info("Backup verificado com sucesso")
            else:
                logger.error("Falha na verificação do backup")
                
    except Exception as e:
        logger.error(f"Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
