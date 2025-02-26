import redis
import json
import time
from datetime import datetime
import hashlib
from typing import Dict, List, Optional, Tuple
import logging
import aioredis
import os
from dataclasses import dataclass, asdict
import asyncio
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from dotenv import load_dotenv

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ava_memory.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AVAMemory')

load_dotenv()

@dataclass
class Memory:
    content: str
    context: Dict
    timestamp: datetime = None
    type: str = None
    importance: float = None
    emotions: List[str] = None
    topics: List[str] = None
    
    def __post_init__(self):
        self.timestamp = self.timestamp or datetime.now()
        self.type = self.type or self._determine_type()
        self.importance = self.importance or self._calculate_importance()
        self.emotions = self.emotions or self._extract_emotions()
        self.topics = self.topics or self._extract_topics()
        
    def _determine_type(self) -> str:
        """Determina o tipo da memória"""
        context = self.context
        if context.get("is_ethical_decision"):
            return "ethical"
        elif context.get("is_creative"):
            return "creative"
        elif context.get("is_learning"):
            return "learning"
        else:
            return "general"
            
    def _calculate_importance(self) -> float:
        """Calcula a importância da memória (0-1)"""
        importance = 0.5  # Base
        
        # Fatores que aumentam importância
        if self.context.get("ethical_impact", 0) > 0.7:
            importance += 0.2
        if self.context.get("emotional_intensity", 0) > 0.7:
            importance += 0.15
        if self.context.get("user_growth", 0) > 0.5:
            importance += 0.1
            
        return min(importance, 1.0)
        
    def _extract_emotions(self) -> List[str]:
        """Extrai emoções do contexto"""
        emotions = []
        if self.context.get("emotions"):
            emotions.extend(self.context["emotions"])
        return emotions
        
    def _extract_topics(self) -> List[str]:
        """Extrai tópicos do conteúdo"""
        topics = []
        if self.context.get("topics"):
            topics.extend(self.context["topics"])
        return topics
        
    def to_dict(self) -> Dict:
        """Converte memória para dicionário"""
        return {
            "content": self.content,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "type": self.type,
            "importance": self.importance,
            "emotions": self.emotions,
            "topics": self.topics
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Memory':
        """Cria memória a partir de dicionário"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

class MemoryIndex:
    """Índice para busca rápida de memórias"""
    def __init__(self):
        self.by_type = defaultdict(list)
        self.by_emotion = defaultdict(list)
        self.by_topic = defaultdict(list)
        self.by_importance = defaultdict(list)
        self.temporal_index = []  # Lista ordenada por timestamp
        
    def add(self, memory_id: str, memory: Memory):
        """Adiciona memória aos índices"""
        # Índice por tipo
        self.by_type[memory.type].append(memory_id)
        
        # Índice por emoções
        for emotion in memory.emotions:
            self.by_emotion[emotion].append(memory_id)
            
        # Índice por tópicos
        for topic in memory.topics:
            self.by_topic[topic].append(memory_id)
            
        # Índice por importância (buckets de 0.1)
        importance_bucket = int(memory.importance * 10)
        self.by_importance[importance_bucket].append(memory_id)
        
        # Índice temporal
        self.temporal_index.append((memory.timestamp, memory_id))
        self.temporal_index.sort(key=lambda x: x[0])
        
    def search(
        self,
        type: Optional[str] = None,
        emotions: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        min_importance: Optional[float] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[str]:
        """Busca IDs de memórias que atendem aos critérios"""
        candidate_sets = []
        
        # Filtra por tipo
        if type:
            candidate_sets.append(set(self.by_type[type]))
            
        # Filtra por emoções
        if emotions:
            emotion_memories = set()
            for emotion in emotions:
                emotion_memories.update(self.by_emotion[emotion])
            candidate_sets.append(emotion_memories)
            
        # Filtra por tópicos
        if topics:
            topic_memories = set()
            for topic in topics:
                topic_memories.update(self.by_topic[topic])
            candidate_sets.append(topic_memories)
            
        # Filtra por importância
        if min_importance is not None:
            min_bucket = int(min_importance * 10)
            importance_memories = set()
            for bucket in range(min_bucket, 10):
                importance_memories.update(self.by_importance[bucket])
            candidate_sets.append(importance_memories)
            
        # Filtra por tempo
        if start_time or end_time:
            time_memories = set()
            for timestamp, memory_id in self.temporal_index:
                if start_time and timestamp < start_time:
                    continue
                if end_time and timestamp > end_time:
                    break
                time_memories.add(memory_id)
            candidate_sets.append(time_memories)
            
        # Intersecção de todos os conjuntos
        if not candidate_sets:
            return []
            
        result = candidate_sets[0]
        for s in candidate_sets[1:]:
            result = result.intersection(s)
            
        return list(result)

class AVAMemory:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.mongo_client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.mongo_client.ava_memory
        
        # Memória de trabalho (curto prazo)
        self.working_memory = []
        self.working_memory_size = 10
        
        # Cache de embeddings
        self.embedding_cache = {}
        
        # Conexão Redis
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        
        # Cache local
        self.cache = {}
        self.cache_size = 1000
        self.cache_ttl = 3600  # 1 hora
        
        # Índices
        self.index = MemoryIndex()
        
        # Métricas
        self.metrics = {
            "total_memories": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "store_operations": 0,
            "retrieve_operations": 0
        }
        
    async def store(self, content: str, memory_type: str, context: Dict = None, 
                   emotions: Dict = None, importance: float = 0.5) -> str:
        """Armazena uma nova memória"""
        try:
            # Cria nova memória
            memory = Memory()
            memory.content = content
            memory.type = memory_type
            memory.context = context or {}
            memory.emotions = emotions or {}
            memory.importance = importance
            memory.embedding = self._generate_embedding(content)
            
            # Adiciona à memória de trabalho
            self.working_memory.append(memory)
            if len(self.working_memory) > self.working_memory_size:
                self._consolidate_memory()
                
            # Armazena no MongoDB
            memory_dict = memory.__dict__
            memory_dict['embedding'] = memory_dict['embedding'].tolist()
            result = self.db.memories.insert_one(memory_dict)
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Erro ao armazenar memória: {str(e)}")
            raise
            
    async def retrieve(self, query: str, limit: int = 5) -> List[Dict]:
        """Recupera memórias relevantes baseado em uma query"""
        try:
            query_embedding = self._generate_embedding(query)
            
            # Busca na memória de trabalho
            working_results = self._search_working_memory(query_embedding, limit)
            
            # Busca no MongoDB
            db_results = await self._search_long_term_memory(query_embedding, limit)
            
            # Combina e ordena resultados
            all_results = working_results + db_results
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return all_results[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao recuperar memórias: {str(e)}")
            raise
            
    async def learn(self, content: str, source: str, metadata: Dict = None):
        """Aprende novo conhecimento e o integra à base existente"""
        try:
            # Verifica conhecimento existente
            existing = await self.retrieve(content, limit=1)
            
            if existing and existing[0]['similarity'] > 0.95:
                # Atualiza conhecimento existente
                memory_id = existing[0]['_id']
                self.db.memories.update_one(
                    {'_id': memory_id},
                    {'$set': {
                        'last_accessed': datetime.now(),
                        'access_count': existing[0].get('access_count', 0) + 1,
                        'metadata': {**existing[0].get('metadata', {}), **(metadata or {})}
                    }}
                )
            else:
                # Armazena novo conhecimento
                await self.store(
                    content=content,
                    memory_type='semantic',
                    context={'source': source},
                    importance=0.7,
                    emotions={'curiosity': 0.8}
                )
                
        except Exception as e:
            logger.error(f"Erro ao aprender novo conhecimento: {str(e)}")
            raise
            
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Gera embedding para um texto"""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
            
        embedding = self.model.encode(text)
        self.embedding_cache[text] = embedding
        
        return embedding
        
    def _search_working_memory(self, query_embedding: np.ndarray, limit: int) -> List[Dict]:
        """Busca na memória de trabalho"""
        results = []
        
        for memory in self.working_memory:
            similarity = np.dot(query_embedding, memory.embedding)
            results.append({
                'content': memory.content,
                'type': memory.type,
                'context': memory.context,
                'similarity': similarity,
                'source': 'working_memory'
            })
            
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
        
    async def _search_long_term_memory(self, query_embedding: np.ndarray, limit: int) -> List[Dict]:
        """Busca na memória de longo prazo (MongoDB)"""
        # Converte embedding para lista
        query_list = query_embedding.tolist()
        
        # Busca usando produto escalar
        pipeline = [
            {
                '$addFields': {
                    'similarity': {
                        '$reduce': {
                            'input': {'$zip': {'inputs': ['$embedding', query_list]}},
                            'initialValue': 0,
                            'in': {'$add': ['$$value', {'$multiply': ['$$this.0', '$$this.1']}]}
                        }
                    }
                }
            },
            {'$sort': {'similarity': -1}},
            {'$limit': limit}
        ]
        
        results = list(self.db.memories.aggregate(pipeline))
        
        # Processa resultados
        for result in results:
            result['source'] = 'long_term_memory'
            del result['embedding']  # Remove embedding do resultado
            
        return results
        
    def _consolidate_memory(self):
        """Consolida memórias de trabalho em memória de longo prazo"""
        # Ordena por importância
        self.working_memory.sort(key=lambda x: x.importance, reverse=True)
        
        # Mantém apenas as mais importantes na memória de trabalho
        excess_memories = self.working_memory[self.working_memory_size:]
        self.working_memory = self.working_memory[:self.working_memory_size]
        
        # Armazena as demais no MongoDB
        for memory in excess_memories:
            memory_dict = memory.__dict__
            memory_dict['embedding'] = memory_dict['embedding'].tolist()
            self.db.memories.insert_one(memory_dict)
        
    def get_metrics(self) -> Dict:
        """Retorna métricas do sistema de memória"""
        return {
            **self.metrics,
            "cache_size": len(self.cache),
            "index_stats": {
                "types": len(self.index.by_type),
                "emotions": len(self.index.by_emotion),
                "topics": len(self.index.by_topic)
            }
        }
        
    async def cleanup(self, max_age_days: int = 30):
        """Remove memórias antigas"""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        
        # Remove do Redis e cache
        for memory_id, memory in self.cache.items():
            if memory.timestamp < cutoff:
                await self.redis.delete(f"memory:{memory_id}")
                del self.cache[memory_id]
                
        # Reconstrói índices
        self.index = MemoryIndex()
        for memory_id, memory in self.cache.items():
            self.index.add(memory_id, memory) 