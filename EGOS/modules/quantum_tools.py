"""
Ferramentas Quânticas - EVA & GUARANI
-------------------------------------
Este módulo fornece ferramentas de alto nível que integram os diversos
subsistemas do EVA & GUARANI, incluindo cartografia sistêmica (ATLAS),
análise modular (NEXUS), preservação evolutiva (CRONOS) e pesquisa na
internet (PERPLEXITY).
"""

import os
import sys
from typing import Dict, Any, List, Union, Optional
from datetime import datetime
import json

# Adicionar o diretório raiz ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
egos_dir = os.path.dirname(current_dir)
if egos_dir not in sys.path:
    sys.path.append(egos_dir)

# Importações dos subsistemas
try:
    from .perplexity_integration import PerplexityIntegration
except ImportError:
    # Fallback para desenvolvimento
    PerplexityIntegration = None
    print("[AVISO] Módulo de pesquisa web (PERPLEXITY) não disponível")

class QuantumTools:
    """
    Ferramentas quânticas integradas do sistema EVA & GUARANI.
    Fornece uma interface unificada para acessar os subsistemas
    ATLAS, NEXUS, CRONOS e PERPLEXITY.
    """
    
    def __init__(self):
        """Inicializa as ferramentas quânticas."""
        self.initialized_at = datetime.now()
        self.log_entries = []
        
        # Inicializar o subsistema de pesquisa web se disponível
        self.perplexity = None
        if PerplexityIntegration:
            try:
                self.perplexity = PerplexityIntegration()
                self._log_quantum_operation(
                    "INICIALIZAÇÃO", 
                    "Módulo PERPLEXITY inicializado com sucesso"
                )
            except Exception as e:
                self._log_quantum_operation(
                    "ERRO", 
                    f"Falha ao inicializar módulo PERPLEXITY: {str(e)}"
                )
    
    def search_web(self, 
                  query: str, 
                  ethical_filter: bool = True,
                  validation_level: str = "standard",
                  context: Optional[str] = None) -> Dict[str, Any]:
        """
        Realiza uma pesquisa na web usando o subsistema PERPLEXITY.
        
        Args:
            query: Consulta para pesquisa
            ethical_filter: Se deve aplicar filtros éticos
            validation_level: Nível de validação ("basic", "standard", "strict")
            context: Contexto adicional da consulta
            
        Returns:
            Resultados da pesquisa com metadados quânticos
        """
        if not self.perplexity:
            return {
                "status": "error",
                "error_message": "Módulo PERPLEXITY não disponível",
                "timestamp": datetime.now().isoformat()
            }
            
        self._log_quantum_operation(
            "PESQUISA_WEB", 
            f"Iniciando consulta: '{query}'",
            f"Validação: {validation_level}"
        )
        
        try:
            results = self.perplexity.search(
                query=query,
                ethical_filter=ethical_filter,
                validation_level=validation_level,
                context=context
            )
            
            if results.get("status") == "success":
                self._log_quantum_operation(
                    "PESQUISA_CONCLUÍDA", 
                    f"Consulta bem-sucedida: '{query}'",
                    f"Fontes: {len(results.get('fontes', []))}"
                )
            else:
                self._log_quantum_operation(
                    "PESQUISA_FALHOU", 
                    f"Consulta falhou: '{query}'",
                    results.get("reason", "Motivo desconhecido")
                )
                
            return results
            
        except Exception as e:
            error_message = f"Erro durante a pesquisa: {str(e)}"
            self._log_quantum_operation("ERRO", error_message)
            
            return {
                "status": "error",
                "error_message": error_message,
                "timestamp": datetime.now().isoformat(),
                "query": query
            }
    
    def get_web_search_history(self) -> List[Dict[str, str]]:
        """
        Retorna o histórico de pesquisas na web.
        
        Returns:
            Lista de entradas do histórico de pesquisa
        """
        if not self.perplexity:
            return []
            
        return self.perplexity.get_query_history()
    
    def clear_web_search_history(self) -> None:
        """Limpa o histórico de pesquisas na web."""
        if self.perplexity:
            self.perplexity.clear_history()
            self._log_quantum_operation(
                "HISTÓRICO_LIMPO", 
                "Histórico de pesquisas na web limpo"
            )
    
    def get_logs(self) -> List[Dict[str, str]]:
        """
        Retorna os logs das operações quânticas.
        
        Returns:
            Lista de entradas de log
        """
        return self.log_entries
    
    def clear_logs(self) -> None:
        """Limpa os logs das operações quânticas."""
        self.log_entries = []
    
    def _log_quantum_operation(self, operation: str, details: str, context: Optional[str] = None) -> None:
        """
        Gera um log no formato padrão EVA & GUARANI.
        
        Args:
            operation: Tipo de operação sendo realizada
            details: Detalhes da operação
            context: Contexto adicional (opcional)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "operation": operation,
            "details": details
        }
        
        if context:
            log_entry["context"] = context
            
        self.log_entries.append(log_entry)
        
        # Formatação para exibição
        log_text = f"[{timestamp}][QUANTUM_TOOLS][{operation}]"
        if context:
            log_text += f"\nCONTEXTO: {context}"
        log_text += f"\nDETALHES: {details}"
        
        # Em produção, este log seria direcionado para um sistema de log apropriado
        print(log_text)


# Exemplo de uso:
if __name__ == "__main__":
    # Inicializar as ferramentas quânticas
    tools = QuantumTools()
    
    # Verificar se o módulo PERPLEXITY está disponível
    if tools.perplexity:
        print("\nPERPLEXITY disponível. Realizando pesquisa de teste...")
        
        # Realizar uma pesquisa de teste
        results = tools.search_web(
            "Qual é o estado atual da tecnologia de fusão nuclear em 2024?",
            validation_level="strict"
        )
        
        if results["status"] == "success":
            print("\n✅ Pesquisa realizada com sucesso!")
            print("\nResultado (prévia):")
            content = str(results["conteúdo"])
            preview = content[:200] + "..." if len(content) > 200 else content
            print(preview)
            
            print("\nFontes principais:")
            for source in results["fontes"][:3]:
                print(f"- {source['título']} ({source['confiabilidade']:.2f})")
        else:
            print(f"\n❌ Falha na pesquisa: {results.get('error_message', 'Erro desconhecido')}")
            
        # Exibir histórico de pesquisas
        history = tools.get_web_search_history()
        print(f"\nHistórico: {len(history)} pesquisa(s) realizada(s)")
    else:
        print("\nO módulo PERPLEXITY não está disponível.")
        print("Execute o script setup_perplexity.py para configurar.")
        
    # Exibir logs
    print("\nLogs de operações:")
    for log in tools.get_logs():
        print(f"[{log['timestamp']}] {log['operation']}: {log['details']}")
        
    print("\n✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧") 