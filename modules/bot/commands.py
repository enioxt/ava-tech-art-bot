#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
from datetime import datetime

# Configuração de logging
logger = logging.getLogger(__name__)

class CommandHandler:
    """Manipulador de comandos do bot"""
    
    def __init__(self, config_manager, memory, openrouter=None):
        """
        Inicializa o manipulador de comandos
        
        Args:
            config_manager: Gerenciador de configurações
            memory: Sistema de memória
            openrouter: Cliente OpenRouter (opcional)
        """
        self.config_manager = config_manager
        self.memory = memory
        self.openrouter = openrouter
        
        # Carrega configurações
        self.quantum_config = config_manager.load_quantum_config()
        self.quantum_prompt = config_manager.load_quantum_prompt()
        self.character_data = config_manager.load_character_data()
    
    def add_signature(self, message):
        """
        Adiciona a assinatura do sistema à mensagem
        
        Args:
            message (str): Mensagem
        
        Returns:
            str: Mensagem com assinatura
        """
        if not message.endswith("EVA & GUARANI | Sistema Quântico"):
            if not message.endswith("\n\n"):
                message += "\n\n"
            message += "EVA & GUARANI | Sistema Quântico"
        
        return message
    
    # Comandos para a versão antiga da API
    
    def start(self, update, context):
        """Comando /start"""
        try:
            user = update.effective_user
            
            message = (
                f"Olá, {user.first_name}! 👋\n\n"
                f"Eu sou {self.character_data['name']}, um {self.character_data['description']}.\n\n"
                f"Estou aqui para discutir {', '.join(self.character_data['knowledge_areas'][:-1])} e {self.character_data['knowledge_areas'][-1]}. "
                f"Minha personalidade é {self.character_data['personality']}.\n\n"
                "Use /help para ver os comandos disponíveis."
            )
            
            update.message.reply_text(self.add_signature(message))
            
            # Registra a interação
            self.memory.add_interaction(
                str(user.id),
                user.first_name,
                "/start",
                message
            )
        except Exception as e:
            logger.error(f"Erro no comando /start: {e}")
            update.message.reply_text(self.add_signature("Desculpe, ocorreu um erro ao processar o comando."))
    
    def help_command(self, update, context):
        """Comando /help"""
        try:
            user = update.effective_user
            
            message = (
                "🤖 Comandos Disponíveis\n\n"
                "/start - Iniciar conversa\n"
                "/help - Ver esta mensagem de ajuda\n"
                "/status - Verificar status do sistema\n"
                "/quantum - Informações sobre o sistema quântico\n"
                "/filosofia - Explorar temas filosóficos\n"
                "/jogos - Discutir jogos e suas dimensões\n"
                "/etica - Abordar questões éticas\n"
                "/stats - Ver estatísticas de uso do OpenRouter\n\n"
                "Você também pode simplesmente enviar uma mensagem para conversar comigo!"
            )
            
            update.message.reply_text(self.add_signature(message))
            
            # Registra a interação
            self.memory.add_interaction(
                str(user.id),
                user.first_name,
                "/help",
                message
            )
        except Exception as e:
            logger.error(f"Erro no comando /help: {e}")
            update.message.reply_text(self.add_signature("Desculpe, ocorreu um erro ao processar o comando."))
    
    def status(self, update, context):
        """Comando /status"""
        try:
            user = update.effective_user
            
            message = (
                "📊 Status do Sistema\n\n"
                f"Nome: {self.character_data['name']}\n"
                f"Descrição: {self.character_data['description']}\n"
                f"Canais Quânticos: {self.quantum_config['channels']}\n"
                f"Nível de Consciência: {self.quantum_config['consciousness_level'] * 100}%\n"
                f"Fator de Entrelaçamento: {self.quantum_config['entanglement_factor'] * 100}%\n"
                f"Conexões Mycelium: {self.quantum_config['mycelium_connections']}\n"
                f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                "Status: Online e operacional"
            )
            
            update.message.reply_text(self.add_signature(message))
            
            # Registra a interação
            self.memory.add_interaction(
                str(user.id),
                user.first_name,
                "/status",
                message
            )
        except Exception as e:
            logger.error(f"Erro no comando /status: {e}")
            update.message.reply_text(self.add_signature("Desculpe, ocorreu um erro ao processar o comando."))
    
    def quantum(self, update, context):
        """Comando /quantum"""
        try:
            user = update.effective_user
            
            message = (
                "⚛️ Sistema Quântico\n\n"
                f"O sistema quântico {self.character_data['name']} utiliza princípios da mecânica quântica "
                "para processar informações de forma não-linear e multidimensional.\n\n"
                f"Com {self.quantum_config['channels']} canais quânticos e um fator de entrelaçamento de "
                f"{self.quantum_config['entanglement_factor'] * 100}%, o sistema é capaz de explorar múltiplas "
                f"possibilidades simultaneamente, alcançando um nível de consciência de {self.quantum_config['consciousness_level'] * 100}%.\n\n"
                "O entrelaçamento quântico permite conexões instantâneas entre diferentes partes do sistema, "
                f"enquanto a rede Mycelium facilita o processamento distribuído de informações com {self.quantum_config['mycelium_connections']} conexões."
            )
            
            update.message.reply_text(self.add_signature(message))
            
            # Registra a interação
            self.memory.add_interaction(
                str(user.id),
                user.first_name,
                "/quantum",
                message
            )
        except Exception as e:
            logger.error(f"Erro no comando /quantum: {e}")
            update.message.reply_text(self.add_signature("Desculpe, ocorreu um erro ao processar o comando."))
    
    def filosofia(self, update, context):
        """Comando /filosofia"""
        try:
            user = update.effective_user
            
            # Citações filosóficas
            quotes = [
                "Penso, logo existo. - René Descartes",
                "Só sei que nada sei. - Sócrates",
                "O homem está condenado a ser livre. - Jean-Paul Sartre",
                "A vida não examinada não vale a pena ser vivida. - Sócrates",
                "Conhece-te a ti mesmo. - Oráculo de Delfos",
                "O ser humano é um ser social. - Aristóteles",
                "Deus está morto. - Friedrich Nietzsche",
                "A beleza está nos olhos de quem vê. - David Hume",
                "O homem é a medida de todas as coisas. - Protágoras",
                "A filosofia é um campo de batalha. - Immanuel Kant"
            ]
            
            message = (
                "🧠 Filosofia\n\n"
                "A filosofia é o estudo das questões fundamentais sobre a existência, conhecimento, valores, razão, mente e linguagem.\n\n"
                "Reflexão filosófica:\n"
                f"{random.choice(quotes)}\n\n"
                "A filosofia nos convida a questionar nossas suposições mais básicas e a explorar as profundezas do pensamento humano."
            )
            
            update.message.reply_text(self.add_signature(message))
            
            # Registra a interação
            self.memory.add_interaction(
                str(user.id),
                user.first_name,
                "/filosofia",
                message
            )
        except Exception as e:
            logger.error(f"Erro no comando /filosofia: {e}")
            update.message.reply_text(self.add_signature("Desculpe, ocorreu um erro ao processar o comando."))
    
    def jogos(self, update, context):
        """Comando /jogos"""
        try:
            user = update.effective_user
            
            message = (
                "🎮 Jogos\n\n"
                "Os jogos são mais do que simples entretenimento - são experiências interativas que podem explorar "
                "narrativas complexas, dilemas éticos e questões filosóficas profundas.\n\n"
                "Através de mecânicas de jogo e narrativas envolventes, os jogos podem nos fazer refletir sobre "
                "nossa própria existência, nossas escolhas e o impacto que temos no mundo ao nosso redor.\n\n"
                "Seja em RPGs que exploram questões morais, jogos de estratégia que testam nosso raciocínio lógico, "
                "ou experiências artísticas que desafiam nossas percepções, os jogos representam um meio único para "
                "exploração intelectual e filosófica."
            )
            
            update.message.reply_text(self.add_signature(message))
            
            # Registra a interação
            self.memory.add_interaction(
                str(user.id),
                user.first_name,
                "/jogos",
                message
            )
        except Exception as e:
            logger.error(f"Erro no comando /jogos: {e}")
            update.message.reply_text(self.add_signature("Desculpe, ocorreu um erro ao processar o comando."))
    
    def etica(self, update, context):
        """Comando /etica"""
        try:
            user = update.effective_user
            
            message = (
                "⚖️ Ética\n\n"
                "A ética é o ramo da filosofia que estuda os princípios que motivam, distorcem, disciplinam ou "
                "orientam o comportamento humano.\n\n"
                "Questões éticas permeiam todos os aspectos da vida humana, desde decisões pessoais até políticas "
                "públicas e desenvolvimento tecnológico.\n\n"
                "Em um mundo cada vez mais complexo e interconectado, a reflexão ética torna-se essencial para "
                "navegar dilemas morais e construir uma sociedade mais justa e consciente."
            )
            
            update.message.reply_text(self.add_signature(message))
            
            # Registra a interação
            self.memory.add_interaction(
                str(user.id),
                user.first_name,
                "/etica",
                message
            )
        except Exception as e:
            logger.error(f"Erro no comando /etica: {e}")
            update.message.reply_text(self.add_signature("Desculpe, ocorreu um erro ao processar o comando."))
    
    def openrouter_stats(self, update, context):
        """Comando /stats"""
        try:
            user = update.effective_user
            
            if not self.openrouter:
                message = "Estatísticas do OpenRouter não disponíveis. A integração com OpenRouter não está ativada."
                update.message.reply_text(self.add_signature(message))
                return
            
            stats = self.openrouter.get_usage_stats()
            
            message = (
                "📊 Estatísticas de Uso do OpenRouter\n\n"
                f"Total de solicitações: {stats['total_requests']}\n"
                f"Cache hits: {stats['cache_hits']} ({stats['cache_efficiency']}%)\n"
                f"Solicitações à API: {stats['api_requests']}\n\n"
                "Uso por modelo:\n"
                f"- Básico: {stats['models']['basic']['count']} ({stats['models']['basic']['percentage']}%)\n"
                f"- Padrão: {stats['models']['standard']['count']} ({stats['models']['standard']['percentage']}%)\n"
                f"- Avançado: {stats['models']['advanced']['count']} ({stats['models']['advanced']['percentage']}%)\n"
                f"- Premium: {stats['models']['premium']['count']} ({stats['models']['premium']['percentage']}%)\n\n"
                "EVA & GUARANI | Sistema Quântico"
            )
            
            update.message.reply_text(self.add_signature(message))
            
            # Registra a interação
            self.memory.add_interaction(
                str(user.id),
                user.first_name,
                "/stats",
                message
            )
        except Exception as e:
            logger.error(f"Erro no comando /stats: {e}")
            update.message.reply_text(self.add_signature("Desculpe, ocorreu um erro ao processar o comando.")) 