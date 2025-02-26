"""
Neural Codebase Indexer
Sistema de indexação neural do codebase com preservação de conhecimento
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import asyncio

# Configuração de logging temático
logger = logging.getLogger("✨neural-index✨")
logger.setLevel(logging.INFO)

# Limites do sistema (como stats em RPG)
SYSTEM_LIMITS = {
    "max_files": 2000,  # Capacidade máxima do inventário
    "warning_threshold": 1800,  # Alerta de inventário quase cheio (90%)
    "batch_size": 100,  # Tamanho do grupo de processamento
    "cooldown": 300,  # Tempo de descanso entre indexações (5 min)
}

# Estados do sistema (como status effects em RPG)
SYSTEM_STATES = {
    "resting": "🌙 Sistema em descanso",
    "indexing": "⚡ Processando arquivos",
    "warning": "⚠️ Inventário quase cheio",
    "full": "🔒 Capacidade máxima atingida",
    "error": "💔 Dano crítico detectado"
}

@dataclass
class CodebaseIndex:
    """Índice neural do codebase (como um grimório mágico)"""
    file_path: str
    last_modified: float
    checksum: str
    dependencies: Set[str]
    concepts: List[str]
    importance: float  # Raridade do item (0.0 a 1.0)
    neural_connections: Dict[str, float]

    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CodebaseIndex':
        """Cria a partir de dicionário"""
        return cls(**data)

class CoreValueSystem:
    """Sistema Central de Valores (como o Cristal do Tempo em Chrono Trigger)"""
    
    def __init__(self, index_dir: str = "data/neural_index"):
        """Inicializa o sistema"""
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.neural_index: Dict[str, CodebaseIndex] = {}
        self.last_indexing = datetime.now()
        self.files_processed = 0
        self._setup_logging()
        self.load_neural_index()
        
    def _setup_logging(self):
        """Configura logging temático (como o diário de quest)"""
        if not logger.handlers:
            fh = logging.FileHandler("logs/neural_index.log")
            fh.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s'
            ))
            logger.addHandler(fh)
    
    def _check_system_state(self) -> str:
        """Verifica estado do sistema (como status check em RPG)"""
        if (datetime.now() - self.last_indexing).total_seconds() < SYSTEM_LIMITS["cooldown"]:
            return "resting"
        if self.files_processed >= SYSTEM_LIMITS["max_files"]:
            return "full"
        if self.files_processed >= SYSTEM_LIMITS["warning_threshold"]:
            return "warning"
        return "indexing"
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calcula checksum do arquivo"""
        sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"❌ Erro ao calcular checksum de {file_path}: {e}")
            return ""
            
    def analyze_file_concepts(self, file_path: Path) -> List[str]:
        """Analisa conceitos presentes no arquivo"""
        concepts = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                
            # Detecta padrões e conceitos
            if 'class' in content:
                concepts.append('oop')
            if 'async' in content:
                concepts.append('async')
            if 'test' in content:
                concepts.append('testing')
            if '@dataclass' in content:
                concepts.append('data')
            if 'import torch' in content:
                concepts.append('ml')
            if 'security' in content:
                concepts.append('security')
                
            return list(set(concepts))
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar conceitos de {file_path}: {e}")
            return []
            
    def find_dependencies(self, file_path: Path) -> Set[str]:
        """Encontra dependências do arquivo"""
        deps = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith(('import ', 'from ')):
                        deps.add(line.strip())
            return deps
            
        except Exception as e:
            logger.error(f"❌ Erro ao encontrar dependências de {file_path}: {e}")
            return set()
            
    def calculate_importance(self, file_path: Path, concepts: List[str]) -> float:
        """Calcula importância do arquivo"""
        importance = 0.5  # Base importance
        
        # Ajusta baseado em fatores
        if 'core' in str(file_path):
            importance += 0.2
        if 'test' in str(file_path):
            importance += 0.1
        if 'security' in concepts:
            importance += 0.15
        if 'ml' in concepts:
            importance += 0.1
            
        # Normaliza para 0.0-1.0
        return min(1.0, max(0.0, importance))
        
    async def index_file(self, file_path: Path) -> CodebaseIndex:
        """Indexa um arquivo"""
        try:
            # Coleta informações
            checksum = self.calculate_file_checksum(file_path)
            concepts = self.analyze_file_concepts(file_path)
            deps = self.find_dependencies(file_path)
            importance = self.calculate_importance(file_path, concepts)
            
            # Cria índice
            index = CodebaseIndex(
                file_path=str(file_path),
                last_modified=file_path.stat().st_mtime,
                checksum=checksum,
                dependencies=deps,
                concepts=concepts,
                importance=importance,
                neural_connections={}
            )
            
            self.neural_index[str(file_path)] = index
            return index
            
        except Exception as e:
            logger.error(f"❌ Erro ao indexar {file_path}: {e}")
            raise
            
    async def update_neural_connections(self):
        """Atualiza conexões neurais entre arquivos"""
        try:
            for path, index in self.neural_index.items():
                connections = {}
                
                for other_path, other_index in self.neural_index.items():
                    if path != other_path:
                        # Calcula força da conexão
                        connection = 0.0
                        
                        # Conceitos em comum
                        common_concepts = set(index.concepts) & set(other_index.concepts)
                        connection += len(common_concepts) * 0.2
                        
                        # Dependências em comum
                        common_deps = index.dependencies & other_index.dependencies
                        connection += len(common_deps) * 0.1
                        
                        # Mesmo diretório
                        if Path(path).parent == Path(other_path).parent:
                            connection += 0.3
                            
                        # Normaliza
                        connection = min(1.0, connection)
                        
                        if connection > 0:
                            connections[other_path] = connection
                            
                index.neural_connections = connections
                
            logger.info("✨ Conexões neurais atualizadas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar conexões: {e}")
            
    def save_neural_index(self):
        """Salva índice neural"""
        try:
            index_file = self.index_dir / "neural_index.json"
            
            # Converte para formato serializável
            data = {
                path: index.to_dict()
                for path, index in self.neural_index.items()
            }
            
            # Salva arquivo
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.info("✨ Índice neural salvo")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar índice: {e}")
            
    def load_neural_index(self):
        """Carrega índice neural"""
        try:
            index_file = self.index_dir / "neural_index.json"
            
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Converte de volta para objetos
                self.neural_index = {
                    path: CodebaseIndex.from_dict(index_data)
                    for path, index_data in data.items()
                }
                
                logger.info("✨ Índice neural carregado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar índice: {e}")
            
    async def index_codebase(self, root_dir: Path):
        """Indexa o codebase (como explorar uma dungeon)"""
        try:
            state = self._check_system_state()
            
            if state == "resting":
                logger.info(SYSTEM_STATES["resting"])
                return
                
            if state == "full":
                logger.warning(SYSTEM_STATES["full"])
                return
            
            # Processa em batches (como grupos de monstros)
            python_files = list(root_dir.rglob("*.py"))
            total_files = len(python_files)
            
            if total_files == 0:
                return
                
            # Mostra progresso como barra de HP
            progress = "█" * (20 * self.files_processed // total_files)
            remaining = "░" * (20 - len(progress))
            
            logger.info(f"🗺️ Explorando dungeon: {root_dir}")
            logger.info(f"📜 Pergaminhos encontrados: {total_files}")
            logger.info(f"[{progress}{remaining}] {self.files_processed}/{total_files}")
            
            # Processa arquivos em grupos
            for i in range(0, len(python_files), SYSTEM_LIMITS["batch_size"]):
                batch = python_files[i:i + SYSTEM_LIMITS["batch_size"]]
                for file in batch:
                    await self.index_file(file)
                    
                self.files_processed += len(batch)
                if self.files_processed >= SYSTEM_LIMITS["max_files"]:
                    logger.warning(SYSTEM_STATES["full"])
                    break
                    
            self.last_indexing = datetime.now()
            await self.update_neural_connections()
            
        except Exception as e:
            logger.error(f"{SYSTEM_STATES['error']}: {e}")
            
    def get_related_files(self, file_path: str, min_connection: float = 0.3) -> List[str]:
        """Retorna arquivos relacionados"""
        try:
            if file_path not in self.neural_index:
                return []
                
            index = self.neural_index[file_path]
            
            # Filtra por força mínima de conexão
            related = [
                path
                for path, strength in index.neural_connections.items()
                if strength >= min_connection
            ]
            
            return sorted(related, key=lambda p: index.neural_connections[p], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar arquivos relacionados: {e}")
            return []
            
    def get_important_files(self, min_importance: float = 0.7) -> List[str]:
        """Retorna arquivos importantes"""
        try:
            important = [
                path
                for path, index in self.neural_index.items()
                if index.importance >= min_importance
            ]
            
            return sorted(important, key=lambda p: self.neural_index[p].importance, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar arquivos importantes: {e}")
            return []

# Instância global do sistema
core_values = CoreValueSystem()