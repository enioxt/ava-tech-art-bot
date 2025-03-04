#!/usr/bin/env python
"""
Script de Configuração da API Perplexity - EVA & GUARANI
--------------------------------------------------------
Este script configura a API key da Perplexity para uso no sistema EVA & GUARANI.
"""

import sys
import os
from services.config import config_manager

def setup_perplexity_api():
    """Configura a API key da Perplexity para o sistema."""
    print("\n========== Configuração da API Perplexity ==========")
    print("Este script configurará a API key da Perplexity para o sistema EVA & GUARANI.")
    
    # Verificar se já está configurada
    if config_manager.is_configured("perplexity"):
        existing_key = config_manager.get_key("perplexity")
        masked_key = f"{existing_key[:8]}...{existing_key[-4:]}" if existing_key else ""
        print(f"\nUma API key da Perplexity já está configurada: {masked_key}")
        
        choice = input("\nDeseja substituí-la? (s/n): ").strip().lower()
        if choice != 's':
            print("Configuração cancelada. A API key existente será mantida.")
            return
    
    # Obter a nova API key
    print("\nVocê pode obter uma API key da Perplexity em: https://www.perplexity.ai/settings/api")
    
    # Usar a API key fornecida como argumento ou solicitar ao usuário
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        print("\nAPI key fornecida via argumento de linha de comando.")
    else:
        api_key = input("\nDigite sua API key da Perplexity: ").strip()
    
    if not api_key.startswith("pplx-"):
        print("\nAVISO: A API key fornecida não parece ser válida (deve começar com 'pplx-').")
        confirm = input("Deseja continuar mesmo assim? (s/n): ").strip().lower()
        if confirm != 's':
            print("Configuração cancelada.")
            return
    
    # Salvar a API key
    config_manager.set_key("perplexity", api_key)
    print("\nAPI key da Perplexity configurada com sucesso!")
    
    # Informações adicionais
    print("\nA API key está armazenada em:", config_manager.config_path)
    print("Para usar a API em ambiente de produção, considere configurar")
    print("a variável de ambiente PERPLEXITY_API_KEY ao invés de armazenar no arquivo.")
    
    # Testar conexão
    print("\nDeseja testar a conexão com a API? (s/n): ", end="")
    test_choice = input().strip().lower()
    if test_choice == 's':
        test_perplexity_connection()

def test_perplexity_connection():
    """Testa a conexão com a API da Perplexity."""
    try:
        from services.perplexity_service import PerplexityService
        
        print("\nTestando conexão com a API da Perplexity...")
        perplexity = PerplexityService()
        
        test_query = "Qual é o dia de hoje?"
        print(f"\nConsulta de teste: '{test_query}'")
        
        results = perplexity.search(test_query)
        
        if results.get("status") == "success":
            print("\n✅ Conexão estabelecida com sucesso!")
            print("\nExemplo de resultado:")
            if "results" in results:
                # Mostrar apenas uma prévia do resultado para não sobrecarregar o terminal
                result_preview = str(results["results"])[:200] + "..." if len(str(results["results"])) > 200 else str(results["results"])
                print(result_preview)
            
            if "sources" in results:
                print(f"\nFontes: {len(results['sources'])} encontradas")
        else:
            print("\n❌ Falha na conexão:")
            print(results.get("error_message", "Erro desconhecido"))
    
    except ImportError:
        print("\n❌ Erro: Módulo PerplexityService não encontrado.")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")

if __name__ == "__main__":
    # Ajustar PYTHONPATH para acessar os módulos
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    setup_perplexity_api() 