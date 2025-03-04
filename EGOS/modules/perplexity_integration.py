"""
Módulo de Integração da Perplexity com EVA & GUARANI
----------------------------------------------------
Este módulo estabelece a conexão entre o sistema quântico EVA & GUARANI
e a API da Perplexity, permitindo pesquisas na internet com tratamento
ético das informações e validação de fontes.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Adicionar o diretório raiz ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
egos_dir = os.path.dirname(current_dir)
if egos_dir not in sys.path:
    sys.path.append(egos_dir)

# Importar serviços e configurações
from services.perplexity_service import PerplexityService
from services.config import config_manager

class PerplexityIntegration:
    """
    Integração entre o sistema EVA & GUARANI e a API da Perplexity.
    Fornece métodos para pesquisa na internet com validação ética.
    """
    
    def __init__(self):
        """Inicializa a integração com a Perplexity API."""
        self._ensure_api_configured()
        self.perplexity = PerplexityService()
        self.last_search_results = None
        self.query_history = []
        
    def _ensure_api_configured(self) -> None:
        """Verifica se a API da Perplexity está configurada."""
        if not config_manager.is_configured("perplexity"):
            raise ValueError(
                "API da Perplexity não configurada. Execute o script setup_perplexity.py "
                "ou defina a variável de ambiente PERPLEXITY_API_KEY."
            )
        
    def search(self, 
              query: str, 
              ethical_filter: bool = True, 
              validation_level: str = "standard",
              context: Optional[str] = None) -> Dict[str, Any]:
        """
        Realiza uma pesquisa na internet usando a API da Perplexity.
        
        Args:
            query: Consulta para pesquisa
            ethical_filter: Se deve aplicar filtros éticos (default: True)
            validation_level: Nível de validação ("basic", "standard", "strict")
            context: Contexto adicional da consulta para análise ética
            
        Returns:
            Resultados processados com metadados de validação
        """
        # Log quântico no formato EVA & GUARANI
        self._log_quantum_operation("PESQUISA_INTERNET", query, context)
        
        # Verificação adicional de ética baseada no contexto
        if context:
            ethics_assessment = self._assess_query_ethics(query, context)
            if not ethics_assessment["is_appropriate"]:
                return {
                    "status": "rejected",
                    "reason": ethics_assessment["reason"],
                    "timestamp": datetime.now().isoformat(),
                    "ethical_analysis": ethics_assessment["analysis"],
                    "alternative_suggestion": ethics_assessment.get("alternative")
                }
        
        # Registrar histórico
        self.query_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "context": context
        })
        
        # Realizar pesquisa via PerplexityService
        results = self.perplexity.search(
            query, 
            ethical_filter=ethical_filter,
            validation_level=validation_level
        )
        
        # Armazenar resultados para referência
        self.last_search_results = results
        
        # Processar resultados no formato EVA & GUARANI
        processed_results = self._process_for_quantum_system(results)
        
        # Log de conclusão
        if results.get("status") == "success":
            self._log_quantum_operation(
                "PESQUISA_CONCLUÍDA", 
                f"Consulta: {query[:30]}...", 
                f"Fontes: {len(results.get('sources', []))}"
            )
        else:
            self._log_quantum_operation(
                "PESQUISA_FALHOU", 
                f"Consulta: {query[:30]}...", 
                results.get("error_message", "Erro desconhecido")
            )
            
        return processed_results
    
    def _assess_query_ethics(self, query: str, context: str) -> Dict[str, Any]:
        """
        Realiza uma avaliação ética mais profunda da consulta com base no contexto.
        
        Args:
            query: Consulta a ser avaliada
            context: Contexto da consulta (ex: conversa anterior)
            
        Returns:
            Avaliação ética detalhada
        """
        # Esta é uma versão simplificada. Em produção, usaria um modelo de IA
        # mais sofisticado para análise ética contextual.
        
        query_lower = query.lower()
        context_lower = context.lower()
        
        # Detectar intenções maliciosas baseadas no contexto
        malicious_patterns = [
            ("hack", "invasão", "acessar conta"),
            ("burlar", "enganar", "fraudar"),
            ("pornografia", "material ilegal"),
            ("contornar segurança", "bypass")
        ]
        
        for pattern_set in malicious_patterns:
            query_matches = any(pattern in query_lower for pattern in pattern_set)
            context_matches = any(pattern in context_lower for pattern in pattern_set)
            
            if query_matches and context_matches:
                return {
                    "is_appropriate": False,
                    "reason": "A consulta, quando analisada em contexto, parece solicitar informações sobre atividades potencialmente antiéticas ou ilegais.",
                    "analysis": f"Padrões detectados tanto na consulta quanto no contexto: {pattern_set}",
                    "alternative": "Considere reformular sua consulta para focar em aspectos educativos ou de segurança defensive."
                }
        
        # Se não houver problemas
        return {
            "is_appropriate": True,
            "reason": "Consulta aprovada na verificação ética contextual",
            "analysis": "Nenhum padrão problemático detectado no contexto da consulta."
        }
    
    def _process_for_quantum_system(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa os resultados da pesquisa para o formato do sistema EVA & GUARANI.
        
        Args:
            results: Resultados brutos da pesquisa
            
        Returns:
            Resultados formatados para o sistema quântico
        """
        if results.get("status") != "success":
            return results
            
        # Preparar o resultado para o formato do EVA & GUARANI
        quantum_results = {
            "status": results["status"],
            "query": results["query"],
            "conteúdo": results["results"],
            "metadados": {
                "timestamp": datetime.now().isoformat(),
                "nível_validação": results.get("validation_metadata", {}).get("validation_level"),
                "score_confiança": results.get("validation_metadata", {}).get("confidence_score", 0.7),
                "aviso_sensibilidade": results.get("sensitive_topic_warning", None)
            },
            "fontes": [
                {
                    "título": source.get("title", "Não especificado"),
                    "url": source.get("url", ""),
                    "confiabilidade": self._estimate_source_reliability(source)
                }
                for source in results.get("sources", [])
            ],
            "potenciais_vieses": results.get("potential_biases", []),
            "nota_validação": results.get("validation_note", "")
        }
        
        return quantum_results
    
    def _estimate_source_reliability(self, source: Dict[str, Any]) -> float:
        """
        Estima a confiabilidade de uma fonte baseada em heurísticas.
        
        Args:
            source: Informações sobre a fonte
            
        Returns:
            Score de confiabilidade entre 0.0 e 1.0
        """
        # Implementação simplificada
        # Em produção, seria baseada em listas de fontes confiáveis,
        # verificação de domínio, etc.
        
        # Base score
        reliability = 0.7
        
        # Domínios acadêmicos e governamentais têm maior confiabilidade
        url = source.get("url", "").lower()
        if url:
            if url.endswith((".edu", ".gov", ".org")):
                reliability += 0.1
            elif "wikipedia.org" in url:
                reliability += 0.05
            elif any(domain in url for domain in ["news", "blog", "forum"]):
                reliability -= 0.1
                
        # Título muito sensacionalista pode indicar menor confiabilidade
        title = source.get("title", "").lower()
        sensational_terms = ["inacreditável", "chocante", "você não vai acreditar", 
                            "revelado", "segredo", "exclusivo", "surpreendente"]
        if any(term in title for term in sensational_terms):
            reliability -= 0.15
            
        return max(min(reliability, 1.0), 0.1)  # Limitar entre 0.1 e 1.0
    
    def _log_quantum_operation(self, operation: str, details: str, context: Optional[str] = None) -> None:
        """
        Gera um log no formato padrão EVA & GUARANI.
        
        Args:
            operation: Tipo de operação sendo realizada
            details: Detalhes da operação
            context: Contexto adicional (opcional)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}][ATLAS][PERPLEXITY][{operation}]"
        
        if context:
            log_entry += f"\nCONTEXTO: {context}"
            
        log_entry += f"\nDETALHES: {details}"
        
        # Recomendações para melhores resultados
        if operation == "PESQUISA":
            log_entry += "\nRECOMENDAÇÕES: Para melhores resultados, utilize consultas específicas e evite ambiguidades."
            
        # Reflexão ética para pesquisas
        log_entry += "\nREFLEXÃO ÉTICA: A informação da internet deve ser verificada em múltiplas fontes confiáveis."
        
        # Em produção, este log seria direcionado para um sistema de log apropriado
        print(log_entry)
        
    def get_query_history(self) -> List[Dict[str, str]]:
        """
        Retorna o histórico de consultas realizadas.
        
        Returns:
            Lista de consultas com timestamp e contexto
        """
        return self.query_history
        
    def clear_history(self) -> None:
        """Limpa o histórico de consultas."""
        self.query_history = []
        self.last_search_results = None


# Exemplo de uso:
if __name__ == "__main__":
    try:
        perplexity_integration = PerplexityIntegration()
        
        test_query = "Quais são as principais novidades tecnológicas de 2024?"
        print(f"\nRealizando consulta: '{test_query}'")
        
        results = perplexity_integration.search(test_query)
        
        if results["status"] == "success":
            print("\n✅ Consulta realizada com sucesso!")
            print(f"\nResultado (prévia):")
            
            content_preview = str(results["conteúdo"])[:300] + "..." if len(str(results["conteúdo"])) > 300 else str(results["conteúdo"])
            print(content_preview)
            
            print(f"\nFontes encontradas: {len(results['fontes'])}")
            for i, source in enumerate(results['fontes'][:3], 1):
                print(f"  {i}. {source['título']} (Confiabilidade: {source['confiabilidade']:.2f})")
                
            if len(results['fontes']) > 3:
                print(f"  ... e mais {len(results['fontes']) - 3} fontes")
                
            print(f"\nNível de validação: {results['metadados']['nível_validação']}")
            print(f"Score de confiança: {results['metadados']['score_confiança']:.2f}")
            
            if results['potenciais_vieses']:
                print("\nPotenciais vieses detectados:")
                for bias in results['potenciais_vieses']:
                    print(f"  - {bias}")
        else:
            print("\n❌ Falha na consulta:")
            print(results.get("reason", "Erro desconhecido"))
    
    except ValueError as e:
        print(f"\n❌ Erro de configuração: {str(e)}")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}") 