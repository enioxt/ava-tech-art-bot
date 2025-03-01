#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
import random
import time
import math
from datetime import datetime
from threading import Thread, Lock

# Configuração de logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/quantum_entanglement.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QuantumParticle:
    """Representa uma partícula quântica no sistema de entrelaçamento"""
    
    def __init__(self, particle_id, state=None):
        self.particle_id = particle_id
        # Estado quântico: None = superposição, 0 ou 1 = estado colapsado
        self.state = state
        self.entangled_particles = []
        self.creation_time = datetime.now()
        self.last_interaction = self.creation_time
        
    def entangle_with(self, particle):
        """Entrelaça esta partícula com outra"""
        if particle.particle_id not in [p.particle_id for p in self.entangled_particles]:
            self.entangled_particles.append(particle)
            particle.entangled_particles.append(self)
            self.last_interaction = datetime.now()
            particle.last_interaction = datetime.now()
            logger.debug(f"Partículas {self.particle_id} e {particle.particle_id} entrelaçadas")
            return True
        return False
        
    def measure(self):
        """Mede o estado da partícula, colapsando sua superposição"""
        if self.state is None:
            # Colapsar para um estado definido (0 ou 1)
            self.state = random.choice([0, 1])
            
            # Propagar o colapso para partículas entrelaçadas
            for particle in self.entangled_particles:
                if particle.state is None:
                    # Partículas entrelaçadas têm estados correlacionados
                    particle.state = self.state
                    particle.last_interaction = datetime.now()
                    logger.debug(f"Estado da partícula {particle.particle_id} colapsado para {particle.state} devido ao entrelaçamento")
            
            self.last_interaction = datetime.now()
            logger.debug(f"Estado da partícula {self.particle_id} medido como {self.state}")
        
        return self.state
        
    def reset(self):
        """Reinicia a partícula para o estado de superposição"""
        self.state = None
        self.last_interaction = datetime.now()
        logger.debug(f"Partícula {self.particle_id} reiniciada para estado de superposição")
        
    def to_dict(self):
        """Converte a partícula para dicionário"""
        return {
            "particle_id": self.particle_id,
            "state": self.state,
            "entangled_count": len(self.entangled_particles),
            "entangled_with": [p.particle_id for p in self.entangled_particles],
            "creation_time": self.creation_time.isoformat(),
            "last_interaction": self.last_interaction.isoformat()
        }

class QuantumEntanglement:
    """
    Sistema de Entrelaçamento Quântico para EVA & GUARANI.
    Simula o comportamento de partículas quânticas entrelaçadas.
    """
    
    def __init__(self, config_path='config/quantum_config.json'):
        self.particles = {}
        self.entanglement_pairs = []
        self.lock = Lock()
        self.active = True
        self.load_config(config_path)
        self.initialize_particles()
        self._start_background_process()
        logger.info("Sistema de Entrelaçamento Quântico inicializado")
        
    def load_config(self, config_path):
        """Carrega configurações do sistema quântico"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.total_particles = config.get('quantum_particles', 256)
                self.entanglement_factor = config.get('entanglement_factor', 0.95)
                logger.info(f"Configuração carregada: {self.total_particles} partículas, fator de entrelaçamento {self.entanglement_factor}")
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            self.total_particles = 256
            self.entanglement_factor = 0.95
            
    def initialize_particles(self):
        """Inicializa as partículas quânticas"""
        for i in range(self.total_particles):
            particle_id = f"q-{i}"
            self.particles[particle_id] = QuantumParticle(particle_id)
            
        # Criar entrelaçamentos iniciais
        self._create_initial_entanglements()
        logger.info(f"Sistema inicializado com {len(self.particles)} partículas e {len(self.entanglement_pairs)} pares entrelaçados")
        
    def _create_initial_entanglements(self):
        """Cria entrelaçamentos iniciais entre partículas"""
        particle_ids = list(self.particles.keys())
        
        # Determinar número de entrelaçamentos iniciais
        num_entanglements = int(len(particle_ids) * self.entanglement_factor / 2)
        
        for _ in range(num_entanglements):
            # Selecionar duas partículas aleatórias
            if len(particle_ids) < 2:
                break
                
            p1_id = random.choice(particle_ids)
            particle_ids.remove(p1_id)
            
            p2_id = random.choice(particle_ids)
            particle_ids.remove(p2_id)
            
            # Entrelaçar as partículas
            p1 = self.particles[p1_id]
            p2 = self.particles[p2_id]
            
            if p1.entangle_with(p2):
                self.entanglement_pairs.append((p1_id, p2_id))
                
    def _background_process(self):
        """Processo em segundo plano para simular comportamento quântico"""
        while self.active:
            with self.lock:
                # Simular medições aleatórias
                for _ in range(min(10, len(self.particles))):
                    particle_id = random.choice(list(self.particles.keys()))
                    particle = self.particles[particle_id]
                    
                    # 20% de chance de medir a partícula
                    if random.random() < 0.2:
                        state = particle.measure()
                        logger.debug(f"Medição automática da partícula {particle_id}: {state}")
                        
                # Ocasionalmente criar novos entrelaçamentos
                if random.random() < 0.1:  # 10% de chance
                    self._create_new_entanglement()
                    
                # Ocasionalmente reiniciar algumas partículas
                if random.random() < 0.05:  # 5% de chance
                    self._reset_random_particles()
                    
            time.sleep(2)  # Aguardar 2 segundos entre ciclos
            
    def _start_background_process(self):
        """Inicia o processo em segundo plano"""
        thread = Thread(target=self._background_process)
        thread.daemon = True
        thread.start()
        logger.info("Processo em segundo plano iniciado")
        
    def _create_new_entanglement(self):
        """Cria um novo entrelaçamento entre partículas não entrelaçadas"""
        with self.lock:
            # Encontrar partículas com menos entrelaçamentos
            particles_by_entanglement = sorted(
                self.particles.values(),
                key=lambda p: len(p.entangled_particles)
            )
            
            # Tentar entrelaçar as duas partículas com menos entrelaçamentos
            if len(particles_by_entanglement) >= 2:
                p1 = particles_by_entanglement[0]
                
                # Encontrar uma partícula não entrelaçada com p1
                for p2 in particles_by_entanglement[1:]:
                    if p2.particle_id not in [ep.particle_id for ep in p1.entangled_particles]:
                        if p1.entangle_with(p2):
                            self.entanglement_pairs.append((p1.particle_id, p2.particle_id))
                            logger.info(f"Novo entrelaçamento criado: {p1.particle_id} <-> {p2.particle_id}")
                            break
                            
    def _reset_random_particles(self):
        """Reinicia algumas partículas aleatórias para o estado de superposição"""
        with self.lock:
            # Selecionar algumas partículas aleatórias para reiniciar
            num_to_reset = random.randint(1, max(1, int(len(self.particles) * 0.05)))
            particles_to_reset = random.sample(list(self.particles.values()), num_to_reset)
            
            for particle in particles_to_reset:
                particle.reset()
                
            logger.debug(f"Reiniciadas {num_to_reset} partículas para estado de superposição")
            
    def measure_particle(self, particle_id):
        """Mede o estado de uma partícula específica"""
        with self.lock:
            if particle_id in self.particles:
                particle = self.particles[particle_id]
                state = particle.measure()
                logger.info(f"Partícula {particle_id} medida: {state}")
                return state
            else:
                logger.warning(f"Partícula {particle_id} não encontrada")
                return None
                
    def entangle_particles(self, particle_id1, particle_id2):
        """Entrelaça duas partículas específicas"""
        with self.lock:
            if particle_id1 in self.particles and particle_id2 in self.particles:
                p1 = self.particles[particle_id1]
                p2 = self.particles[particle_id2]
                
                if p1.entangle_with(p2):
                    self.entanglement_pairs.append((particle_id1, particle_id2))
                    logger.info(f"Partículas {particle_id1} e {particle_id2} entrelaçadas manualmente")
                    return True
                else:
                    logger.warning(f"Partículas {particle_id1} e {particle_id2} já estão entrelaçadas")
                    return False
            else:
                logger.warning(f"Uma ou ambas as partículas não encontradas: {particle_id1}, {particle_id2}")
                return False
                
    def reset_particle(self, particle_id):
        """Reinicia uma partícula específica para o estado de superposição"""
        with self.lock:
            if particle_id in self.particles:
                particle = self.particles[particle_id]
                particle.reset()
                logger.info(f"Partícula {particle_id} reiniciada manualmente")
                return True
            else:
                logger.warning(f"Partícula {particle_id} não encontrada")
                return False
                
    def get_particle_state(self, particle_id):
        """Retorna o estado atual de uma partícula sem medi-la"""
        with self.lock:
            if particle_id in self.particles:
                particle = self.particles[particle_id]
                return {
                    "particle_id": particle_id,
                    "state": particle.state,
                    "entangled_with": [p.particle_id for p in particle.entangled_particles],
                    "last_interaction": particle.last_interaction.isoformat()
                }
            else:
                logger.warning(f"Partícula {particle_id} não encontrada")
                return None
                
    def get_entanglement_status(self):
        """Retorna o status atual do sistema de entrelaçamento"""
        with self.lock:
            total_particles = len(self.particles)
            measured_particles = sum(1 for p in self.particles.values() if p.state is not None)
            superposition_particles = total_particles - measured_particles
            
            # Calcular estatísticas de entrelaçamento
            entanglement_counts = [len(p.entangled_particles) for p in self.particles.values()]
            avg_entanglement = sum(entanglement_counts) / total_particles if total_particles > 0 else 0
            max_entanglement = max(entanglement_counts) if entanglement_counts else 0
            
            # Calcular distribuição de estados
            state_0_count = sum(1 for p in self.particles.values() if p.state == 0)
            state_1_count = sum(1 for p in self.particles.values() if p.state == 1)
            
            return {
                "total_particles": total_particles,
                "measured_particles": measured_particles,
                "superposition_particles": superposition_particles,
                "total_entanglements": len(self.entanglement_pairs),
                "average_entanglements_per_particle": avg_entanglement,
                "max_entanglements": max_entanglement,
                "state_distribution": {
                    "state_0": state_0_count,
                    "state_1": state_1_count,
                    "superposition": superposition_particles
                },
                "entanglement_factor": self.entanglement_factor,
                "timestamp": datetime.now().isoformat()
            }
            
    def process_quantum_operation(self, operation_type, params=None):
        """
        Processa uma operação quântica no sistema
        
        Tipos de operação:
        - "measure": Mede uma partícula
        - "entangle": Entrelaça duas partículas
        - "reset": Reinicia uma partícula
        - "status": Retorna o status do sistema
        """
        with self.lock:
            if operation_type == "measure":
                if params and "particle_id" in params:
                    return {
                        "operation": "measure",
                        "result": self.measure_particle(params["particle_id"]),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": "Parâmetro particle_id não fornecido"}
                    
            elif operation_type == "entangle":
                if params and "particle_id1" in params and "particle_id2" in params:
                    success = self.entangle_particles(params["particle_id1"], params["particle_id2"])
                    return {
                        "operation": "entangle",
                        "success": success,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": "Parâmetros particle_id1 e particle_id2 não fornecidos"}
                    
            elif operation_type == "reset":
                if params and "particle_id" in params:
                    success = self.reset_particle(params["particle_id"])
                    return {
                        "operation": "reset",
                        "success": success,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": "Parâmetro particle_id não fornecido"}
                    
            elif operation_type == "status":
                return {
                    "operation": "status",
                    "result": self.get_entanglement_status(),
                    "timestamp": datetime.now().isoformat()
                }
                
            else:
                return {"error": f"Operação desconhecida: {operation_type}"}
                
    def create_quantum_circuit(self, num_particles=5):
        """
        Cria um circuito quântico simples com partículas entrelaçadas
        Retorna os IDs das partículas no circuito
        """
        with self.lock:
            # Criar novas partículas para o circuito
            circuit_particles = []
            for i in range(num_particles):
                particle_id = f"circuit-{int(time.time())}-{i}"
                self.particles[particle_id] = QuantumParticle(particle_id)
                circuit_particles.append(particle_id)
                
            # Entrelaçar as partículas em sequência
            for i in range(len(circuit_particles) - 1):
                p1_id = circuit_particles[i]
                p2_id = circuit_particles[i + 1]
                
                p1 = self.particles[p1_id]
                p2 = self.particles[p2_id]
                
                p1.entangle_with(p2)
                self.entanglement_pairs.append((p1_id, p2_id))
                
            logger.info(f"Circuito quântico criado com {num_particles} partículas")
            return circuit_particles
            
    def simulate_quantum_teleportation(self, source_id, target_id):
        """
        Simula o teleporte quântico de informação entre duas partículas
        """
        with self.lock:
            if source_id in self.particles and target_id in self.particles:
                source = self.particles[source_id]
                target = self.particles[target_id]
                
                # Verificar se as partículas estão entrelaçadas
                if target not in source.entangled_particles:
                    # Criar uma partícula intermediária para entrelaçamento
                    intermediate_id = f"teleport-{int(time.time())}"
                    intermediate = QuantumParticle(intermediate_id)
                    self.particles[intermediate_id] = intermediate
                    
                    # Entrelaçar a partícula intermediária com a fonte e o alvo
                    source.entangle_with(intermediate)
                    intermediate.entangle_with(target)
                    
                    self.entanglement_pairs.append((source_id, intermediate_id))
                    self.entanglement_pairs.append((intermediate_id, target_id))
                    
                # Medir a partícula fonte para colapsar seu estado
                source_state = source.measure()
                
                # O estado da partícula alvo agora está correlacionado com a fonte
                # devido ao entrelaçamento
                target_state = target.measure()
                
                logger.info(f"Teleporte quântico: {source_id}({source_state}) -> {target_id}({target_state})")
                
                return {
                    "operation": "teleport",
                    "source": {
                        "id": source_id,
                        "state": source_state
                    },
                    "target": {
                        "id": target_id,
                        "state": target_state
                    },
                    "success": source_state == target_state,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"Uma ou ambas as partículas não encontradas: {source_id}, {target_id}")
                return {"error": "Partículas não encontradas"}
                
    def shutdown(self):
        """Desliga o sistema de entrelaçamento quântico"""
        self.active = False
        logger.info("Sistema de Entrelaçamento Quântico desligado")

# Função para teste do módulo
if __name__ == "__main__":
    entanglement = QuantumEntanglement()
    print(json.dumps(entanglement.get_entanglement_status(), indent=2))
    
    # Criar um circuito quântico
    circuit = entanglement.create_quantum_circuit(5)
    print(f"Circuito quântico: {circuit}")
    
    # Simular teleporte quântico
    teleport_result = entanglement.simulate_quantum_teleportation(circuit[0], circuit[-1])
    print(json.dumps(teleport_result, indent=2))
    
    # Verificar status após operações
    print(json.dumps(entanglement.get_entanglement_status(), indent=2))
    
    # Aguardar um pouco para o processo em segundo plano executar
    time.sleep(5)
    
    # Verificar status final
    print(json.dumps(entanglement.get_entanglement_status(), indent=2))
    
    entanglement.shutdown()
    
# EVA & GUARANI | Sistema Quântico 