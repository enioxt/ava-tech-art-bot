from typing import Dict, List, Optional, Union
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdaptiveCache:
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hit_count = 0
        self.miss_count = 0
        self.last_optimization = datetime.now()
        
    async def get(self, key: str) -> Optional[Dict]:
        if key in self.cache:
            self.hit_count += 1
            self.cache.move_to_end(key)
            return self.cache[key]
        self.miss_count += 1
        return None
        
    async def put(self, key: str, value: Dict, priority: float = 0.5) -> None:
        if len(self.cache) >= self.max_size:
            # Remove item com menor prioridade
            lowest_priority = min(self.cache.items(), key=lambda x: x[1].get('priority', 0))
            self.cache.pop(lowest_priority[0])
        
        value['priority'] = priority
        self.cache[key] = value
        self.cache.move_to_end(key)
        
    async def optimize(self) -> None:
        if (datetime.now() - self.last_optimization).seconds > 3600:
            hit_rate = self.hit_count / (self.hit_count + self.miss_count + 1)
            if hit_rate < 0.5:
                # Ajusta tamanho do cache baseado na taxa de acertos
                self.max_size = int(self.max_size * 1.2)
            self.last_optimization = datetime.now()

class MemorySystem:
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o sistema de memória.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração.
        """
        self.config = self._load_config(config_path)
        self.memory_types = {
            'episodic': [],    # Experiências específicas
            'semantic': {},    # Conhecimento geral
            'procedural': [],  # Habilidades e processos
            'emotional': []    # Respostas emocionais
        }
        
        self.memory_weights = {
            'importance': 0.4,
            'recency': 0.3,
            'frequency': 0.2,
            'emotional_impact': 0.1
        }
        
        self.embeddings = {}  # Armazena embeddings para busca semântica
        self.cache = AdaptiveCache(max_size=self.config['memory']['short_term_limit'])
        logger.info("MemorySystem initialized successfully")
    
    def _load_config(self, config_path: Optional[str]) -> dict:
        """
        Carrega a configuração do sistema.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração.
            
        Returns:
            dict: Configuração carregada
        """
        default_config = {
            'memory': {
                'episodic_limit': 1000,
                'semantic_limit': 5000,
                'procedural_limit': 500,
                'emotional_limit': 300,
                'consolidation_threshold': 0.8,
                'forgetting_rate': 0.001,
                'short_term_limit': 1000
            },
            'embedding': {
                'dimension': 768,
                'similarity_threshold': 0.85
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                return default_config
        return default_config
    
    async def store(self, memory_data: Dict) -> None:
        """
        Armazena uma nova memória no sistema.
        
        Args:
            memory_data (Dict): Dados da memória para armazenamento
        """
        try:
            processed_memory = await self._process_memory(memory_data)
            memory_type = await self._classify_memory(processed_memory)
            
            # Calcula prioridade baseada em importância e recência
            priority = self._calculate_importance(processed_memory)
            
            # Armazena no cache adaptativo
            await self.cache.put(
                key=f"{memory_type}_{datetime.now().timestamp()}",
                value=processed_memory,
                priority=priority
            )
            
            # Otimiza cache se necessário
            await self.cache.optimize()
            
            await self._consolidate_memory(processed_memory, memory_type)
            
            logger.info(f"Memory stored successfully: {memory_type}")
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            raise
    
    async def retrieve(self, query: Dict, memory_type: Optional[str] = None) -> List[Dict]:
        """
        Recupera memórias baseado em uma consulta.
        
        Args:
            query (Dict): Consulta para busca de memórias
            memory_type (str, optional): Tipo específico de memória para buscar
            
        Returns:
            List[Dict]: Lista de memórias recuperadas
        """
        try:
            # 1. Geração de embedding para a consulta
            query_embedding = await self._generate_embedding(query)
            
            # 2. Busca por similaridade
            memories = await self._search_memories(query_embedding, memory_type)
            
            # 3. Ordenação por relevância
            sorted_memories = self._sort_by_relevance(memories, query)
            
            # 4. Aplicação de contexto
            contextualized = await self._apply_context(sorted_memories, query)
            
            return contextualized
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            raise
    
    async def _classify_memory(self, memory_data: Dict) -> str:
        """
        Classifica o tipo de memória baseado nos dados.
        
        Args:
            memory_data (Dict): Dados da memória
            
        Returns:
            str: Tipo de memória classificado
        """
        # Análise de características
        features = {
            'episodic': self._calculate_episodic_score(memory_data),
            'semantic': self._calculate_semantic_score(memory_data),
            'procedural': self._calculate_procedural_score(memory_data),
            'emotional': self._calculate_emotional_score(memory_data)
        }
        
        # Retorna o tipo com maior score
        return max(features.items(), key=lambda x: x[1])[0]
    
    async def _process_memory(self, memory_data: Dict) -> Dict:
        """
        Processa os dados da memória para armazenamento.
        
        Args:
            memory_data (Dict): Dados brutos da memória
            
        Returns:
            Dict: Dados processados
        """
        processed = {
            'data': memory_data,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'importance': self._calculate_importance(memory_data),
                'emotional_impact': self._calculate_emotional_impact(memory_data),
                'complexity': self._calculate_complexity(memory_data)
            },
            'embedding': await self._generate_embedding(memory_data),
            'associations': await self._find_associations(memory_data)
        }
        
        return processed
    
    async def _consolidate_memory(self, processed_memory: Dict, memory_type: str) -> None:
        """
        Consolida uma memória processada no sistema.
        
        Args:
            processed_memory (Dict): Memória processada
            memory_type (str): Tipo de memória
        """
        # Verifica limites
        if len(self.memory_types[memory_type]) >= self.config['memory'][f'{memory_type}_limit']:
            await self._forget_memories(memory_type)
        
        # Adiciona nova memória
        self.memory_types[memory_type].append(processed_memory)
        
        # Atualiza embeddings
        self.embeddings[memory_type] = np.vstack([
            self.embeddings.get(memory_type, np.array([])),
            processed_memory['embedding']
        ])
    
    async def _optimize_storage(self) -> None:
        """Otimiza o armazenamento de memória."""
        for memory_type in self.memory_types:
            # Remove memórias duplicadas
            await self._remove_duplicates(memory_type)
            
            # Compacta memórias similares
            await self._compact_memories(memory_type)
            
            # Atualiza importância
            await self._update_importance(memory_type)
    
    async def _generate_embedding(self, data: Dict) -> np.ndarray:
        """
        Gera um embedding para os dados.
        
        Args:
            data (Dict): Dados para gerar embedding
            
        Returns:
            np.ndarray: Embedding gerado
        """
        # Implementação básica - deve ser substituída por um modelo real
        return np.random.rand(self.config['embedding']['dimension'])
    
    async def _search_memories(self, query_embedding: np.ndarray, memory_type: Optional[str] = None) -> List[Dict]:
        """
        Busca memórias similares ao embedding da consulta.
        
        Args:
            query_embedding (np.ndarray): Embedding da consulta
            memory_type (str, optional): Tipo específico de memória
            
        Returns:
            List[Dict]: Memórias similares encontradas
        """
        results = []
        types_to_search = [memory_type] if memory_type else self.memory_types.keys()
        
        for mtype in types_to_search:
            if mtype in self.embeddings and len(self.embeddings[mtype]) > 0:
                similarities = cosine_similarity([query_embedding], self.embeddings[mtype])[0]
                
                # Filtra por threshold
                threshold = self.config['embedding']['similarity_threshold']
                matches = [(i, sim) for i, sim in enumerate(similarities) if sim >= threshold]
                
                # Adiciona memórias correspondentes
                for idx, sim in matches:
                    memory = self.memory_types[mtype][idx]
                    memory['similarity'] = float(sim)
                    results.append(memory)
        
        return results
    
    def _sort_by_relevance(self, memories: List[Dict], query: Dict) -> List[Dict]:
        """
        Ordena memórias por relevância.
        
        Args:
            memories (List[Dict]): Lista de memórias
            query (Dict): Consulta original
            
        Returns:
            List[Dict]: Memórias ordenadas
        """
        def calculate_relevance(memory: Dict) -> float:
            return (
                memory['similarity'] * self.memory_weights['importance'] +
                memory['metadata']['importance'] * self.memory_weights['importance'] +
                memory['metadata']['emotional_impact'] * self.memory_weights['emotional_impact']
            )
        
        return sorted(memories, key=calculate_relevance, reverse=True)
    
    async def _apply_context(self, memories: List[Dict], query: Dict) -> List[Dict]:
        """
        Aplica contexto às memórias recuperadas.
        
        Args:
            memories (List[Dict]): Lista de memórias
            query (Dict): Consulta original
            
        Returns:
            List[Dict]: Memórias com contexto
        """
        for memory in memories:
            memory['context'] = {
                'query_relevance': memory.get('similarity', 0.0),
                'temporal_distance': self._calculate_temporal_distance(memory),
                'emotional_alignment': self._calculate_emotional_alignment(memory, query)
            }
        
        return memories
    
    def _calculate_importance(self, data: Dict) -> float:
        """Calcula a importância dos dados."""
        # Implementação básica - pode ser expandida
        return 0.7
    
    def _calculate_emotional_impact(self, data: Dict) -> float:
        """Calcula o impacto emocional dos dados."""
        # Implementação básica - pode ser expandida
        return 0.5
    
    def _calculate_complexity(self, data: Dict) -> float:
        """Calcula a complexidade dos dados."""
        # Implementação básica - pode ser expandida
        return 0.6
    
    def _calculate_episodic_score(self, data: Dict) -> float:
        """Calcula o score para memória episódica."""
        # Implementação básica - pode ser expandida
        return 0.7
    
    def _calculate_semantic_score(self, data: Dict) -> float:
        """Calcula o score para memória semântica."""
        # Implementação básica - pode ser expandida
        return 0.6
    
    def _calculate_procedural_score(self, data: Dict) -> float:
        """Calcula o score para memória procedural."""
        # Implementação básica - pode ser expandida
        return 0.5
    
    def _calculate_emotional_score(self, data: Dict) -> float:
        """Calcula o score para memória emocional."""
        # Implementação básica - pode ser expandida
        return 0.4
    
    async def _find_associations(self, data: Dict) -> List[Dict]:
        """Encontra associações entre memórias."""
        # Implementação básica - pode ser expandida
        return []
    
    async def _forget_memories(self, memory_type: str) -> None:
        """
        Remove memórias menos importantes quando necessário.
        
        Args:
            memory_type (str): Tipo de memória para esquecer
        """
        memories = self.memory_types[memory_type]
        if not memories:
            return
        
        # Ordena por importância
        sorted_memories = sorted(
            memories,
            key=lambda x: x['metadata']['importance'],
            reverse=True
        )
        
        # Mantém apenas as mais importantes
        limit = self.config['memory'][f'{memory_type}_limit']
        self.memory_types[memory_type] = sorted_memories[:limit]
        
        # Atualiza embeddings
        self.embeddings[memory_type] = np.array([
            m['embedding'] for m in self.memory_types[memory_type]
        ])
    
    async def _remove_duplicates(self, memory_type: str) -> None:
        """Remove memórias duplicadas."""
        # Implementação básica - pode ser expandida
        pass
    
    async def _compact_memories(self, memory_type: str) -> None:
        """Compacta memórias similares."""
        # Implementação básica - pode ser expandida
        pass
    
    async def _update_importance(self, memory_type: str) -> None:
        """Atualiza a importância das memórias."""
        # Implementação básica - pode ser expandida
        pass
    
    def _calculate_temporal_distance(self, memory: Dict) -> float:
        """Calcula a distância temporal de uma memória."""
        # Implementação básica - pode ser expandida
        return 0.5
    
    def _calculate_emotional_alignment(self, memory: Dict, query: Dict) -> float:
        """Calcula o alinhamento emocional entre memória e consulta."""
        # Implementação básica - pode ser expandida
        return 0.6

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        memory_system = MemorySystem()
        
        test_memory = {
            'type': 'experience',
            'content': {
                'message': 'Learning about consciousness',
                'emotion': 'curiosity',
                'importance': 0.8
            }
        }
        
        # Armazena memória
        await memory_system.store(test_memory)
        
        # Recupera memórias similares
        query = {
            'type': 'search',
            'content': {
                'topic': 'consciousness',
                'emotion': 'curiosity'
            }
        }
        
        results = await memory_system.retrieve(query)
        print(f"Retrieved memories: {json.dumps(results, indent=2, default=str)}")
    
    asyncio.run(main()) 