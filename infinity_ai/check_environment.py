import os
import sys
import pkg_resources
import platform
import logging
import requests
import shutil
import git
from datetime import datetime
from pathlib import Path
from colorama import init, Fore, Back, Style
from tqdm import tqdm
import time
import json

# Inicializa o colorama para Windows
init()

# Arte ASCII para o cabeçalho (usando caracteres ASCII simples para Windows)
HEADER_ART = f"""
{Fore.CYAN}
    +------------------------------------------------+
    |  _____   ____  _____    _____ _               _|
    | / ____|/ __ \\|  __ \\  / ____| |             | |
    || |    | |  | | |__) || |    | |__   ___  ___| |
    || |    | |  | |  _  / | |    | '_ \\ / _ \\/ __| |
    || |____| |__| | | \\ \\ | |____| | | |  __/ (__|_|
    | \\_____|\____/|_|  \\_\\ \\_____| |_|\\___|\\___|_|
    |                                                 |
    |     Arte & Tecnologia em Perfeita Harmonia     |
    +------------------------------------------------+
{Style.RESET_ALL}"""

# Configuração de logging com estilo
class ColoredFormatter(logging.Formatter):
    def __init__(self):
        super().__init__('%(levelname)s - %(message)s')
        self.level_colors = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.RED + Style.BRIGHT
        }
        self.level_icons = {
            'DEBUG': '*',
            'INFO': '+',
            'WARNING': '!',
            'ERROR': 'X',
            'CRITICAL': '!!'
        }

    def format(self, record):
        # Add color
        color = self.level_colors.get(record.levelname, '')
        icon = self.level_icons.get(record.levelname, '')
        
        # Format the message
        record.msg = f"{color}[{icon}] {record.msg}{Style.RESET_ALL}"
        return super().format(record)

def setup_logging():
    """Configura o sistema de logging com cores e ícones."""
    logger = logging.getLogger('environment_checker')
    logger.setLevel(logging.DEBUG)

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    # File handler
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_handler = logging.FileHandler(
        log_dir / f'environment_check_{timestamp}.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(file_handler)

    return logger

def show_progress(description, total=10):
    """Mostra uma barra de progresso estilizada"""
    with tqdm(total=total, desc=f"{Fore.CYAN}{description}{Style.RESET_ALL}",
              bar_format="{l_bar}{bar:30}{r_bar}") as pbar:
        for _ in range(total):
            time.sleep(0.1)
            pbar.update(1)

def check_python_version():
    """Verifica a versão do Python instalada."""
    logger.info("Analisando a versao do Python...")
    
    with tqdm(total=10, desc="Verificando compatibilidade") as pbar:
        current_version = sys.version.split()[0]
        pbar.update(5)
        
        # Verifica se a versão está entre 3.8 e 3.11
        version_parts = current_version.split('.')
        major, minor = map(int, version_parts[:2])
        
        if not (major == 3 and 8 <= minor <= 11):
            logger.error(f"Python {current_version} encontrado, mas precisamos de 3.8-3.11")
            logger.info("Dica: Considere usar pyenv para gerenciar multiplas versoes")
            pbar.update(5)
            return False
            
        logger.info(f"Python {current_version} - OK!")
        pbar.update(5)
        return True

def check_git_repos():
    """Verifica os repositórios Git."""
    logger.info("Investigando repositorios Git...")
    
    with tqdm(total=10, desc="Analisando repositórios") as pbar:
        try:
            repo = git.Repo(os.getcwd())
            pbar.update(3)
            
            logger.info(f"Repositorio: {repo.working_tree_dir}")
            logger.info(f"Branch atual: {repo.active_branch.name}")
            pbar.update(3)
            
            for remote in repo.remotes:
                logger.info(f"Remote encontrado: {remote.name} ({remote.url})")
            pbar.update(2)
            
            if repo.is_dirty():
                logger.warning("Atencao: Ha alteracoes nao commitadas!")
            
            pbar.update(2)
            return True
            
        except git.exc.InvalidGitRepositoryError:
            logger.error("Diretorio atual nao e um repositorio Git!")
            pbar.update(7)
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar Git: {str(e)}")
            pbar.update(7)
            return False

def check_network():
    """Verifica a conectividade de rede."""
    logger.info("Testando conectividade...")
    
    endpoints = [
        "https://api.telegram.org",
        "https://github.com",
        "https://pypi.org"
    ]
    
    with tqdm(total=10, desc="Verificando conexões") as pbar:
        all_ok = True
        step = 10 / len(endpoints)
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    logger.info(f"Conexao com {endpoint} - OK!")
                else:
                    logger.warning(f"Resposta inesperada de {endpoint}: {response.status_code}")
                    all_ok = False
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao conectar com {endpoint}: {str(e)}")
                all_ok = False
            
            pbar.update(step)
        
        return all_ok

def check_system_resources():
    """Verifica recursos do sistema"""
    logger.info("🔧 Analisando recursos do sistema...")
    show_progress("Verificando recursos")
    
    # CPU Info
    logger.info(f"💻 Processador: {platform.processor()}")
    
    # Memória
    try:
        import psutil
        mem = psutil.virtual_memory()
        logger.info(f"💾 Memória Total: {mem.total / (1024**3):.2f} GB")
        logger.info(f"💫 Memória Disponível: {mem.available / (1024**3):.2f} GB")
    except ImportError:
        logger.warning("⚠️ psutil não instalado - info de memória indisponível")
    
    # Espaço em disco
    disk = shutil.disk_usage('/')
    logger.info(f"💿 Espaço em Disco: {disk.free / (1024**3):.2f} GB livre")
    
    return True

def main():
    """Função principal com interface amigável"""
    print(HEADER_ART)
    
    # Configurar logging
    global logger
    logger = setup_logging()
    
    logger.info("Iniciando verificacao do ambiente...")
    
    checks = [
        ("Versao do Python", check_python_version),
        ("Repositorios Git", check_git_repos),
        ("Conectividade", check_network),
        ("Recursos do Sistema", check_system_resources)
    ]
    
    results = []
    for check_name, check_func in checks:
        logger.info(f"\n{Fore.CYAN}{'='*20} {check_name} {'='*20}{Style.RESET_ALL}")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            results.append(False)
    
    # Gera relatório
    log_dir = Path('logs')
    report_file = log_dir / f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "os": platform.system(),
            "version": platform.version(),
            "python": sys.version,
            "processor": platform.processor()
        },
        "checks": {
            "python_version": results[0],
            "git": results[1],
            "network": results[2],
            "resources": results[3]
        }
    }
    
    log_dir.mkdir(exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    # Resultado final
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    if all(results):
        print(f"""
{Fore.GREEN}
    Ambiente Configurado com Sucesso!
    
    Tudo esta pronto para comecar.
    
    "A arte desafia a tecnologia, e a tecnologia inspira a arte."
                                        - John Lasseter
{Style.RESET_ALL}
        """)
    else:
        print(f"""
{Fore.YELLOW}
    Alguns Ajustes Sao Necessarios
    
    Como em toda obra de arte, as vezes precisamos
    fazer alguns retoques para alcancar a perfeicao.
    
    Consulte o log para mais detalhes: {report_file}
{Style.RESET_ALL}
        """)
    
    logger.info(f"Relatorio completo salvo em: {report_file}")
    return all(results)

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Verificacao interrompida pelo usuario!{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Erro inesperado: {str(e)}{Style.RESET_ALL}")
        sys.exit(1) 