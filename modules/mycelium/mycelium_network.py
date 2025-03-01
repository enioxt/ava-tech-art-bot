#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
import random
import time
from datetime import datetime
from threading import Thread, Lock

# Configuração de logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/mycelium.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MyceliumNode:
    """Representa um nó individual na rede Mycelium"""
    
    def __init__(self, node_id, node_type, capacity):
        self.node_id = node_id
        self.node_type = node_type
        self.capacity = capacity
        self.connections = []
        self.data = {}
        self.status = "active"
        self.last_update = datetime.now()
        
    def connect(self, target_node):
        """Estabelece conexão com outro nó"""
        if target_node.node_id not in [conn.node_id for conn in self.connections]:
            self.connections.append(target_node)
            logger.debug(f"Nó {self.node_id} conectado ao nó {target_node.node_id}")
            return True
        return False
        
    def store_data(self, key, value):
        """Armazena dados no nó"""
        self.data[key] = value
        self.last_update = datetime.now()
        
    def retrieve_data(self, key):
        """Recupera dados do nó"""
        return self.data.get(key)
        
    def to_dict(self):
        """Converte o nó para dicionário"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "capacity": self.capacity,
            "connections": len(self.connections),
            "data_keys": list(self.data.keys()),
            "status": self.status,
            "last_update": self.last_update.isoformat()
        }

class MyceliumNetwork:
    """
    Rede Mycelium para EVA & GUARANI.
    Implementa um sistema de processamento distribuído inspirado em redes miceliais.
    """
    
    def __init__(self, config_path='config/quantum_config.json'):
        self.nodes = []
        self.node_types = ["storage", "processing", "interface", "quantum"]
        self.lock = Lock()
        self.active = True
        self.load_config(config_path)
        self.initialize_network()
        self._start_background_process()
        logger.info("Rede Mycelium inicializada")
        
    def load_config(self, config_path):
        """Carrega configurações do sistema quântico"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.total_nodes = config.get('mycelium_connections', 1024)
                logger.info(f"Configuração carregada: {self.total_nodes} nós")
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            self.total_nodes = 1024
            
    def initialize_network(self):
        """Inicializa a rede com nós aleatórios"""
        for i in range(self.total_nodes):
            node_type = random.choice(self.node_types)
            capacity = random.randint(1, 10) * 10
            node = MyceliumNode(f"node-{i}", node_type, capacity)
            self.nodes.append(node)
            
        # Criar conexões aleatórias entre nós
        for node in self.nodes:
            # Cada nó se conecta a 3-10 outros nós aleatórios
            connections = random.randint(3, min(10, len(self.nodes)-1))
            potential_connections = [n for n in self.nodes if n.node_id != node.node_id]
            for target in random.sample(potential_connections, connections):
                node.connect(target)
                
        logger.info(f"Rede inicializada com {len(self.nodes)} nós e conexões aleatórias")
        
    def _background_process(self):
        """Processo em segundo plano para simular atividade da rede"""
        while self.active:
            with self.lock:
                # Simular transferência de dados entre nós
                for _ in range(min(100, len(self.nodes))):
                    source_node = random.choice(self.nodes)
                    if source_node.connections:
                        target_node = random.choice(source_node.connections)
                        data_key = f"data-{int(time.time())}-{random.randint(1000, 9999)}"
                        data_value = random.random()
                        source_node.store_data(data_key, data_value)
                        target_node.store_data(data_key, data_value)
                        
                # Ocasionalmente adicionar ou remover nós
                if random.random() < 0.05:  # 5% de chance
                    if random.random() < 0.7:  # 70% de chance de adicionar
                        self._add_node()
                    else:  # 30% de chance de remover
                        self._remove_node()
                        
            time.sleep(5)  # Aguardar 5 segundos entre ciclos
            
    def _start_background_process(self):
        """Inicia o processo em segundo plano"""
        thread = Thread(target=self._background_process)
        thread.daemon = True
        thread.start()
        logger.info("Processo em segundo plano iniciado")
        
    def _add_node(self):
        """Adiciona um novo nó à rede"""
        node_type = random.choice(self.node_types)
        capacity = random.randint(1, 10) * 10
        node_id = f"node-{len(self.nodes)}"
        node = MyceliumNode(node_id, node_type, capacity)
        
        # Conectar a alguns nós existentes
        connections = random.randint(2, min(5, len(self.nodes)))
        for target in random.sample(self.nodes, connections):
            node.connect(target)
            target.connect(node)
            
        self.nodes.append(node)
        logger.info(f"Nó adicionado: {node_id}")
        
    def _remove_node(self):
        """Remove um nó da rede"""
        if len(self.nodes) > 10:  # Manter pelo menos 10 nós
            node = random.choice(self.nodes)
            self.nodes.remove(node)
            logger.info(f"Nó removido: {node.node_id}")
            
    def get_network_status(self):
        """Retorna o status atual da rede"""
        with self.lock:
            active_nodes = sum(1 for node in self.nodes if node.status == "active")
            node_types_count = {}
            for node in self.nodes:
                node_types_count[node.node_type] = node_types_count.get(node.node_type, 0) + 1
                
            total_connections = sum(len(node.connections) for node in self.nodes)
            avg_connections = total_connections / len(self.nodes) if self.nodes else 0
            
            return {
                "total_nodes": len(self.nodes),
                "active_nodes": active_nodes,
                "node_types": node_types_count,
                "total_connections": total_connections,
                "average_connections_per_node": avg_connections,
                "network_health": (active_nodes / len(self.nodes)) * 100 if self.nodes else 0,
                "timestamp": datetime.now().isoformat()
            }
            
    def process_data(self, data, processing_type="distributed"):
        """
        Processa dados através da rede Mycelium
        Simula processamento distribuído através dos nós
        """
        with self.lock:
            if not self.nodes:
                return {"error": "Rede sem nós disponíveis"}
                
            # Selecionar nós para processamento
            if processing_type == "distributed":
                # Usar múltiplos nós para processamento paralelo
                processing_nodes = random.sample(
                    [n for n in self.nodes if n.node_type == "processing" and n.status == "active"],
                    min(5, sum(1 for n in self.nodes if n.node_type == "processing" and n.status == "active"))
                )
            else:
                # Usar um único nó para processamento sequencial
                processing_nodes = [random.choice([n for n in self.nodes if n.status == "active"])]
                
            if not processing_nodes:
                return {"error": "Nenhum nó de processamento disponível"}
                
            # Simular processamento
            processing_time = random.uniform(0.1, 2.0)
            time.sleep(processing_time)
            
            # Armazenar resultado em nós de armazenamento
            result = {
                "input_data_hash": hash(str(data)),
                "processing_time": processing_time,
                "nodes_involved": [node.node_id for node in processing_nodes],
                "timestamp": datetime.now().isoformat(),
                "result": f"Processed data with {len(processing_nodes)} nodes"
            }
            
            # Armazenar o resultado em nós de armazenamento
            storage_nodes = [n for n in self.nodes if n.node_type == "storage" and n.status == "active"]
            if storage_nodes:
                result_key = f"result-{int(time.time())}"
                for node in random.sample(storage_nodes, min(3, len(storage_nodes))):
                    node.store_data(result_key, result)
                    
            logger.info(f"Dados processados por {len(processing_nodes)} nós em {processing_time:.2f}s")
            return result
            
    def shutdown(self):
        """Desliga a rede Mycelium"""
        self.active = False
        logger.info("Rede Mycelium desligada")

# Função para teste do módulo
if __name__ == "__main__":
    mycelium = MyceliumNetwork()
    print(json.dumps(mycelium.get_network_status(), indent=2))
    print(json.dumps(mycelium.process_data({"test": "data"}), indent=2))
    time.sleep(10)  # Permitir que o processo em segundo plano execute
    print(json.dumps(mycelium.get_network_status(), indent=2))
    mycelium.shutdown()
    
# EVA & GUARANI | Sistema Quântico 