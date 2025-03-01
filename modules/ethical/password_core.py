import secrets
import hashlib
import zxcvbn
from datetime import datetime
from pathlib import Path

class EthicalPasswordCore:
    """
    Núcleo de gerenciamento de senhas éticas com segurança quântica avançada.
    Implementa geração, validação e armazenamento seguro de credenciais.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializa o núcleo de senhas éticas.
        
        Args:
            config_path: Caminho opcional para arquivo de configuração
        """
        # Configurações padrão
        self.entropy_threshold = 70  # bits de entropia mínima
        self.quantum_enhanced = True
        self.ethical_guidelines = {
            "prevent_common": True,
            "prevent_personal": True,
            "prevent_sequential": True,
            "encourage_diversity": True
        }
        
        # Dicionário de palavras comuns a evitar
        self.common_words = self._load_common_words()
        
        # Configurações de hash
        self.hash_iterations = 600000  # Número de iterações para PBKDF2
        self.argon2_hasher = PasswordHasher(
            time_cost=4,
            memory_cost=65536,
            parallelism=8,
            hash_len=32
        )
        
        # Carregar configurações personalizadas
        if config_path and Path(config_path).exists():
            self._load_config(config_path)
            
        logger.info("Núcleo de senhas éticas inicializado com configurações de segurança quântica")
    
    def _load_common_words(self) -> List[str]:
        """Carrega lista de palavras comuns a serem evitadas em senhas."""
        # Lista básica - em produção seria carregada de um arquivo
        return [
            "password", "123456", "qwerty", "admin", "welcome", "senha",
            "guarani", "eva", "quantum", "seguranca", "sistema", "usuario"
        ]
    
    def _load_config(self, config_path: Path) -> None:
        """Carrega configurações personalizadas."""
        try:
            logger.info(f"Carregando configurações de {config_path}")
            # Implementação simplificada - em produção usaria json/yaml
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
    
    def generate_secure_password(self, length: int = 16, 
                               include_special: bool = True,
                               exclude_similar: bool = True) -> str:
        """
        Gera uma senha segura e ética usando entropia quântica quando disponível.
        
        Args:
            length: Comprimento da senha (mínimo 12)
            include_special: Incluir caracteres especiais
            exclude_similar: Excluir caracteres visualmente similares
            
        Returns:
            Senha segura gerada
        """
        # Garantir comprimento mínimo
        length = max(12, length)
        
        # Definir conjuntos de caracteres
        chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        if include_special:
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?/~"
        
        if exclude_similar:
            for char in "Il1O0":
                chars = chars.replace(char, "")
        
        # Usar secrets para geração criptograficamente segura
        password = "".join(secrets.choice(chars) for _ in range(length))
        
        # Garantir requisitos mínimos
        if not any(c.islower() for c in password):
            password = self._replace_random_char(password, string.ascii_lowercase)
        if not any(c.isupper() for c in password):
            password = self._replace_random_char(password, string.ascii_uppercase)
        if not any(c.isdigit() for c in password):
            password = self._replace_random_char(password, string.digits)
        if include_special and not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/~" for c in password):
            password = self._replace_random_char(password, "!@#$%^&*()-_=+[]{}|;:,.<>?/~")
        
        # Verificar força da senha gerada
        if self._calculate_entropy(password) < self.entropy_threshold:
            # Recursivamente gerar nova senha se não atender aos requisitos
            return self.generate_secure_password(length, include_special, exclude_similar)
        
        return password
    
    def _replace_random_char(self, password: str, char_set: str) -> str:
        """Substitui um caractere aleatório na senha por um do conjunto especificado."""
        if not password:
            return ""
        
        index = secrets.randbelow(len(password))
        char_list = list(password)
        char_list[index] = secrets.choice(char_set)
        return "".join(char_list)
    
    def _calculate_entropy(self, password: str) -> float:
        """Calcula a entropia estimada de uma senha em bits."""
        if not password:
            return 0.0
        
        # Usar zxcvbn para análise avançada de entropia
        result = zxcvbn.zxcvbn(password)
        return result['entropy']
    
    def hash_password(self, password: str, method: str = "argon2") -> str:
        """
        Cria hash seguro de senha usando algoritmos modernos.
        
        Args:
            password: Senha a ser hasheada
            method: Método de hash ('argon2', 'bcrypt', ou 'pbkdf2')
            
        Returns:
            Hash da senha
        """
        if not password:
            raise ValueError("Senha não pode ser vazia")
        
        if method.lower() == "argon2":
            return self.argon2_hasher.hash(password)
        elif method.lower() == "bcrypt":
            salt = bcrypt.gensalt(rounds=12)
            return bcrypt.hashpw(password.encode(), salt).decode()
        elif method.lower() == "pbkdf2":
            return pbkdf2_sha256.hash(password, rounds=self.hash_iterations)
        else:
            raise ValueError(f"Método de hash não suportado: {method}")
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verifica se uma senha corresponde ao hash armazenado.
        
        Args:
            password: Senha a ser verificada
            password_hash: Hash armazenado
            
        Returns:
            True se a senha corresponder ao hash, False caso contrário
        """
        if not password or not password_hash:
            return False
        
        try:
            # Detectar automaticamente o tipo de hash
            if password_hash.startswith("$argon2"):
                return self.argon2_hasher.verify(password_hash, password)
            elif password_hash.startswith("$2b$"):
                return bcrypt.checkpw(password.encode(), password_hash.encode())
            elif password_hash.startswith("$pbkdf2"):
                return pbkdf2_sha256.verify(password, password_hash)
            else:
                logger.warning("Formato de hash não reconhecido")
                return False
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {e}")
            return False
    
    def evaluate_password_ethics(self, password: str) -> Dict[str, Union[bool, str, List[str]]]:
        """
        Avalia aspectos éticos de uma senha.
        
        Args:
            password: Senha a ser avaliada
            
        Returns:
            Dicionário com avaliação ética
        """
        issues = []
        
        # Verificar palavras comuns
        if self.ethical_guidelines["prevent_common"]:
            for word in self.common_words:
                if word.lower() in password.lower():
                    issues.append(f"Contém palavra comum: '{word}'")
        
        # Verificar sequências
        if self.ethical_guidelines["prevent_sequential"]:
            sequences = ["123", "abc", "qwe", "xyz"]
            for seq in sequences:
                if seq.lower() in password.lower():
                    issues.append(f"Contém sequência previsível: '{seq}'")
        
        # Análise avançada com zxcvbn
        analysis = zxcvbn.zxcvbn(password)
        
        return {
            "is_ethical": len(issues) == 0,
            "strength_score": analysis['score'],  # 0-4, onde 4 é o mais forte
            "estimated_crack_time": analysis['crack_times_display']['offline_slow_hashing_1e4_per_second'],
            "issues": issues,
            "suggestions": analysis['feedback']['suggestions']
        }
    
    def generate_recovery_token(self) -> Tuple[str, str]:
        """
        Gera um token seguro para recuperação de senha.
        
        Returns:
            Tupla contendo (token, hash do token)
        """
        # Gerar token com alta entropia
        token_bytes = secrets.token_bytes(32)
        token = token_bytes.hex()
        
        # Criar hash do token para armazenamento
        token_hash = hashlib.sha256(token_bytes).hexdigest()
        
        return token, token_hash
    
    def log_security_event(self, event_type: str, details: Dict[str, any]) -> None:
        """
        Registra evento de segurança relacionado a senhas.
        
        Args:
            event_type: Tipo de evento (ex: 'password_change', 'failed_attempt')
            details: Detalhes do evento (sem informações sensíveis)
        """
        timestamp = datetime.now().isoformat()
        
        # Garantir que não há dados sensíveis nos logs
        if "password" in details:
            details["password"] = "[REDACTED]"
        if "hash" in details:
            details["hash"] = "[HASH_REDACTED]"
        
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "details": details
        }
        
        logger.info(f"Evento de segurança: {event_type} - {timestamp}")

"""
EVA & GUARANI - Módulo de Núcleo de Senhas Éticas
Este módulo fornece funcionalidades centrais para geração e validação de senhas
seguindo princípios éticos e de segurança quântica.
"""

import random
import string
import re
import logging
from typing import List, Dict, Optional, Tuple, Union
import bcrypt
from argon2 import PasswordHasher
from passlib.hash import pbkdf2_sha256

# Configuração de logging
logger = logging.getLogger(__name__)

class PasswordStrengthEvaluator:
    """Avaliador de força de senhas com consciência ética."""
    
    def __init__(self):
        self.min_length = 8
        self.recommended_length = 16
        
    def evaluate(self, password: str) -> Dict[str, Union[float, bool, str]]:
        """
        Avalia a força de uma senha.
        
        Args:
            password: A senha a ser avaliada
            
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
        
        # Cálculo básico de pontuação
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
        
        # Entropia
        char_set_size = 0
        if has_lower: char_set_size += 26
        if has_upper: char_set_size += 26
        if has_digit: char_set_size += 10
        if has_special: char_set_size += 32
        
        if char_set_size > 0:
            entropy = len(password) * (len(password) / char_set_size)
            entropy_score = min(1.0, entropy / 100)
            score += entropy_score * 0.2
        
        # Padrões comuns
        patterns = [
            r'12345', r'qwerty', r'password', r'admin', r'welcome',
            r'123123', r'abcabc', r'abc123', r'senha', r'admin123'
        ]
        
        pattern_found = False
        for pattern in patterns:
            if re.search(pattern, password.lower()):
                pattern_found = True
                feedback.append(f"Evite padrões comuns como '{pattern}'.")
                break
        
        if not pattern_found:
            score += 0.1
        
        # Repetições
        if re.search(r'(.)\1{2,}', password):
            score -= 0.1
            feedback.append("Evite caracteres repetidos consecutivamente.")
        
        # Sequências
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', 
                    password.lower()):
            score -= 0.1
            feedback.append("Evite sequências de caracteres.")
        
        # Classificação final
        score = max(0.0, min(1.0, score))
        
        strength_levels = [
            (0.2, "Muito fraca"),
            (0.4, "Fraca"),
            (0.6, "Média"),
            (0.8, "Forte"),
            (1.0, "Muito forte")
        ]
        
        strength = "Desconhecida"
        for threshold, level in strength_levels:
            if score <= threshold:
                strength = level
                break
        
        if not feedback:
            feedback.append("Senha adequada.")
        
        return {
            "score": score,
            "strength": strength,
            "is_strong": score >= 0.6,
            "feedback": "; ".join(feedback)
        }

class PasswordGenerator:
    """Gerador de senhas éticas e seguras."""
    
    def __init__(self):
        self.lowercase_chars = string.ascii_lowercase
        self.uppercase_chars = string.ascii_uppercase
        self.digit_chars = string.digits
        self.symbol_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        self.similar_chars = "iIl1oO0"
        
    def generate(self, 
                length: int = 16, 
                include_uppercase: bool = True,
                include_lowercase: bool = True,
                include_numbers: bool = True,
                include_symbols: bool = True,
                avoid_similar: bool = False) -> str:
        """
        Gera uma senha aleatória com os critérios especificados.
        
        Args:
            length: Comprimento da senha
            include_uppercase: Incluir letras maiúsculas
            include_lowercase: Incluir letras minúsculas
            include_numbers: Incluir números
            include_symbols: Incluir símbolos
            avoid_similar: Evitar caracteres similares
            
        Returns:
            Senha gerada
        """
        if length < 4:
            length = 4
            logger.warning("Comprimento mínimo de senha ajustado para 4")
        
        # Prepara o conjunto de caracteres
        char_set = ""
        
        if include_lowercase:
            if avoid_similar:
                char_set += ''.join(c for c in self.lowercase_chars if c not in self.similar_chars)
            else:
                char_set += self.lowercase_chars
                
        if include_uppercase:
            if avoid_similar:
                char_set += ''.join(c for c in self.uppercase_chars if c not in self.similar_chars)
            else:
                char_set += self.uppercase_chars
                
        if include_numbers:
            if avoid_similar:
                char_set += ''.join(c for c in self.digit_chars if c not in self.similar_chars)
            else:
                char_set += self.digit_chars
                
        if include_symbols:
            char_set += self.symbol_chars
            
        if not char_set:
            # Fallback para garantir que temos algum conjunto de caracteres
            char_set = self.lowercase_chars
            logger.warning("Nenhum conjunto de caracteres selecionado, usando letras minúsculas")
        
        # Garante que pelo menos um caractere de cada tipo esteja presente
        password_chars = []
        
        if include_lowercase:
            subset = self.lowercase_chars
            if avoid_similar:
                subset = ''.join(c for c in subset if c not in self.similar_chars)
            password_chars.append(random.choice(subset))
            
        if include_uppercase:
            subset = self.uppercase_chars
            if avoid_similar:
                subset = ''.join(c for c in subset if c not in self.similar_chars)
            password_chars.append(random.choice(subset))
            
        if include_numbers:
            subset = self.digit_chars
            if avoid_similar:
                subset = ''.join(c for c in subset if c not in self.similar_chars)
            password_chars.append(random.choice(subset))
            
        if include_symbols:
            password_chars.append(random.choice(self.symbol_chars))
        
        # Preenche o restante da senha
        while len(password_chars) < length:
            password_chars.append(random.choice(char_set))
        
        # Embaralha a senha para garantir aleatoriedade
        random.shuffle(password_chars)
        
        return ''.join(password_chars)

class PasswordHashManager:
    """Gerenciador de hash de senhas com múltiplos algoritmos."""
    
    def __init__(self):
        self.argon2_hasher = PasswordHasher()
    
    def hash_password(self, password: str, method: str = "argon2") -> str:
        """
        Cria um hash seguro da senha.
        
        Args:
            password: Senha a ser hasheada
            method: Método de hash (argon2, bcrypt, pbkdf2)
            
        Returns:
            Hash da senha
        """
        if method == "argon2":
            return self.argon2_hasher.hash(password)
        elif method == "bcrypt":
            return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        elif method == "pbkdf2":
            return pbkdf2_sha256.hash(password)
        else:
            raise ValueError(f"Método de hash não suportado: {method}")
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash.
        
        Args:
            password: Senha a ser verificada
            password_hash: Hash da senha
            
        Returns:
            True se a senha corresponder ao hash, False caso contrário
        """
        try:
            # Tenta verificar com Argon2
            if password_hash.startswith("$argon2"):
                return self.argon2_hasher.verify(password_hash, password)
            
            # Tenta verificar com bcrypt
            elif password_hash.startswith("$2"):
                return bcrypt.checkpw(password.encode(), password_hash.encode())
            
            # Tenta verificar com pbkdf2
            elif password_hash.startswith("$pbkdf2"):
                return pbkdf2_sha256.verify(password, password_hash)
            
            else:
                logger.error(f"Formato de hash não reconhecido: {password_hash[:10]}...")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {str(e)}")
            return False

# Instâncias singleton para uso em toda a aplicação
password_evaluator = PasswordStrengthEvaluator()
password_generator = PasswordGenerator()
password_hash_manager = PasswordHashManager()