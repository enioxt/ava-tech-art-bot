#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from datetime import datetime

# Configuração de logging
logger = logging.getLogger(__name__)

class SimpleMemory:
    """Sistema de memória simples para o bot"""
    
    def __init__(self, memory_file="memory/interactions.json"):
        """
        Inicializa o sistema de memória
        
        Args:
            memory_file (str): Caminho para o arquivo de memória
        """
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self):
        """
        Carrega a memória do arquivo
        
        Returns:
            dict: Memória carregada
        """
        try:
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Memória inicial vazia
                initial_memory = {
                    "users": {},
                    "interactions": []
                }
                
                # Salva a memória inicial
                with open(self.memory_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_memory, f, indent=4)
                
                return initial_memory
        except Exception as e:
            logger.error(f"Erro ao carregar memória: {e}")
            return {
                "users": {},
                "interactions": []
            }
    
    def _save_memory(self):
        """Salva a memória no arquivo"""
        try:
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")
    
    def add_interaction(self, user_id, user_name, message, response):
        """
        Adiciona uma interação à memória
        
        Args:
            user_id (str): ID do usuário
            user_name (str): Nome do usuário
            message (str): Mensagem do usuário
            response (str): Resposta do bot
        """
        try:
            # Adiciona ou atualiza o usuário
            if user_id not in self.memory["users"]:
                self.memory["users"][user_id] = {
                    "name": user_name,
                    "first_interaction": datetime.now().isoformat(),
                    "interaction_count": 0
                }
            
            # Incrementa o contador de interações do usuário
            self.memory["users"][user_id]["interaction_count"] += 1
            self.memory["users"][user_id]["last_interaction"] = datetime.now().isoformat()
            
            # Adiciona a interação
            self.memory["interactions"].append({
                "user_id": user_id,
                "user_name": user_name,
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "response": response
            })
            
            # Limita o número de interações armazenadas (mantém as 1000 mais recentes)
            if len(self.memory["interactions"]) > 1000:
                self.memory["interactions"] = self.memory["interactions"][-1000:]
            
            # Salva a memória
            self._save_memory()
        except Exception as e:
            logger.error(f"Erro ao adicionar interação: {e}")
    
    def get_user_interactions(self, user_id, limit=10):
        """
        Obtém as interações de um usuário
        
        Args:
            user_id (str): ID do usuário
            limit (int, optional): Número máximo de interações a retornar
        
        Returns:
            list: Lista de interações do usuário
        """
        try:
            # Filtra as interações do usuário
            user_interactions = [
                interaction for interaction in self.memory["interactions"]
                if interaction["user_id"] == user_id
            ]
            
            # Retorna as interações mais recentes
            return user_interactions[-limit:]
        except Exception as e:
            logger.error(f"Erro ao obter interações do usuário: {e}")
            return []
    
    def get_user_info(self, user_id):
        """
        Obtém informações sobre um usuário
        
        Args:
            user_id (str): ID do usuário
        
        Returns:
            dict: Informações do usuário
        """
        try:
            return self.memory["users"].get(user_id, {})
        except Exception as e:
            logger.error(f"Erro ao obter informações do usuário: {e}")
            return {}
    
    def get_all_users(self):
        """
        Obtém todos os usuários
        
        Returns:
            dict: Dicionário de usuários
        """
        try:
            return self.memory["users"]
        except Exception as e:
            logger.error(f"Erro ao obter todos os usuários: {e}")
            return {}
    
    def get_interaction 