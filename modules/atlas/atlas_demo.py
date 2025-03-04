#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✧༺❀༻∞ ATLAS - Demo de Cartografia Sistêmica ∞༺❀༻✧
====================================================

Este script demonstra as capacidades do subsistema ATLAS do EGOS,
permitindo mapear e visualizar a estrutura de um projeto.

Uso:
    python atlas_demo.py --project /caminho/do/projeto [--output formato] [--export diretório]

Autor: Comunidade EGOS
Versão: 1.0.0
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Adicionar diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ATLAS.Demo")

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(message, color=Colors.CYAN, bold=False):
    """Imprime mensagem colorida no terminal."""
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{message}{Colors.ENDC}")

def print_banner():
    """Exibe o banner do ATLAS."""
    banner = f"""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║                       ✧༺❀༻∞ ATLAS ∞༺❀༻✧                          ║
║                      Cartografia Sistêmica                         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """
    print_colored(banner, Colors.CYAN, bold=True)
    print_colored("Demonstração do subsistema de cartografia do EGOS\n", Colors.BLUE)

def parse_arguments():
    """Analisa os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="ATLAS - Cartografia Sistêmica")
    parser.add_argument("--project", type=str, required=True, help="Caminho para o projeto a ser mapeado")
    parser.add_argument("--output", type=str, default="json", choices=["json", "md", "html"], help="Formato de saída")
    parser.add_argument("--export", type=str, help="Diretório para exportar visualização para Obsidian")
    parser.add_argument("--config", type=str, help="Caminho para arquivo de configuração personalizado")
    return parser.parse_args()

def main():
    """Função principal."""
    # Exibir banner
    print_banner()
    
    # Analisar argumentos
    args = parse_arguments()
    
    # Verificar se o projeto existe
    if not os.path.exists(args.project):
        print_colored(f"Erro: O caminho do projeto '{args.project}' não existe", Colors.RED)
        return 1
    
    print_colored(f"Mapeando projeto: {args.project}", Colors.BLUE)
    print_colored(f"Formato de saída: {args.output}", Colors.BLUE)
    
    try:
        # Importar o módulo ATLAS
        from modules.atlas import AtlasModule
        
        # Configuração
        config_path = args.config
        if not config_path:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                      "config", "modules", "atlas_config.json")
        
        # Inicializar o ATLAS
        print_colored("Inicializando ATLAS...", Colors.BLUE)
        atlas = AtlasModule(config_path)
        
        # Mapear o projeto
        print_colored("Mapeando estrutura do projeto...", Colors.BLUE)
        mapping = atlas.map_project(args.project, args.output)
        
        # Exibir estatísticas
        print_colored("\nEstatísticas do mapeamento:", Colors.GREEN, bold=True)
        print(f"  Projeto: {mapping['project']}")
        print(f"  Caminho: {mapping['path']}")
        print(f"  Timestamp: {mapping['timestamp']}")
        print(f"  Nós: {len(mapping['nodes'])}")
        print(f"  Conexões: {len(mapping['edges'])}")
        print(f"  Métricas:")
        print(f"    - Arquivos: {mapping['metrics']['files']}")
        print(f"    - Diretórios: {mapping['metrics']['directories']}")
        print(f"    - Conexões: {mapping['metrics']['connections']}")
        print(f"    - Complexidade: {mapping['metrics']['complexity']}")
        
        # Gerar visualização
        print_colored("\nGerando visualização...", Colors.BLUE)
        visualization_path = atlas.visualize_mapping(mapping)
        print_colored(f"Visualização gerada em: {visualization_path}", Colors.GREEN)
        
        # Exportar para Obsidian se solicitado
        if args.export:
            print_colored(f"\nExportando para Obsidian em: {args.export}", Colors.BLUE)
            files = atlas.export_to_obsidian(mapping, args.export)
            print_colored(f"Exportação concluída: {len(files)} arquivos gerados", Colors.GREEN)
            for file in files:
                print(f"  - {file}")
        
        print_colored("\n⊹⊱∞⊰⊹ ATLAS: Mapeando com Amor ⊹⊰∞⊱⊹\n", Colors.CYAN, bold=True)
        return 0
        
    except ImportError as e:
        print_colored(f"Erro ao importar ATLAS: {str(e)}", Colors.RED)
        return 1
    except Exception as e:
        print_colored(f"Erro durante execução: {str(e)}", Colors.RED)
        logger.error(f"Erro: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
