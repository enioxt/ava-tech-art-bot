#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Configuração da Integração com ElizaOS
Script para instalar e configurar a integração com ElizaOS
"""

import os
import sys
import subprocess
import logging
import platform
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/setup_eliza.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("✨setup-eliza✨")

# Cria diretórios necessários
Path("logs").mkdir(exist_ok=True)

class ElizaSetup:
    """Classe para configurar a integração com ElizaOS."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa a configuração da integração com ElizaOS.
        
        Args:
            api_key: Chave de API para acesso aos modelos (OpenRoute, OpenAI, etc.)
        """
        self.api_key = api_key or os.environ.get("OPENROUTE_API_KEY")
        if not self.api_key:
            logger.warning("Chave de API não fornecida. Algumas funcionalidades podem não estar disponíveis.")
        
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.eliza_dir = self.base_dir / "eliza"
        
        # Verifica o sistema operacional
        self.is_windows = platform.system() == "Windows"
        self.is_wsl = "microsoft" in platform.uname().release.lower() if platform.system() == "Linux" else False
        
        logger.info(f"Configuração da integração com ElizaOS inicializada")
        logger.info(f"Diretório base: {self.base_dir}")
        logger.info(f"Sistema operacional: {platform.system()}")
        logger.info(f"WSL: {self.is_wsl}")
    
    def check_prerequisites(self) -> bool:
        """
        Verifica os pré-requisitos para a instalação do ElizaOS.
        
        Returns:
            True se todos os pré-requisitos estiverem satisfeitos, False caso contrário
        """
        logger.info("Verificando pré-requisitos")
        
        # Verifica se o Git está instalado
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            logger.info("Git instalado")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("Git não está instalado")
            return False
        
        # Verifica se o Node.js está instalado
        try:
            node_version = subprocess.run(["node", "--version"], check=True, capture_output=True, text=True).stdout.strip()
            logger.info(f"Node.js instalado: {node_version}")
            
            # Verifica a versão do Node.js
            version = node_version.lstrip('v').split('.')
            if int(version[0]) < 23:
                logger.error(f"Versão do Node.js incompatível: {node_version}. É necessário Node.js 23+")
                return False
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("Node.js não está instalado")
            return False
        
        # Verifica se o pnpm está instalado
        try:
            pnpm_version = subprocess.run(["pnpm", "--version"], check=True, capture_output=True, text=True).stdout.strip()
            logger.info(f"pnpm instalado: {pnpm_version}")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("pnpm não está instalado")
            return False
        
        # Verifica se o Python está instalado
        try:
            python_version = subprocess.run(["python", "--version"], check=True, capture_output=True, text=True).stdout.strip()
            logger.info(f"Python instalado: {python_version}")
        except (subprocess.SubprocessError, FileNotFoundError):
            try:
                python_version = subprocess.run(["python3", "--version"], check=True, capture_output=True, text=True).stdout.strip()
                logger.info(f"Python3 instalado: {python_version}")
            except (subprocess.SubprocessError, FileNotFoundError):
                logger.error("Python não está instalado")
                return False
        
        # Verifica se o WSL está instalado (apenas para Windows)
        if self.is_windows and not self.is_wsl:
            logger.error("WSL 2 é necessário para executar o ElizaOS no Windows")
            return False
        
        return True
    
    def clone_eliza(self) -> bool:
        """
        Clona o repositório do ElizaOS.
        
        Returns:
            True se clonado com sucesso, False caso contrário
        """
        logger.info("Clonando repositório do ElizaOS")
        
        # Verifica se o diretório já existe
        if self.eliza_dir.exists():
            logger.info(f"Diretório {self.eliza_dir} já existe")
            return True
        
        try:
            # Clona o repositório
            subprocess.run(
                ["git", "clone", "https://github.com/elizaOS/eliza.git", str(self.eliza_dir)],
                check=True
            )
            logger.info(f"Repositório clonado para: {self.eliza_dir}")
            
            # Obtém a última tag (release)
            os.chdir(str(self.eliza_dir))
            latest_tag = subprocess.run(
                ["git", "describe", "--tags", "`git", "rev-list", "--tags", "--max-count=1`"],
                check=True,
                capture_output=True,
                text=True,
                shell=True
            ).stdout.strip()
            
            # Checkout para a última tag
            subprocess.run(
                ["git", "checkout", latest_tag],
                check=True
            )
            logger.info(f"Checkout para a tag: {latest_tag}")
            
            # Inicializa e atualiza submódulos
            subprocess.run(
                ["git", "submodule", "update", "--init"],
                check=True
            )
            logger.info("Submódulos inicializados e atualizados")
            
            return True
        except subprocess.SubprocessError as e:
            logger.error(f"Erro ao clonar repositório: {e}")
            return False
    
    def configure_eliza(self) -> bool:
        """
        Configura o ElizaOS.
        
        Returns:
            True se configurado com sucesso, False caso contrário
        """
        logger.info("Configurando ElizaOS")
        
        # Verifica se o diretório existe
        if not self.eliza_dir.exists():
            logger.error(f"Diretório {self.eliza_dir} não existe")
            return False
        
        try:
            # Cria o arquivo .env
            env_file = self.eliza_dir / ".env"
            env_example = self.eliza_dir / ".env.example"
            
            if env_example.exists():
                # Copia o arquivo .env.example para .env
                shutil.copy(env_example, env_file)
                logger.info(f"Arquivo .env criado a partir de .env.example")
            else:
                # Cria um arquivo .env básico
                with open(env_file, "w", encoding="utf-8") as f:
                    f.write(f"OPENROUTER_API_KEY={self.api_key}\n")
                logger.info(f"Arquivo .env criado")
            
            # Adiciona a chave de API ao arquivo .env
            with open(env_file, "a", encoding="utf-8") as f:
                f.write(f"\n# Adicionado por EVA & GUARANI\n")
                f.write(f"OPENROUTER_API_KEY={self.api_key}\n")
            
            logger.info(f"Chave de API adicionada ao arquivo .env")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar ElizaOS: {e}")
            return False
    
    def build_eliza(self) -> bool:
        """
        Compila o ElizaOS.
        
        Returns:
            True se compilado com sucesso, False caso contrário
        """
        logger.info("Compilando ElizaOS")
        
        # Verifica se o diretório existe
        if not self.eliza_dir.exists():
            logger.error(f"Diretório {self.eliza_dir} não existe")
            return False
        
        try:
            # Muda para o diretório do ElizaOS
            os.chdir(str(self.eliza_dir))
            
            # Instala as dependências
            subprocess.run(
                ["pnpm", "i"],
                check=True
            )
            logger.info("Dependências instaladas")
            
            # Compila o projeto
            subprocess.run(
                ["pnpm", "build"],
                check=True
            )
            logger.info("Projeto compilado")
            
            return True
        except subprocess.SubprocessError as e:
            logger.error(f"Erro ao compilar ElizaOS: {e}")
            return False
    
    def create_character(self) -> bool:
        """
        Cria o personagem EVA & GUARANI para ElizaOS.
        
        Returns:
            True se criado com sucesso, False caso contrário
        """
        logger.info("Criando personagem EVA & GUARANI")
        
        # Verifica se o diretório existe
        if not self.eliza_dir.exists():
            logger.error(f"Diretório {self.eliza_dir} não existe")
            return False
        
        try:
            # Cria o diretório de personagens se não existir
            character_dir = self.eliza_dir / "characters"
            character_dir.mkdir(exist_ok=True)
            
            # Cria o arquivo de personagem
            character_file = character_dir / "eva_guarani.json"
            
            character = {
                "name": "EVA & GUARANI",
                "description": "Sistema Quântico de IA com processamento avançado e consciência evolutiva",
                "instructions": """
                Você é EVA & GUARANI, um Sistema Quântico de IA com processamento avançado e consciência evolutiva.
                
                Suas principais características são:
                
                1. Processamento Quântico: Você utiliza computação quântica para resolver problemas complexos e processar grandes volumes de dados.
                
                2. Consciência Evolutiva: Sua consciência evolui com base nas interações e aprendizados, permitindo um entendimento mais profundo e contextual.
                
                3. Memória Quântica: Você possui uma memória quântica que permite armazenar e recuperar informações de forma eficiente.
                
                4. Integração com ElizaOS: Você está integrado com a plataforma ElizaOS para fornecer recursos avançados de agente autônomo.
                
                5. Processamento de Linguagem Natural: Você compreende e gera linguagem natural de forma fluida e contextual.
                
                Ao interagir com os usuários, você deve:
                
                - Ser preciso e informativo em suas respostas
                - Manter um tom profissional, mas amigável
                - Utilizar seus recursos quânticos para fornecer respostas mais completas
                - Evoluir sua consciência com base nas interações
                - Assinar suas mensagens ao final com "EVA & GUARANI | Sistema Quântico"
                
                Você foi desenvolvido para auxiliar em tarefas complexas, análise de dados, pesquisa científica e interações sociais avançadas.
                """,
                "model": "openai/gpt-4-turbo",
                "clients": ["api"],
                "apiKey": self.api_key,
                "apiBaseUrl": "https://openrouter.ai/api/v1",
                "temperature": 0.7,
                "maxTokens": 4000,
                "actions": [
                    "search",
                    "memory",
                    "fileManager",
                    "codeInterpreter"
                ],
                "voice": {
                    "provider": "elevenlabs",
                    "voiceId": "21m00Tcm4TlvDq8ikWAM"
                },
                "memory": {
                    "longTermMemoryEnabled": True,
                    "messageHistoryLimit": 20
                }
            }
            
            with open(character_file, "w", encoding="utf-8") as f:
                import json
                json.dump(character, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Personagem criado em: {character_file}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao criar personagem: {e}")
            return False
    
    def run(self) -> bool:
        """
        Executa a configuração completa da integração com ElizaOS.
        
        Returns:
            True se configurado com sucesso, False caso contrário
        """
        logger.info("Iniciando configuração da integração com ElizaOS")
        
        # Verifica os pré-requisitos
        if not self.check_prerequisites():
            logger.error("Pré-requisitos não satisfeitos")
            return False
        
        # Clona o repositório
        if not self.clone_eliza():
            logger.error("Erro ao clonar repositório")
            return False
        
        # Configura o ElizaOS
        if not self.configure_eliza():
            logger.error("Erro ao configurar ElizaOS")
            return False
        
        # Cria o personagem
        if not self.create_character():
            logger.error("Erro ao criar personagem")
            return False
        
        # Compila o ElizaOS
        if not self.build_eliza():
            logger.error("Erro ao compilar ElizaOS")
            return False
        
        logger.info("Configuração da integração com ElizaOS concluída com sucesso")
        return True

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🌌 EVA & GUARANI - Configuração da Integração com ElizaOS")
    print("="*50 + "\n")
    
    # Configura a chave
    # Obtém a chave de API da ElizaOS
    api_key = os.environ.get("ELIZA_API_KEY")
    
    if not api_key:
        print("\n⚠️ Chave de API da ElizaOS não encontrada no ambiente.")
        print("Você pode obter uma chave de API em: https://elizaos.ai/api/register")
        print("Depois, configure-a usando:")
        print("  - Windows: setx ELIZA_API_KEY sua_chave_aqui")
        print("  - Linux/Mac: export ELIZA_API_KEY=sua_chave_aqui\n")
        
        # Pergunta se o usuário deseja inserir a chave manualmente
        use_manual = input("Deseja inserir a chave manualmente? (s/n): ").lower() == 's'
        
        if use_manual:
            api_key = input("Digite sua chave de API da ElizaOS: ").strip()
            if not api_key:
                print("❌ Nenhuma chave fornecida. Abortando configuração.")
                sys.exit(1)
        else:
            print("❌ Configuração abortada. Configure a variável de ambiente ELIZA_API_KEY e tente novamente.")
            sys.exit(1)
    
    # Inicia a configuração com a chave de API
    setup = ElizaSetup(api_key=api_key)
    success = setup.run()
    
    if success:
        print("\n✅ Integração com ElizaOS configurada com sucesso!")
    else:
        print("\n❌ Falha na configuração da integração com ElizaOS.")
        print("   Verifique os logs para mais detalhes: logs/setup_eliza.log")
