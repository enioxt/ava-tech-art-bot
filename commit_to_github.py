#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Commit para GitHub - EVA & GUARANI
==================================

Este script realiza o commit e push das alterações para o GitHub.
Ele verifica se o repositório está configurado corretamente e
executa os comandos git necessários.

Versão: 1.0.0
Autor: EVA & GUARANI
"""

import os
import sys
import subprocess
import logging
import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/github_commit.log', encoding='utf-8')
    ]
)

logger = logging.getLogger("GITHUB_COMMIT")

def run_command(command, check=True):
    """
    Executa um comando no shell e retorna o resultado.
    
    Args:
        command: Comando a ser executado.
        check: Se True, levanta uma exceção se o comando falhar.
        
    Returns:
        Tupla com (stdout, stderr) se o comando for bem-sucedido.
    """
    try:
        result = subprocess.run(
            command,
            check=check,
            text=True,
            capture_output=True,
            shell=True
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar comando: {e}")
        logger.error(f"Saída de erro: {e.stderr}")
        if check:
            raise
        return None, e.stderr

def is_git_repo():
    """
    Verifica se o diretório atual é um repositório Git.
    
    Returns:
        True se for um repositório Git, False caso contrário.
    """
    try:
        run_command("git rev-parse --is-inside-work-tree")
        return True
    except subprocess.CalledProcessError:
        return False

def init_git_repo():
    """
    Inicializa um repositório Git se ainda não existir.
    
    Returns:
        True se o repositório foi inicializado com sucesso, False caso contrário.
    """
    try:
        if not is_git_repo():
            logger.info("Inicializando repositório Git...")
            run_command("git init")
            logger.info("Repositório Git inicializado com sucesso!")
        else:
            logger.info("Repositório Git já existe.")
        return True
    except Exception as e:
        logger.error(f"Erro ao inicializar repositório Git: {e}")
        return False

def configure_git_user():
    """
    Configura o usuário e email do Git se ainda não estiverem configurados.
    
    Returns:
        True se a configuração foi bem-sucedida, False caso contrário.
    """
    try:
        # Verificar se o nome de usuário está configurado
        stdout, _ = run_command("git config user.name", check=False)
        if not stdout:
            name = input("Digite seu nome para configuração do Git: ")
            run_command(f'git config user.name "{name}"')
            logger.info(f"Nome de usuário configurado: {name}")
        
        # Verificar se o email está configurado
        stdout, _ = run_command("git config user.email", check=False)
        if not stdout:
            email = input("Digite seu email para configuração do Git: ")
            run_command(f'git config user.email "{email}"')
            logger.info(f"Email configurado: {email}")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar usuário Git: {e}")
        return False

def add_files():
    """
    Adiciona todos os arquivos ao staging area.
    
    Returns:
        True se os arquivos foram adicionados com sucesso, False caso contrário.
    """
    try:
        logger.info("Adicionando arquivos ao staging area...")
        run_command("git add .")
        logger.info("Arquivos adicionados com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao adicionar arquivos: {e}")
        return False

def create_commit(message=None):
    """
    Cria um commit com a mensagem especificada.
    
    Args:
        message: Mensagem de commit. Se None, uma mensagem padrão será usada.
        
    Returns:
        True se o commit foi criado com sucesso, False caso contrário.
    """
    try:
        if message is None:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            message = f"EVA & GUARANI - Atualização {date_str}"
        
        logger.info(f"Criando commit: {message}")
        run_command(f'git commit -m "{message}"')
        logger.info("Commit criado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar commit: {e}")
        return False

def configure_remote(force=False):
    """
    Configura o repositório remoto se ainda não estiver configurado.
    
    Args:
        force: Se True, reconfigura mesmo se já existir.
        
    Returns:
        True se a configuração foi bem-sucedida, False caso contrário.
    """
    try:
        # Verificar se o remote já está configurado
        stdout, _ = run_command("git remote -v", check=False)
        
        if not stdout or force:
            remote_url = input("Digite a URL do repositório GitHub: ")
            if remote_url:
                # Remover remote existente se necessário
                if stdout:
                    run_command("git remote remove origin", check=False)
                
                # Adicionar novo remote
                run_command(f"git remote add origin {remote_url}")
                logger.info(f"Repositório remoto configurado: {remote_url}")
                return True
            else:
                logger.warning("URL do repositório não fornecida. Configuração de remote ignorada.")
                return False
        else:
            logger.info(f"Repositório remoto já configurado: {stdout}")
            return True
    except Exception as e:
        logger.error(f"Erro ao configurar repositório remoto: {e}")
        return False

def push_to_remote():
    """
    Envia as alterações para o repositório remoto.
    
    Returns:
        True se o push foi bem-sucedido, False caso contrário.
    """
    try:
        # Verificar se o remote está configurado
        stdout, _ = run_command("git remote -v", check=False)
        if not stdout:
            logger.warning("Repositório remoto não configurado. Push ignorado.")
            return False
        
        # Obter o branch atual
        branch, _ = run_command("git rev-parse --abbrev-ref HEAD")
        if not branch:
            branch = "main"  # Default para repositórios modernos
        
        logger.info(f"Enviando alterações para o branch {branch}...")
        run_command(f"git push -u origin {branch}")
        logger.info("Alterações enviadas com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar alterações: {e}")
        return False

def main():
    """
    Função principal.
    
    Returns:
        Código de saída (0 para sucesso, 1 para erro).
    """
    print("\n==================================================")
    print("🌌 EVA & GUARANI - Commit para GitHub")
    print("==================================================\n")
    
    try:
        # Verificar se o diretório é um repositório Git
        if not init_git_repo():
            return 1
        
        # Configurar usuário Git
        if not configure_git_user():
            return 1
        
        # Adicionar arquivos
        if not add_files():
            return 1
        
        # Verificar se há alterações para commit
        stdout, _ = run_command("git status --porcelain", check=False)
        if not stdout:
            logger.info("Não há alterações para commit.")
            print("\nNão há alterações para commit.")
            return 0
        
        # Criar commit
        commit_message = input("Digite a mensagem de commit (ou pressione Enter para usar a mensagem padrão): ")
        if not create_commit(commit_message if commit_message else None):
            return 1
        
        # Configurar repositório remoto
        reconfigure = input("Deseja configurar/reconfigurar o repositório remoto? (s/N): ").lower() == 's'
        if reconfigure and not configure_remote(force=True):
            logger.warning("Configuração de repositório remoto ignorada.")
        
        # Perguntar se deseja fazer push
        do_push = input("Deseja enviar as alterações para o GitHub? (S/n): ").lower() != 'n'
        if do_push:
            if not push_to_remote():
                logger.warning("Push para o repositório remoto falhou.")
                print("\nPush para o repositório remoto falhou.")
                return 1
        
        print("\n==================================================")
        print("Commit para GitHub concluído com sucesso!")
        print("==================================================")
        return 0
    
    except Exception as e:
        logger.exception(f"Erro durante o processo: {e}")
        print(f"\nErro durante o processo: {e}")
        return 1

if __name__ == "__main__":
    # Criar diretório de logs se não existir
    Path("logs").mkdir(exist_ok=True)
    
    sys.exit(main())
