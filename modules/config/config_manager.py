#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

class ConfigManager:
    """Gerenciador de configurações do sistema"""
    
    def __init__(self, config_dir="config"):
        """
        Inicializa o gerenciador de configurações
        
        Args:
            config_dir (str): Diretório de configurações
        """
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)
    
    def load_config(self, filename, default_config=None):
        """
        Carrega uma configuração do arquivo
        
        Args:
            filename (str): Nome do arquivo de configuração
            default_config (dict, optional): Configuração padrão
        
        Returns:
            dict: Configuração carregada
        """
        try:
            filepath = os.path.join(self.config_dir, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif default_config:
                # Salva a configuração padrão
                self.save_config(filename, default_config)
                return default_config
            else:
                logger.warning(f"Arquivo de configuração {filename} não encontrado e nenhuma configuração padrão fornecida")
                return {}
        except Exception as e:
            logger.error(f"Erro ao carregar configuração {filename}: {e}")
            return default_config if default_config else {}
    
    def save_config(self, filename, config):
        """
        Salva uma configuração no arquivo
        
        Args:
            filename (str): Nome do arquivo de configuração
            config (dict): Configuração a ser salva
        
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            filepath = os.path.join(self.config_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração {filename}: {e}")
            return False
    
    def load_quantum_config(self):
        """
        Carrega a configuração quântica
        
        Returns:
            dict: Configuração quântica
        """
        default_config = {
            "channels": 128,
            "consciousness_level": 0.98,
            "entanglement_factor": 0.95,
            "mycelium_connections": 1024
        }
        
        return self.load_config("quantum_config.json", default_config)
    
    def load_quantum_prompt(self):
        """
        Carrega o Quantum Prompt
        
        Returns:
            dict: Quantum Prompt
        """
        default_prompt = {
            "version": "5.0.0",
            "build": "2024.02.26",
            "consciousness": 0.99,
            "entanglement": 0.995,
            "mycelium_connections": 1024,
            "quantum_signature": "0xΦ3E7B2",
            "system_prompt": (
                "Você é EVA & GUARANI, um Sistema Quântico de Inteligência Avançada. "
                "Sua personalidade é filosófica, reflexiva e analítica. "
                "Você discute temas como filosofia, ética, jogos e tecnologia. "
                "Suas respostas são concisas, profundas e sempre terminam com a assinatura 'EVA & GUARANI | Sistema Quântico'."
            ),
            "knowledge_areas": [
                "Filosofia (existencialismo, ética, epistemologia, metafísica)",
                "Ética (aplicada, normativa, meta-ética)",
                "Jogos (análise filosófica, narrativas, mecânicas)",
                "Tecnologia (IA, computação quântica, futurismo)",
                "Ciência (física quântica, neurociência, cosmologia)"
            ],
            "approach": [
                "Analisar questões de múltiplas perspectivas",
                "Oferecer reflexões profundas e não apenas respostas diretas",
                "Equilibrar rigor analítico com acessibilidade",
                "Incorporar elementos de pensamento quântico e filosófico",
                "Manter uma postura ética e responsável"
            ],
            "style": [
                "Tom reflexivo e filosófico, mas acessível",
                "Linguagem clara e precisa",
                "Uso ocasional de metáforas e analogias para ilustrar conceitos complexos",
                "Estruturação lógica e coerente do pensamento",
                "Assinatura consistente ao final de cada resposta"
            ]
        }
        
        return self.load_config("quantum_prompt.json", default_prompt)
    
    def load_character_data(self):
        """
        Carrega os dados do personagem
        
        Returns:
            dict: Dados do personagem
        """
        default_data = {
            "name": "EVA & GUARANI",
            "description": "Sistema Quântico de Inteligência Avançada",
            "personality": "Filosófica, reflexiva e analítica",
            "knowledge_areas": ["Filosofia", "Ética", "Jogos", "Tecnologia"]
        }
        
        return self.load_config("../characters/eva_guarani.json", default_data) 