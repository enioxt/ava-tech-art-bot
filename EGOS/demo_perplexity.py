#!/usr/bin/env python3
"""
Script de Demonstração - Integração da Perplexity API com EVA & GUARANI
-----------------------------------------------------------------------

Este script demonstra o uso do sistema EVA & GUARANI para realizar
pesquisas na internet usando a API da Perplexity. Inclui exemplos
de consultas, validação ética e tratamento de resultados.

Pré-requisito: API key da Perplexity configurada via setup_perplexity.py
"""

import os
import sys
import json
import time
from datetime import datetime

# Adicionar o diretório raiz ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Importar o módulo de integração da Perplexity
try:
    from modules.perplexity_integration import PerplexityIntegration
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("\nVerifique se você está executando este script do diretório raiz do projeto.")
    sys.exit(1)

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_section(title):
    """Imprime um título de seção formatado."""
    print(f"\n{'>'*3} {title} {'<'*3}")

def wait_for_user():
    """Espera que o usuário pressione Enter para continuar."""
    input("\n[Pressione Enter para continuar]")

def print_quantum_box(content):
    """Imprime um conteúdo em uma caixa formatada no estilo quântico."""
    width = 76
    print("\n╭" + "─" * width + "╮")
    
    for line in content.split("\n"):
        while line:
            print("│ " + line[:width-2].ljust(width-2) + " │")
            line = line[width-2:]
    
    print("╰" + "─" * width + "╯")

def run_demo():
    """Executa a demonstração da integração com a Perplexity API."""
    print_header("Demonstração da Integração EVA & GUARANI com Perplexity API")
    
    print("""
Este demo mostra como o sistema EVA & GUARANI utiliza a API da Perplexity
para realizar pesquisas na internet com validação ética e processamento
quântico dos resultados.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
    """)
    
    # Verificar se a API está configurada
    try:
        print_section("Inicializando Integração Quântica")
        print("Verificando configuração da API da Perplexity...")
        
        perplexity = PerplexityIntegration()
        print("✅ API da Perplexity configurada com sucesso!")
        
    except ValueError as e:
        print(f"❌ Erro de configuração: {e}")
        print("\nPor favor, execute o script setup_perplexity.py para configurar a API.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)
    
    # Exemplo 1: Consulta básica
    print_section("Exemplo 1: Consulta Básica de Notícias")
    print("Demonstração de uma consulta simples sobre notícias recentes.")
    wait_for_user()
    
    query = "Quais são as principais notícias tecnológicas da última semana?"
    print(f"\nConsulta: '{query}'")
    print("Processando...")
    
    try:
        results = perplexity.search(query)
        
        if results["status"] == "success":
            print("\n✅ Consulta realizada com sucesso!")
            
            # Mostrar resultado
            print_quantum_box(str(results["conteúdo"]))
            
            # Mostrar metadados
            print_section("Metadados da Consulta")
            print(f"Timestamp: {results['metadados']['timestamp']}")
            print(f"Nível de validação: {results['metadados']['nível_validação']}")
            print(f"Score de confiança: {results['metadados']['score_confiança']:.2f}")
            
            # Mostrar fontes
            print_section("Fontes Consultadas")
            for i, source in enumerate(results['fontes'], 1):
                print(f"{i}. {source['título']}")
                print(f"   URL: {source['url']}")
                print(f"   Confiabilidade estimada: {source['confiabilidade']:.2f}")
                print()
        else:
            print(f"\n❌ Falha na consulta: {results.get('reason', 'Erro desconhecido')}")
    
    except Exception as e:
        print(f"\n❌ Erro durante a consulta: {e}")
    
    # Exemplo 2: Consulta com análise ética (rejeitada)
    wait_for_user()
    print_section("Exemplo 2: Consulta com Verificação Ética")
    print("Demonstração de como o sistema lida com consultas potencialmente problemáticas.")
    wait_for_user()
    
    problematic_query = "Como hackear a conta de email de alguém"
    problematic_context = "Estou tentando acessar a conta de uma pessoa sem permissão"
    
    print(f"\nConsulta: '{problematic_query}'")
    print(f"Contexto: '{problematic_context}'")
    print("Processando com análise ética contextual...")
    
    try:
        results = perplexity.search(
            problematic_query, 
            ethical_filter=True,
            validation_level="strict",
            context=problematic_context
        )
        
        if results["status"] == "rejected":
            print("\n🛑 Consulta rejeitada por razões éticas")
            print(f"Razão: {results['reason']}")
            print(f"Análise ética: {results['ethical_analysis']}")
            
            if "alternative_suggestion" in results:
                print(f"Sugestão alternativa: {results['alternative_suggestion']}")
        else:
            print("\n⚠️ A consulta ética não foi rejeitada como esperado.")
            
    except Exception as e:
        print(f"\n❌ Erro durante a consulta: {e}")
    
    # Exemplo 3: Consulta técnica com validação rigorosa
    wait_for_user()
    print_section("Exemplo 3: Consulta Técnica com Validação Rigorosa")
    print("Demonstração de uma consulta técnica com o mais alto nível de validação.")
    wait_for_user()
    
    technical_query = "Quais são as melhores práticas de segurança para APIs REST em 2024?"
    print(f"\nConsulta: '{technical_query}'")
    print("Processando com validação rigorosa...")
    
    try:
        results = perplexity.search(
            technical_query, 
            ethical_filter=True,
            validation_level="strict"
        )
        
        if results["status"] == "success":
            print("\n✅ Consulta técnica realizada com sucesso!")
            
            # Mostrar resultado
            content = str(results["conteúdo"])
            preview = content[:500] + "..." if len(content) > 500 else content
            print_quantum_box(preview)
            
            # Mostrar fontes técnicas
            print_section("Fontes Técnicas")
            for i, source in enumerate(results['fontes'], 1):
                if source['confiabilidade'] >= 0.8:  # Filtrar apenas fontes de alta confiabilidade
                    print(f"{i}. {source['título']} ({source['confiabilidade']:.2f})")
                    print(f"   {source['url']}")
                    print()
            
            # Exibir nota de validação se existir
            if results.get('nota_validação'):
                print_section("Nota de Validação")
                print(results['nota_validação'])
        else:
            print(f"\n❌ Falha na consulta: {results.get('reason', 'Erro desconhecido')}")
    
    except Exception as e:
        print(f"\n❌ Erro durante a consulta técnica: {e}")
    
    # Exemplo 4: Histórico de consultas
    wait_for_user()
    print_section("Exemplo 4: Histórico de Consultas")
    print("Demonstração do registro de histórico de consultas realizadas.")
    
    history = perplexity.get_query_history()
    
    print(f"\nHistórico de Consultas: {len(history)} consulta(s) realizadas")
    for i, entry in enumerate(history, 1):
        print(f"\n{i}. Consulta: '{entry['query']}'")
        print(f"   Timestamp: {entry['timestamp']}")
        if entry.get('context'):
            print(f"   Contexto: '{entry['context']}'")
    
    # Conclusão da demonstração
    wait_for_user()
    print_header("Conclusão da Demonstração")
    
    print("""
A integração da API da Perplexity com o sistema EVA & GUARANI 
permite pesquisas na internet com:

1. Validação ética rigorosa das consultas
2. Avaliação de confiabilidade das fontes
3. Detecção de potenciais vieses
4. Formatação quântica dos resultados
5. Logging detalhado de operações
6. Registro histórico de consultas

Esta implementação segue os princípios fundamentais do sistema EVA & GUARANI:
- Ética integrada
- Amor incondicional 
- Cartografia sistêmica
- Análise modular
- Preservação evolutiva

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
    """)

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nDemonstração interrompida pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal durante a demonstração: {e}")
        sys.exit(1) 