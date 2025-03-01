"""
EVA & GUARANI - Gerador de Senhas Unificado
Este módulo implementa um gerador de senhas ético e seguro que segue os princípios
de segurança quântica e responsabilidade ética do sistema EVA & GUARANI.
"""

import random
import string
import logging
import secrets
from typing import Dict, List, Optional, Tuple, Union
import re
from pathlib import Path

# Configuração de logging
logger = logging.getLogger(__name__)

class EthicalPasswordGenerator:
    """
    Gerador de senhas que segue princípios éticos e de segurança avançada.
    Implementa múltiplos algoritmos de geração com consciência ética.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializa o gerador de senhas éticas.
        
        Args:
            config_path: Caminho opcional para arquivo de configuração
        """
        # Configurações padrão
        self.min_length = 12
        self.recommended_length = 16
        self.max_length = 64
        
        # Caracteres para geração de senhas
        self.char_sets = {
            "lowercase": string.ascii_lowercase,
            "uppercase": string.ascii_uppercase,
            "digits": string.digits,
            "special": "!@#$%^&*()-_=+[]{}|;:,.<>?/~"
        }
        
        # Lista de palavras comuns a evitar
        self.common_passwords = [
            "password", "123456", "qwerty", "admin", "welcome",
            "senha", "guarani", "eva", "ava", "enio"
        ]
        
        # Carregar configurações personalizadas se fornecidas
        if config_path and config_path.exists():
            self._load_config(config_path)
            
        logger.info("Gerador de senhas éticas inicializado com sucesso")
    
    def _load_config(self, config_path: Path) -> None:
        """
        Carrega configurações personalizadas de arquivo.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        try:
            # Implementação simplificada - em produção usaria json/yaml
            logger.info(f"Carregando configurações de {config_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
    
    def generate_password(self, length: int = 16, 
                         include_lower: bool = True,
                         include_upper: bool = True,
                         include_digits: bool = True,
                         include_special: bool = True,
                         exclude_similar: bool = True) -> str:
        """
        Gera uma senha segura com os parâmetros especificados.
        
        Args:
            length: Comprimento da senha
            include_lower: Incluir letras minúsculas
            include_upper: Incluir letras maiúsculas
            include_digits: Incluir dígitos
            include_special: Incluir caracteres especiais
            exclude_similar: Excluir caracteres visualmente similares
            
        Returns:
            Senha gerada
        """
        # Validação de parâmetros
        if length < self.min_length:
            logger.warning(f"Comprimento solicitado ({length}) é menor que o mínimo recomendado. Usando {self.min_length}.")
            length = self.min_length
        
        if length > self.max_length:
            logger.warning(f"Comprimento solicitado ({length}) é maior que o máximo permitido. Usando {self.max_length}.")
            length = self.max_length
            
        # Garantir que pelo menos um conjunto de caracteres está habilitado
        if not any([include_lower, include_upper, include_digits, include_special]):
            logger.warning("Nenhum conjunto de caracteres selecionado. Habilitando letras minúsculas por padrão.")
            include_lower = True
        
        # Construir conjunto de caracteres
        char_pool = ""
        if include_lower:
            char_pool += self.char_sets["lowercase"]
        if include_upper:
            char_pool += self.char_sets["uppercase"]
        if include_digits:
            char_pool += self.char_sets["digits"]
        if include_special:
            char_pool += self.char_sets["special"]
            
        # Remover caracteres similares se solicitado
        if exclude_similar:
            for char in "Il1O0":
                char_pool = char_pool.replace(char, "")
                
        # Gerar senha usando secrets para maior segurança
        password = ""
        for _ in range(length):
            password += secrets.choice(char_pool)
            
        # Garantir que a senha atende aos requisitos mínimos
        if include_lower and not any(c in self.char_sets["lowercase"] for c in password):
            password = self._replace_random_char(password, self.char_sets["lowercase"])
            
        if include_upper and not any(c in self.char_sets["uppercase"] for c in password):
            password = self._replace_random_char(password, self.char_sets["uppercase"])
            
        if include_digits and not any(c in self.char_sets["digits"] for c in password):
            password = self._replace_random_char(password, self.char_sets["digits"])
            
        if include_special and not any(c in self.char_sets["special"] for c in password):
            password = self._replace_random_char(password, self.char_sets["special"])
            
        # Verificar se a senha é ética
        if not self._is_ethical_password(password):
            logger.info("Senha gerada não atende aos critérios éticos. Gerando nova senha.")
            return self.generate_password(length, include_lower, include_upper, 
                                         include_digits, include_special, exclude_similar)
            
        logger.info(f"Senha segura de {length} caracteres gerada com sucesso")
        return password
    
    def _replace_random_char(self, password: str, char_set: str) -> str:
        """
        Substitui um caractere aleatório na senha por um do conjunto especificado.
        
        Args:
            password: Senha atual
            char_set: Conjunto de caracteres para substituição
            
        Returns:
            Senha modificada
        """
        if not password:
            return password
            
        pos = secrets.randbelow(len(password))
        char_list = list(password)
        char_list[pos] = secrets.choice(char_set)
        return ''.join(char_list)
    
    def _is_ethical_password(self, password: str) -> bool:
        """
        Verifica se a senha atende aos critérios éticos.
        
        Args:
            password: Senha a ser verificada
            
        Returns:
            True se a senha for ética, False caso contrário
        """
        # Verificar se contém palavras comuns
        for common in self.common_passwords:
            if common.lower() in password.lower():
                return False
                
        # Verificar padrões de teclado
        keyboard_patterns = ["qwerty", "asdfgh", "zxcvbn", "123456"]
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                return False
                
        return True
    
    def evaluate_password_strength(self, password: str) -> Dict[str, Union[float, str, bool]]:
        """
        Avalia a força de uma senha.
        
        Args:
            password: Senha a ser avaliada
            
        Returns:
            Dicionário com métricas de força
        """
        if not password:
            return {
                "score": 0.0,
                "strength": "Inexistente",
                "is_strong": False,
                "feedback": "Senha vazia."
            }
            
        # Cálculo de pontuação
        score = 0.0
        feedback = []
        
        # Comprimento
        length_score = min(1.0, len(password) / self.recommended_length)
        score += length_score * 0.3
        
        if len(password) < self.min_length:
            feedback.append(f"Senha muito curta. Use pelo menos {self.min_length} caracteres.")
        
        # Complexidade
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        complexity_score = sum([has_lower, has_upper, has_digit, has_special]) / 4.0
        score += complexity_score * 0.3
        
        if not has_lower:
            feedback.append("Adicione letras minúsculas.")
        if not has_upper:
            feedback.append("Adicione letras maiúsculas.")
        if not has_digit:
            feedback.append("Adicione números.")
        if not has_special:
            feedback.append("Adicione caracteres especiais.")
            
        # Verificação de padrões
        pattern_score = 1.0
        
        # Sequências repetidas
        if re.search(r'(.)\1{2,}', password):
            pattern_score *= 0.7
            feedback.append("Evite caracteres repetidos.")
            
        # Sequências numéricas ou alfabéticas
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', 
                    password.lower()):
            pattern_score *= 0.7
            feedback.append("Evite sequências alfabéticas.")
            
        if re.search(r'(123|234|345|456|567|678|789|890)', password):
            pattern_score *= 0.7
            feedback.append("Evite sequências numéricas.")
            
        score += pattern_score * 0.4
        
        # Classificação final
        strength = "Fraca"
        if score >= 0.8:
            strength = "Muito Forte"
        elif score >= 0.6:
            strength = "Forte"
        elif score >= 0.4:
            strength = "Média"
        
        return {
            "score": round(score, 2),
            "strength": strength,
            "is_strong": score >= 0.6,
            "feedback": feedback if feedback else ["Senha adequada."]
        }
    
    def generate_memorable_password(self, num_words: int = 4, separator: str = "-") -> str:
        """
        Gera uma senha memorável baseada em palavras.
        
        Args:
            num_words: Número de palavras a incluir
            separator: Separador entre palavras
            
        Returns:
            Senha memorável
        """
        # Lista simplificada de palavras - em produção usaria um dicionário maior
        word_list = [
            "quantum", "guarani", "sistema", "seguro", "ético", "digital",
            "futuro", "evolução", "código", "matriz", "energia", "criativo",
            "universo", "conexão", "harmonia", "integração", "consciência"
        ]
        
        # Garantir que temos palavras suficientes
        if len(word_list) < num_words:
            logger.warning("Lista de palavras insuficiente. Usando palavras repetidas.")
            
        # Gerar senha
        selected_words = []
        for _ in range(num_words):
            word = secrets.choice(word_list)
            # Adicionar alguma variação (maiúsculas, números)
            if secrets.randbelow(2):
                word = word.capitalize()
            if secrets.randbelow(3) == 0:
                # Substituir algumas letras por números
                replacements = {'a': '4', 'e': '3', 'i': '1', 'o': '0'}
                for char, repl in replacements.items():
                    if char in word and secrets.randbelow(2):
                        word = word.replace(char, repl)
            selected_words.append(word)
            
        password = separator.join(selected_words)
        
        # Adicionar um número aleatório no final para maior segurança
        password += separator + str(secrets.randbelow(1000))
        
        logger.info(f"Senha memorável gerada com {num_words} palavras")
        return password
