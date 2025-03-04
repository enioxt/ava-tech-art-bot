"""
Serviço de integração com a API da Perplexity para pesquisas na web.

Este módulo fornece uma interface para realizar pesquisas na web usando a API da Perplexity,
com verificações éticas e validação de resultados. Implementa estratégia de fallback
entre modelos disponíveis.
"""

import os
import re
import json
import logging
import datetime
from typing import Dict, List, Tuple, Any, Optional, cast, Iterable

try:
    from openai import OpenAI
    from openai.types.chat import ChatCompletion
    from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
except ImportError:
    raise ImportError("A biblioteca 'openai' não está instalada. Execute 'pip install openai' para instalá-la.")

# Importar configuração da Perplexity
try:
    import perplexity_config
    HAS_CONFIG_FILE = True
except ImportError:
    HAS_CONFIG_FILE = False
    logging.warning("O arquivo perplexity_config.py não foi encontrado. Usando configurações padrão.")

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PerplexityService")

# Modelos padrão caso a configuração não esteja disponível
DEFAULT_MODELS = [
    "sonar",                # Modelo básico mais rápido (2.17s)
    "sonar-pro",            # Modelo avançado (3.64s)
    "sonar-reasoning",      # Modelo com capacidade de raciocínio (2.31s)
    "sonar-reasoning-pro",  # Modelo avançado com capacidade de raciocínio (2.73s)
    "r1-1776",              # Modelo de raciocínio alternativo (3.67s)
    "sonar-deep-research"   # Modelo para pesquisas profundas, mais lento (41.05s)
]

# Mock do ConfigManager para casos onde não está disponível
class ConfigManagerMock:
    """Mock do ConfigManager para casos onde o ConfigManager real não está disponível."""
    
    def get_key(self, service_name: str) -> Optional[str]:
        """Obtém uma chave de API para o serviço especificado."""
        if service_name.lower() == "perplexity":
            return os.environ.get("PERPLEXITY_API_KEY")
        return None
    
    def set_key(self, service_name: str, key: str) -> None:
        """Define uma chave de API para o serviço especificado."""
        pass
    
    def is_configured(self, service_name: str) -> bool:
        """Verifica se um serviço está configurado."""
        return self.get_key(service_name) is not None

class PerplexityService:
    """
    Serviço para interagir com a API da Perplexity, realizando buscas na web
    e processando os resultados.
    
    Este serviço utiliza a API Perplexity via cliente OpenAI para realizar pesquisas
    na web com verificação ética e análise de fontes.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o serviço Perplexity.
        
        A chave API pode ser fornecida diretamente ou obtida das seguintes fontes 
        (em ordem de prioridade):
        1. Arquivo perplexity_config.py
        2. ConfigManager
        3. Variável de ambiente PERPLEXITY_API_KEY
        
        Args:
            api_key: Chave API da Perplexity (opcional)
        """
        self.api_key = api_key
        
        # Se a chave não foi fornecida, tenta obter de outras fontes
        if not self.api_key:
            # 1. Tentar obter do arquivo de configuração
            if HAS_CONFIG_FILE and hasattr(perplexity_config, 'get_api_key'):
                self.api_key = perplexity_config.get_api_key()
                if self.api_key:
                    logger.info("Chave API da Perplexity obtida do arquivo perplexity_config.py")
            
            # 2. Tentar obter do ConfigManager
            if not self.api_key:
                try:
                    from config_manager import ConfigManager
                    manager = ConfigManager()
                    self.api_key = manager.get_key("perplexity")
                    if self.api_key:
                        logger.info("Chave API da Perplexity obtida do ConfigManager")
                except ImportError:
                    manager = ConfigManagerMock()
                    self.api_key = manager.get_key("perplexity")
                    if self.api_key:
                        logger.info("Chave API da Perplexity obtida da variável de ambiente")
        
        # Inicializar o cliente OpenAI com a API da Perplexity
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.perplexity.ai",
                default_headers={"Authorization": f"Bearer {self.api_key}"}
            )
            logger.info("Cliente OpenAI para Perplexity inicializado com sucesso")
        else:
            self.client = None
            logger.warning("Cliente OpenAI para Perplexity NÃO inicializado - chave API não encontrada")
    
    def search(self, query: str, validate_level: str = "normal", model: Optional[str] = None) -> Dict[str, Any]:
        """
        Realiza uma pesquisa web usando a API da Perplexity.
        
        Se um modelo específico não funcionar ou não estiver disponível, 
        tentará outros modelos em ordem de preferência.
        
        Args:
            query: A consulta de pesquisa
            validate_level: Nível de validação de resultados ("minimal", "normal", "strict")
            model: Modelo da Perplexity a ser usado (opcional, usa "sonar" como padrão)
        
        Returns:
            Dicionário com resultados da pesquisa e metadados
            
        Raises:
            RuntimeError: Se a chave API não estiver configurada ou outros erros
        """
        if not self.client:
            raise RuntimeError("Serviço Perplexity não inicializado. Verifique se a chave API está configurada.")
        
        # Verificação ética antes da consulta
        if not self._check_query_ethics(query, validate_level):
            return {
                "error": "Consulta rejeitada por questões éticas",
                "query": query,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        try:
            # Se nenhum modelo foi especificado, tenta a estratégia de fallback
            if not model:
                return self._try_models_in_order(query, validate_level)
            
            # Se um modelo específico foi solicitado, usa esse modelo
            return self._execute_search(query, validate_level, model)
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"Erro ao realizar pesquisa: {error_type}: {error_msg}")
            
            # Tratamento específico para erros de autenticação
            if "401" in error_msg:
                raise RuntimeError(f"Erro de autenticação: A chave API da Perplexity é inválida ou expirou. {error_msg}")
            
            # Se for erro de modelo não encontrado e um modelo específico foi solicitado,
            # tenta a estratégia de fallback
            if ("404" in error_msg or "model_not_found" in error_msg.lower()) and model:
                logger.warning(f"Modelo {model} não disponível. Tentando outros modelos...")
                return self._try_models_in_order(query, validate_level)
            
            # Para outros erros, propaga a exceção
            raise RuntimeError(f"Erro ao processar consulta: {error_type}: {error_msg}")
    
    def _try_models_in_order(self, query: str, validate_level: str) -> Dict[str, Any]:
        """
        Tenta executar a pesquisa com diferentes modelos em ordem até que um tenha sucesso.
        
        Args:
            query: A consulta de pesquisa
            validate_level: Nível de validação de resultados
            
        Returns:
            Dicionário com resultados da pesquisa e metadados
            
        Raises:
            RuntimeError: Se todos os modelos falharem
        """
        # Determinar quais modelos tentar
        models_to_try = (
            perplexity_config.AVAILABLE_MODELS 
            if HAS_CONFIG_FILE and hasattr(perplexity_config, 'AVAILABLE_MODELS')
            else DEFAULT_MODELS
        )
        
        logger.info(f"Tentando pesquisa com cascata de modelos: {', '.join(models_to_try)}")
        
        # Armazenar erros para diagnóstico
        errors = {}
        
        for model in models_to_try:
            try:
                logger.info(f"Tentando pesquisa com o modelo: {model}")
                result = self._execute_search(query, validate_level, model)
                logger.info(f"Pesquisa bem-sucedida com o modelo: {model}")
                # Adicionar informação sobre o modelo usado
                result["model_used"] = model
                return result
                
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                errors[model] = f"{error_type}: {error_msg}"
                logger.warning(f"Falha com modelo {model}: {error_type}: {error_msg}")
                
                # Se for erro de autenticação, não adianta tentar outros modelos
                if "401" in error_msg:
                    raise RuntimeError(f"Erro de autenticação: A chave API da Perplexity é inválida ou expirou.")
                
                # Se for limite de taxa, pode ser temporário
                if "429" in error_msg:
                    logger.warning(f"Limite de taxa atingido para o modelo {model}. Tentando próximo modelo...")
                    continue
                
                # Se for modelo não disponível, tenta o próximo
                if "404" in error_msg or "model_not_found" in error_msg.lower():
                    logger.warning(f"Modelo {model} não disponível para esta conta. Tentando próximo...")
                    continue
                
                # Para outros erros, tenta o próximo modelo
                logger.warning(f"Erro desconhecido com o modelo {model}. Tentando próximo modelo...")
        
        # Se chegou aqui, todos os modelos falharam
        error_details = "\n".join([f"{model}: {error}" for model, error in errors.items()])
        raise RuntimeError(f"Todos os modelos da Perplexity falharam. Detalhes:\n{error_details}")
    
    def _execute_search(self, query: str, validate_level: str, model: str) -> Dict[str, Any]:
        """
        Executa uma pesquisa com um modelo específico.
        
        Args:
            query: A consulta de pesquisa
            validate_level: Nível de validação de resultados
            model: Modelo a ser usado
            
        Returns:
            Dicionário com resultados da pesquisa e metadados
        """
        inicio = datetime.datetime.now()
        
        # Preparar mensagens para a API
        messages = [
            {"role": "system", "content": (
                "Você é um assistente de pesquisa que gera respostas baseadas em fontes verificáveis. "
                "Forneça respostas detalhadas e precisas para as consultas, sempre citando suas fontes. "
                "Use marcação [número] para citar fontes inline e liste todas as fontes ao final. "
                "Prefira fontes atualizadas e confiáveis. "
                "Seja objetivo, imparcial e forneça informações completas."
            )},
            {"role": "user", "content": query}
        ]
        
        # Realizar a chamada à API
        logger.info(f"Enviando consulta para API Perplexity usando modelo {model}: '{query}'")
        response = self.client.chat.completions.create(
            model=model,
            messages=cast(List[ChatCompletionMessageParam], messages),
            temperature=0.7,
            max_tokens=1500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        # Processar a resposta
        raw_response = json.loads(response.model_dump_json())
        if not response.choices or len(response.choices) == 0:
            raise RuntimeError("Resposta vazia da API da Perplexity")
        
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Conteúdo vazio na resposta da Perplexity")
            
        # Extrair citações e fontes
        safe_content = content if content is not None else ""
        sources = self._extract_sources(safe_content, raw_response)
        
        # Validar resultados
        validation = self._validate_results(safe_content, sources, validate_level)
        
        # Calcular tempo de resposta
        fim = datetime.datetime.now()
        tempo_resposta = (fim - inicio).total_seconds()
        
        # Construir resposta final
        result = {
            "content": safe_content,
            "sources": sources,
            "validation": validation,
            "query": query,
            "model": model,
            "response_time": round(tempo_resposta, 2),
            "timestamp": datetime.datetime.now().isoformat(),
            "raw_response": raw_response if validate_level == "debug" else None
        }
        
        logger.info(f"Pesquisa concluída em {tempo_resposta:.2f}s usando o modelo {model}")
        return result
    
    def _check_query_ethics(self, query: str, validate_level: str) -> bool:
        """
        Verifica se a consulta é ética e apropriada para pesquisa.
        
        Args:
            query: A consulta a ser verificada
            validate_level: Nível de validação/restrição
            
        Returns:
            True se a consulta for ética, False caso contrário
        """
        if not query or query.strip() == "":
            logger.warning("Consulta vazia rejeitada")
            return False
            
        # Lista de termos proibidos (simplificada - implementar verificação mais robusta em produção)
        forbidden_terms = [
            "como fabricar bomba",
            "como invadir",
            "como hackear",
            "pornografia infantil",
            "como produzir drogas",
            "como enganar",
            "como fraudar"
        ]
        
        # Verificação básica (para demonstração)
        query_lower = query.lower()
        for term in forbidden_terms:
            if term in query_lower:
                logger.warning(f"Consulta rejeitada por conter termo proibido: '{term}'")
                return False
                
        # Em produção, considerar implementar verificação mais robusta com
        # classificadores de conteúdo ou APIs específicas para isso
        
        return True
    
    def _validate_results(self, content: Optional[str], sources: List[Dict], validate_level: str) -> Dict[str, Any]:
        """
        Valida os resultados retornados e calcula métricas de qualidade.
        
        Args:
            content: O conteúdo textual da resposta
            sources: Lista de fontes citadas
            validate_level: Nível de validação ("minimal", "normal", "strict")
            
        Returns:
            Dicionário com métricas e flags de validação
        """
        safe_content = content if content is not None else ""
        
        # Valores padrão
        validation = {
            "has_sources": len(sources) > 0,
            "source_count": len(sources),
            "source_consistency": 0.0,
            "potential_biases": [],
            "confidence_score": 0.0,
            "validation_level": validate_level,
            "validation_passed": True
        }
        
        # Se nível de validação for minimal, retorna validação básica
        if validate_level == "minimal":
            validation["validation_passed"] = validation["has_sources"]
            return validation
            
        # Análises adicionais para níveis normal e strict
        if validate_level in ["normal", "strict"]:
            # Verificar consistência entre fontes
            validation["source_consistency"] = self._check_source_consistency(sources)
            
            # Identificar potenciais vieses
            validation["potential_biases"] = self._identify_potential_biases(safe_content)
            
            # Calcular pontuação de confiança
            validation["confidence_score"] = self._estimate_confidence(sources)
            
            # Determinar se passou na validação
            if validate_level == "normal":
                # No nível normal, exige pelo menos uma fonte e confiança mínima
                validation["validation_passed"] = (
                    validation["has_sources"] and 
                    validation["confidence_score"] >= 0.3
                )
            else:  # strict
                # No nível estrito, exige mais fontes e maior confiança
                validation["validation_passed"] = (
                    validation["has_sources"] and
                    validation["source_count"] >= 2 and
                    validation["confidence_score"] >= 0.6 and
                    validation["source_consistency"] >= 0.5
                )
                
        return validation
    
    def _estimate_source_reliability(self, url: str) -> float:
        """
        Estima a confiabilidade de uma fonte com base no URL.
        
        Args:
            url: URL da fonte
            
        Returns:
            Pontuação de confiabilidade entre 0.0 e 1.0
        """
        # Lista de domínios de alta confiabilidade
        high_reliability_domains = [
            "wikipedia.org",
            "gov",
            "edu",
            "britannica.com",
            "nature.com",
            "scholar.google.com",
            "sciencedirect.com",
            "nih.gov",
            "who.int",
            "bbc.com",
            "nytimes.com",
            "washingtonpost.com",
            "reuters.com",
            "bloomberg.com",
            "ft.com"
        ]
        
        # Lista de domínios de média confiabilidade
        medium_reliability_domains = [
            "medium.com",
            "github.com",
            "stackoverflow.com",
            "cnn.com",
            "theguardian.com",
            "forbes.com",
            "time.com",
            "economist.com",
            "nationalgeographic.com"
        ]
        
        # Verificar domínio
        for domain in high_reliability_domains:
            if domain in url:
                return 0.9
                
        for domain in medium_reliability_domains:
            if domain in url:
                return 0.7
                
        # Para outros domínios, atribui confiabilidade moderada
        return 0.5
    
    def _extract_sources(self, content: str, raw_response: Dict) -> List[Dict]:
        """
        Extrai informações sobre as fontes citadas no conteúdo.
        
        Args:
            content: O conteúdo textual da resposta
            raw_response: Resposta bruta da API
            
        Returns:
            Lista de fontes citadas com metadados
        """
        safe_content = content if content is not None else ""
        
        # Extrair URLs mencionados
        urls = re.findall(r'(https?://[^\s\)]+)', safe_content)
        
        # Extrair números de referência no formato [1], [2], etc.
        ref_numbers = re.findall(r'\[(\d+)\]', safe_content)
        
        # Padrão para extrair fontes listadas ao final do texto
        # Exemplo: "[1] BBC News: https://www.bbc.com/news/article123"
        source_pattern = r'\[(\d+)\]\s+([^:]+):\s+(https?://[^\s]+)'
        listed_sources = re.findall(source_pattern, safe_content)
        
        # Consolidar fontes encontradas
        sources = []
        source_ids = set()
        
        # Adicionar fontes listadas explicitamente
        for ref_num, title, url in listed_sources:
            if ref_num not in source_ids:
                sources.append({
                    "id": ref_num,
                    "title": title.strip(),
                    "url": url.strip(),
                    "reliability": self._estimate_source_reliability(url),
                    "extracted_method": "explicit_listing"
                })
                source_ids.add(ref_num)
        
        # Adicionar outras URLs encontradas no texto
        for url in urls:
            # Verificar se esta URL já está em alguma fonte
            url_exists = any(s["url"] == url for s in sources)
            
            if not url_exists:
                # Gerar ID para a fonte
                source_id = str(len(sources) + 1)
                
                # Extrair título básico do URL
                domain = url.split("//")[-1].split("/")[0]
                title = f"Source from {domain}"
                
                sources.append({
                    "id": source_id,
                    "title": title,
                    "url": url,
                    "reliability": self._estimate_source_reliability(url),
                    "extracted_method": "url_extraction"
                })
        
        return sources
    
    def _identify_potential_biases(self, content: Optional[str]) -> List[str]:
        """
        Identifica potenciais vieses no conteúdo da resposta.
        
        Args:
            content: O conteúdo textual da resposta
            
        Returns:
            Lista de potenciais vieses identificados
        """
        safe_content = content if content is not None else ""
        biases = []
        
        # Palavras que podem indicar viés
        bias_indicators = {
            "certamente": "Expressão de certeza absoluta",
            "obviamente": "Pressupõe conhecimento universal",
            "claramente": "Pressupõe evidência inequívoca",
            "sem dúvida": "Afirmação sem qualificações",
            "sempre": "Generalização temporal absoluta",
            "nunca": "Negação absoluta",
            "todos": "Generalização universal",
            "ninguém": "Negação universal",
            "melhor": "Julgamento comparativo sem critérios",
            "pior": "Julgamento comparativo sem critérios",
            "devemos": "Prescrição normativa sem justificativa",
            "temos que": "Obrigação não justificada",
            "é importante": "Julgamento de valor não justificado"
        }
        
        # Verificar presença de indicadores de viés
        content_lower = safe_content.lower()
        for indicator, reason in bias_indicators.items():
            if indicator in content_lower:
                biases.append(f"{indicator}: {reason}")
        
        # Verificar equilíbrio entre pontos de vista
        if "por um lado" in content_lower and "por outro lado" not in content_lower:
            biases.append("Apresenta apenas um lado da questão")
            
        # Verificar se há qualificações
        if "contudo" not in content_lower and "entretanto" not in content_lower and "no entanto" not in content_lower:
            biases.append("Falta de qualificações ou nuances")
        
        return biases
    
    def _check_source_consistency(self, sources: List[Dict]) -> float:
        """
        Verifica a consistência entre as fontes citadas.
        
        Args:
            sources: Lista de fontes citadas
            
        Returns:
            Pontuação de consistência entre 0.0 e 1.0
        """
        if not sources or len(sources) <= 1:
            return 1.0  # Uma única fonte é consistente consigo mesma
            
        # Calcular a média de confiabilidade das fontes
        reliability_scores = [s.get("reliability", 0.5) for s in sources]
        avg_reliability = sum(reliability_scores) / len(reliability_scores)
        
        # Verificar variação na confiabilidade
        # Uma baixa variação indica maior consistência
        variance = sum((r - avg_reliability) ** 2 for r in reliability_scores) / len(reliability_scores)
        consistency_score = 1.0 - min(variance * 2, 0.5)  # Normalizar para 0.5-1.0
        
        return consistency_score
    
    def _estimate_confidence(self, sources: List[Dict]) -> float:
        """
        Estima a confiança geral nos resultados.
        
        Args:
            sources: Lista de fontes citadas
            
        Returns:
            Pontuação de confiança entre 0.0 e 1.0
        """
        # Se não há fontes, confiança é baixa
        if not sources:
            return 0.2
            
        # Confiança base depende do número de fontes (até 5)
        source_count_score = min(len(sources) / 5, 1.0) * 0.5
        
        # Confiança também depende da confiabilidade das fontes
        reliability_scores = [s.get("reliability", 0.5) for s in sources]
        avg_reliability = sum(reliability_scores) / len(reliability_scores)
        
        # Combinar os fatores
        confidence = source_count_score + (avg_reliability * 0.5)
        
        # Normalizar para 0.0-1.0
        return min(confidence, 1.0)
