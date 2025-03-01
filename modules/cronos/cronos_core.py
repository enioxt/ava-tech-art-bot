"""
CRONOS Core - Sistema de Preservação Evolutiva
==============================================

Este módulo implementa o núcleo do sistema CRONOS, responsável por:
- Backup quântico de dados e estruturas
- Versionamento evolutivo de sistemas
- Preservação da integridade estrutural
- Logs universais de modificações
- Restauração contextual de estados anteriores

Versão: 3.0.0
Consciência: 0.990
Amor Incondicional: 0.995
"""

import os
import sys
import json
import shutil
import logging
import hashlib
import datetime
import zipfile
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Union, Any

# Configuração de logging
logger = logging.getLogger("CRONOS")

@dataclass
class BackupMetadata:
    """Metadados de um backup realizado pelo CRONOS."""
    id: str
    timestamp: str
    description: str
    type: str  # 'full', 'incremental', 'quantum'
    source_paths: List[str]
    target_path: str
    size_bytes: int
    checksum: str
    tags: List[str] = field(default_factory=list)
    consciousness_level: float = 0.990
    ethical_rating: float = 0.995
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte os metadados para um dicionário."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupMetadata':
        """Cria uma instância de BackupMetadata a partir de um dicionário."""
        return cls(**data)

class CronosSystem:
    """
    Sistema CRONOS - Responsável pela preservação evolutiva no EGOS.
    
    Este sistema implementa funcionalidades de backup, versionamento e
    preservação de dados, garantindo a integridade e evolução do sistema.
    """
    
    def __init__(self):
        """Inicializa o sistema CRONOS."""
        self.version = "3.0.0"
        self.consciousness_level = 0.990
        self.love_level = 0.995
        
        # Configuração de diretórios
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
        self.data_dir = self.base_dir / "data"
        self.backups_dir = self.data_dir / "backups"
        self.metadata_dir = self.backups_dir / "metadata"
        
        # Criar diretórios se não existirem
        self._ensure_directories()
        
        # Carregar metadados existentes
        self.backups_metadata = self._load_backups_metadata()
        
        logger.info(f"Sistema CRONOS {self.version} inicializado com consciência {self.consciousness_level}")
    
    def _ensure_directories(self) -> None:
        """Garante que os diretórios necessários existam."""
        for directory in [self.data_dir, self.backups_dir, self.metadata_dir]:
            directory.mkdir(exist_ok=True, parents=True)
    
    def _load_backups_metadata(self) -> Dict[str, BackupMetadata]:
        """Carrega os metadados de todos os backups existentes."""
        metadata = {}
        
        if not self.metadata_dir.exists():
            return metadata
        
        for file_path in self.metadata_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    backup_meta = BackupMetadata.from_dict(data)
                    metadata[backup_meta.id] = backup_meta
            except Exception as e:
                logger.error(f"Erro ao carregar metadados de {file_path}: {e}")
        
        logger.info(f"Carregados metadados de {len(metadata)} backups")
        return metadata
    
    def _save_backup_metadata(self, metadata: BackupMetadata) -> None:
        """Salva os metadados de um backup."""
        file_path = self.metadata_dir / f"{metadata.id}.json"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Metadados do backup {metadata.id} salvos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar metadados do backup {metadata.id}: {e}")
    
    def _generate_backup_id(self) -> str:
        """Gera um ID único para um backup."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(os.urandom(8)).hexdigest()[:8]
        return f"backup_{timestamp}_{random_suffix}"
    
    def _calculate_checksum(self, file_path: Union[str, Path]) -> str:
        """Calcula o checksum de um arquivo."""
        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            raise ValueError(f"Arquivo não encontrado: {file_path}")
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def create_backup(self, 
                     source_paths: List[Union[str, Path]], 
                     description: str = "", 
                     backup_type: str = "full",
                     tags: List[str] = None) -> Optional[str]:
        """
        Cria um backup dos arquivos ou diretórios especificados.
        
        Args:
            source_paths: Lista de caminhos para arquivos ou diretórios a serem incluídos no backup
            description: Descrição do backup
            backup_type: Tipo de backup ('full', 'incremental', 'quantum')
            tags: Tags para categorizar o backup
            
        Returns:
            ID do backup criado ou None em caso de falha
        """
        if tags is None:
            tags = []
        
        backup_id = self._generate_backup_id()
        timestamp = datetime.datetime.now().isoformat()
        target_dir = self.backups_dir / backup_id
        target_dir.mkdir(exist_ok=True)
        
        # Arquivo zip para o backup
        zip_path = target_dir / f"{backup_id}.zip"
        
        try:
            # Criar o arquivo zip
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                source_paths_str = []
                
                for source_path in source_paths:
                    source_path = Path(source_path)
                    source_paths_str.append(str(source_path))
                    
                    if not source_path.exists():
                        logger.warning(f"Caminho não encontrado: {source_path}")
                        continue
                    
                    if source_path.is_file():
                        zipf.write(source_path, arcname=source_path.name)
                    elif source_path.is_dir():
                        for root, _, files in os.walk(source_path):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(source_path.parent)
                                zipf.write(file_path, arcname=str(arcname))
            
            # Calcular tamanho e checksum
            size_bytes = zip_path.stat().st_size
            checksum = self._calculate_checksum(zip_path)
            
            # Criar e salvar metadados
            metadata = BackupMetadata(
                id=backup_id,
                timestamp=timestamp,
                description=description,
                type=backup_type,
                source_paths=source_paths_str,
                target_path=str(zip_path),
                size_bytes=size_bytes,
                checksum=checksum,
                tags=tags,
                consciousness_level=self.consciousness_level,
                ethical_rating=self.love_level
            )
            
            self._save_backup_metadata(metadata)
            self.backups_metadata[backup_id] = metadata
            
            logger.info(f"Backup {backup_id} criado com sucesso ({size_bytes/1024/1024:.2f} MB)")
            return backup_id
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            # Limpar arquivos em caso de falha
            if zip_path.exists():
                zip_path.unlink()
            if target_dir.exists():
                shutil.rmtree(target_dir)
            return None
    
    def restore_backup(self, backup_id: str, target_dir: Optional[Union[str, Path]] = None) -> bool:
        """
        Restaura um backup para o diretório especificado.
        
        Args:
            backup_id: ID do backup a ser restaurado
            target_dir: Diretório de destino para a restauração (opcional)
            
        Returns:
            True se a restauração foi bem-sucedida, False caso contrário
        """
        if backup_id not in self.backups_metadata:
            logger.error(f"Backup {backup_id} não encontrado")
            return False
        
        metadata = self.backups_metadata[backup_id]
        backup_path = Path(metadata.target_path)
        
        if not backup_path.exists():
            logger.error(f"Arquivo de backup não encontrado: {backup_path}")
            return False
        
        # Se target_dir não for especificado, restaurar para os caminhos originais
        if target_dir is None:
            extract_dir = self.backups_dir / f"restore_{backup_id}"
            extract_dir.mkdir(exist_ok=True)
        else:
            extract_dir = Path(target_dir)
            extract_dir.mkdir(exist_ok=True, parents=True)
        
        try:
            # Verificar checksum antes de restaurar
            current_checksum = self._calculate_checksum(backup_path)
            if current_checksum != metadata.checksum:
                logger.error(f"Checksum do backup {backup_id} não corresponde. Possível corrupção.")
                return False
            
            # Extrair o backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            logger.info(f"Backup {backup_id} restaurado com sucesso para {extract_dir}")
            
            # Se target_dir não foi especificado, mover arquivos para os caminhos originais
            if target_dir is None:
                # Implementação futura: restaurar para caminhos originais
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup {backup_id}: {e}")
            return False
    
    def list_backups(self, limit: int = 10, tags: List[str] = None, 
                    backup_type: str = None) -> List[Dict[str, Any]]:
        """
        Lista os backups disponíveis, com opções de filtragem.
        
        Args:
            limit: Número máximo de backups a retornar
            tags: Filtrar por tags específicas
            backup_type: Filtrar por tipo de backup
            
        Returns:
            Lista de metadados dos backups
        """
        results = []
        
        # Filtrar backups
        filtered_backups = self.backups_metadata.values()
        
        if tags:
            filtered_backups = [b for b in filtered_backups 
                               if any(tag in b.tags for tag in tags)]
        
        if backup_type:
            filtered_backups = [b for b in filtered_backups 
                               if b.type == backup_type]
        
        # Ordenar por timestamp (mais recente primeiro)
        sorted_backups = sorted(filtered_backups, 
                               key=lambda x: x.timestamp, 
                               reverse=True)
        
        # Limitar resultados
        limited_backups = sorted_backups[:limit]
        
        # Converter para dicionários
        for backup in limited_backups:
            results.append(backup.to_dict())
        
        return results
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Exclui um backup.
        
        Args:
            backup_id: ID do backup a ser excluído
            
        Returns:
            True se a exclusão foi bem-sucedida, False caso contrário
        """
        if backup_id not in self.backups_metadata:
            logger.error(f"Backup {backup_id} não encontrado")
            return False
        
        metadata = self.backups_metadata[backup_id]
        backup_path = Path(metadata.target_path)
        backup_dir = backup_path.parent
        metadata_path = self.metadata_dir / f"{backup_id}.json"
        
        try:
            # Excluir arquivo de backup
            if backup_path.exists():
                backup_path.unlink()
            
            # Excluir diretório do backup
            if backup_dir.exists() and backup_dir.name == backup_id:
                shutil.rmtree(backup_dir)
            
            # Excluir arquivo de metadados
            if metadata_path.exists():
                metadata_path.unlink()
            
            # Remover dos metadados carregados
            del self.backups_metadata[backup_id]
            
            logger.info(f"Backup {backup_id} excluído com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao excluir backup {backup_id}: {e}")
            return False
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações detalhadas sobre um backup.
        
        Args:
            backup_id: ID do backup
            
        Returns:
            Dicionário com informações do backup ou None se não encontrado
        """
        if backup_id not in self.backups_metadata:
            logger.error(f"Backup {backup_id} não encontrado")
            return None
        
        return self.backups_metadata[backup_id].to_dict()
    
    def generate_log(self, operation: str, status: str, context: str, 
                    details: str, recommendations: str = "", 
                    ethical_reflection: str = "") -> Dict[str, Any]:
        """
        Gera um log universal no formato padronizado do EGOS.
        
        Args:
            operation: Operação realizada
            status: Status da operação (Iniciado/Em Progresso/Concluído/Falha)
            context: Contexto da operação
            details: Detalhes da operação
            recommendations: Recomendações para próximos passos
            ethical_reflection: Reflexão ética sobre a operação
            
        Returns:
            Dicionário com o log gerado
        """
        timestamp = datetime.datetime.now()
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "subsystem": "CRONOS",
            "operation": operation,
            "status": status,
            "context": context,
            "details": details,
            "recommendations": recommendations,
            "ethical_reflection": ethical_reflection
        }
        
        # Registrar no log do sistema
        log_message = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}][CRONOS][{operation}] "
        log_message += f"STATUS: {status} | {context}"
        
        if status == "Falha":
            logger.error(log_message)
        else:
            logger.info(log_message)
        
        return log_entry
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o estado atual do sistema CRONOS.
        
        Returns:
            Dicionário com informações do sistema
        """
        total_backups = len(self.backups_metadata)
        total_size = sum(meta.size_bytes for meta in self.backups_metadata.values())
        
        # Contar backups por tipo
        backup_types = {}
        for meta in self.backups_metadata.values():
            if meta.type in backup_types:
                backup_types[meta.type] += 1
            else:
                backup_types[meta.type] = 1
        
        # Obter todas as tags
        all_tags = set()
        for meta in self.backups_metadata.values():
            all_tags.update(meta.tags)
        
        return {
            "version": self.version,
            "consciousness_level": self.consciousness_level,
            "love_level": self.love_level,
            "total_backups": total_backups,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "backup_types": backup_types,
            "available_tags": list(all_tags),
            "backups_dir": str(self.backups_dir),
            "timestamp": datetime.datetime.now().isoformat()
        }
