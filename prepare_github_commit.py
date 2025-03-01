#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Preparação para Commit no GitHub - EVA & GUARANI
================================================

Este script prepara o repositório para commit no GitHub:
1. Identifica e move arquivos antigos para uma pasta de arquivamento
2. Remove arquivos grandes (>10MB) que não são essenciais
3. Gera um relatório de arquivos incluídos/excluídos
4. Cria um arquivo .gitignore apropriado

Versão: 1.0.0
Autor: EVA & GUARANI
"""

import os
import sys
import shutil
import datetime
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/github_prep.log', encoding='utf-8')
    ]
)

logger = logging.getLogger("GITHUB_PREP")

# Configurações
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB em bytes
ARCHIVE_DIR = "archived_files"
ESSENTIAL_LARGE_FILES = set()  # Adicione aqui caminhos de arquivos grandes que são essenciais

# Extensões e diretórios a serem ignorados
IGNORE_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.obj', '.o',
    '.a', '.lib', '.zip', '.tar', '.gz', '.rar', '.7z',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',
    '.log', '.tmp', '.temp', '.swp', '.swo', '.bak', '.backup'
}

IGNORE_DIRS = {
    '__pycache__', '.git', '.idea', '.vscode', 'venv', 'env',
    'node_modules', 'dist', 'build', 'target', 'out'
}

# Diretórios e arquivos essenciais que devem ser mantidos
ESSENTIAL_DIRS = {
    'modules', 'config', 'QUANTUM_PROMPTS', 'src', 'templates'
}

ESSENTIAL_FILES = {
    'README.md', 'LICENSE', 'requirements.txt', 'setup.py',
    'quantum_integration_hub.py', 'test_plugins.py'
}

def get_file_info(path: Path) -> Dict[str, Any]:
    """
    Obtém informações sobre um arquivo.
    
    Args:
        path: Caminho do arquivo.
        
    Returns:
        Dicionário com informações do arquivo.
    """
    stats = path.stat()
    return {
        'path': str(path),
        'size': stats.st_size,
        'size_mb': round(stats.st_size / (1024 * 1024), 2),
        'modified': datetime.datetime.fromtimestamp(stats.st_mtime).isoformat(),
        'is_large': stats.st_size > MAX_FILE_SIZE
    }

def should_ignore(path: Path) -> bool:
    """
    Verifica se um arquivo ou diretório deve ser ignorado.
    
    Args:
        path: Caminho do arquivo ou diretório.
        
    Returns:
        True se deve ser ignorado, False caso contrário.
    """
    # Verificar se é um diretório a ser ignorado
    if path.is_dir() and (path.name in IGNORE_DIRS or path.name.startswith('.')):
        return True
    
    # Verificar se é um arquivo com extensão a ser ignorada
    if path.is_file() and path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    
    return False

def is_essential(path: Path) -> bool:
    """
    Verifica se um arquivo ou diretório é essencial.
    
    Args:
        path: Caminho do arquivo ou diretório.
        
    Returns:
        True se é essencial, False caso contrário.
    """
    # Verificar diretórios essenciais
    for essential_dir in ESSENTIAL_DIRS:
        if str(path).startswith(essential_dir) or path.name == essential_dir:
            return True
    
    # Verificar arquivos essenciais
    if path.name in ESSENTIAL_FILES:
        return True
    
    # Verificar arquivos grandes essenciais
    if str(path) in ESSENTIAL_LARGE_FILES:
        return True
    
    return False

def scan_directory(directory: Path = Path('.')) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Escaneia um diretório e retorna informações sobre arquivos.
    
    Args:
        directory: Diretório a ser escaneado.
        
    Returns:
        Tupla com listas de arquivos a serem mantidos e arquivos a serem arquivados.
    """
    keep_files = []
    archive_files_list = []
    
    for item in directory.rglob('*'):
        # Ignorar diretórios
        if item.is_dir():
            continue
        
        # Ignorar arquivos específicos
        if should_ignore(item):
            continue
        
        file_info = get_file_info(item)
        
        # Decidir se mantém ou arquiva
        if file_info['is_large'] and not is_essential(item) and str(item) not in ESSENTIAL_LARGE_FILES:
            archive_files_list.append(file_info)
        else:
            keep_files.append(file_info)
    
    return keep_files, archive_files_list

def move_to_archive(files_to_archive: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Move arquivos para o diretório de arquivamento.
    
    Args:
        files_to_archive: Lista de informações de arquivos a serem arquivados.
        
    Returns:
        Tupla com o número de arquivos arquivados e o número de erros.
    """
    archive_dir = Path(ARCHIVE_DIR)
    archive_dir.mkdir(exist_ok=True)
    
    success_count = 0
    error_count = 0
    
    for file_info in files_to_archive:
        source_path = Path(file_info['path'])
        relative_path = source_path.relative_to(Path('.'))
        target_path = archive_dir / relative_path
        
        # Criar diretórios necessários
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Mover arquivo
            shutil.move(str(source_path), str(target_path))
            logger.info(f"Arquivo arquivado: {relative_path} ({file_info['size_mb']} MB)")
            success_count += 1
        except Exception as e:
            logger.error(f"Erro ao arquivar {relative_path}: {e}")
            error_count += 1
    
    return success_count, error_count

def create_gitignore() -> None:
    """
    Cria ou atualiza o arquivo .gitignore.
    """
    gitignore_content = """# EVA & GUARANI - EGOS .gitignore

# Arquivos de sistema
.DS_Store
Thumbs.db
desktop.ini

# Arquivos Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Logs
logs/
*.log

# Arquivos de configuração local
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Diretório de arquivamento
{}/

# IDEs e editores
.idea/
.vscode/
*.swp
*.swo
*~

# Arquivos temporários
*.tmp
*.temp
.coverage
htmlcov/

# Arquivos grandes (>10MB) não essenciais
# Adicione exceções específicas abaixo se necessário
""".format(ARCHIVE_DIR)
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    logger.info("Arquivo .gitignore criado/atualizado")

def generate_report(keep_files: List[Dict[str, Any]], archive_files: List[Dict[str, Any]]) -> None:
    """
    Gera um relatório sobre os arquivos mantidos e arquivados.
    
    Args:
        keep_files: Lista de informações de arquivos mantidos.
        archive_files: Lista de informações de arquivos arquivados.
    """
    report = {
        'timestamp': datetime.datetime.now().isoformat(),
        'summary': {
            'total_files_scanned': len(keep_files) + len(archive_files),
            'files_kept': len(keep_files),
            'files_archived': len(archive_files),
            'total_size_kept_mb': round(sum(f['size'] for f in keep_files) / (1024 * 1024), 2),
            'total_size_archived_mb': round(sum(f['size'] for f in archive_files) / (1024 * 1024), 2)
        },
        'large_files_kept': [f for f in keep_files if f['is_large']],
        'archived_files': archive_files
    }
    
    # Salvar relatório como JSON
    with open('github_prep_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Exibir resumo
    logger.info(f"Relatório gerado: github_prep_report.json")
    logger.info(f"Total de arquivos escaneados: {report['summary']['total_files_scanned']}")
    logger.info(f"Arquivos mantidos: {report['summary']['files_kept']} ({report['summary']['total_size_kept_mb']} MB)")
    logger.info(f"Arquivos arquivados: {report['summary']['files_archived']} ({report['summary']['total_size_archived_mb']} MB)")
    
    # Listar arquivos grandes mantidos
    if report['large_files_kept']:
        logger.info("Arquivos grandes mantidos:")
        for file in report['large_files_kept']:
            logger.info(f"  - {file['path']} ({file['size_mb']} MB)")

def main() -> int:
    """
    Função principal.
    
    Returns:
        Código de saída (0 para sucesso, 1 para erro).
    """
    logger.info("Iniciando preparação para commit no GitHub")
    
    try:
        # Escanear diretório
        logger.info("Escaneando diretório...")
        keep_files, archive_files_list = scan_directory()
        
        # Arquivar arquivos
        if archive_files_list:
            logger.info(f"Arquivando {len(archive_files_list)} arquivos...")
            success_count, error_count = move_to_archive(archive_files_list)
            logger.info(f"Arquivamento concluído: {success_count} sucesso, {error_count} erros")
        else:
            logger.info("Nenhum arquivo para arquivar")
        
        # Criar .gitignore
        logger.info("Criando arquivo .gitignore...")
        create_gitignore()
        
        # Gerar relatório
        logger.info("Gerando relatório...")
        generate_report(keep_files, archive_files_list)
        
        logger.info("Preparação para commit concluída com sucesso!")
        return 0
    
    except Exception as e:
        logger.exception(f"Erro durante a preparação: {e}")
        return 1

if __name__ == "__main__":
    # Criar diretório de logs se não existir
    Path("logs").mkdir(exist_ok=True)
    
    sys.exit(main()) 