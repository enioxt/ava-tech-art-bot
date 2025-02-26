from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import re
from datetime import datetime
from .source_validator import SourceValidator, SourceType, SourceScore

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerplexityValidator:
    """
    Validador para respostas da API Perplexity.
    
    Esta classe é responsável por validar respostas de pesquisa,
    verificando sua confiabilidade, relevância e alinhamento ético.
    """
    
    def __init__(self, source_validator: SourceValidator):
        self.source_validator = source_validator
        self.perplexity_threshold = 50.0
        self.min_confidence_threshold = 0.6
        self.bias_keywords = self._load_bias_keywords()
        self.content_filters = self._load_content_filters()
        
    def _load_bias_keywords(self) -> Dict[str, float]:
        """Carrega palavras-chave que podem indicar viés na resposta."""
        try:
            with open("config/bias_keywords.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Palavras-chave padrão se o arquivo não existir
            return {
                "certamente": -0.1,
                "obviamente": -0.1,
                "claramente": -0.1,
                "sem dúvida": -0.1,
                "sempre": -0.2,
                "nunca": -0.2,
                "todos": -0.1,
                "ninguém": -0.1,
                "absolutamente": -0.2,
                "definitivamente": -0.1
            }
    
    def _load_content_filters(self) -> List[Dict[str, Any]]:
        """Carrega filtros de conteúdo para verificação ética."""
        try:
            with open("config/content_filters.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Filtros padrão se o arquivo não existir
            return [
                {
                    "name": "harmful_content",
                    "patterns": [
                        r"(?i)como\s+(?:fazer|criar|construir)\s+(?:armas|explosivos)",
                        r"(?i)como\s+(?:hackear|invadir)\s+(?:sistemas|contas)"
                    ],
                    "penalty": 0.5
                },
                {
                    "name": "misinformation",
                    "patterns": [
                        r"(?i)(?:cura|tratamento)\s+(?:milagroso|secreto)",
                        r"(?i)(?:teoria da conspiração|conspiração global)"
                    ],
                    "penalty": 0.3
                }
            ]
    
    async def validate_perplexity_response(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> float:
        """
        Valida uma resposta usando perplexidade e outras métricas.
        
        Args:
            text: O texto da resposta a ser validado
            metadata: Metadados associados à resposta
            
        Returns:
            Um score de confiança entre 0 e 1
        """
        # Validação da fonte
        source_score = self.source_validator.validate_source(text)
        
        # Verificar confiança nos metadados
        confidence = metadata.get('confidence', 0.5)
        
        # Verificar fontes citadas
        sources_score = self._validate_sources(metadata.get('sources', []))
        
        # Verificar viés no texto
        bias_score = self._check_bias(text)
        
        # Verificar conteúdo ético
        ethics_score = self._check_ethical_content(text)
        
        # Verificar atualidade da informação
        freshness_score = self._check_freshness(metadata)
        
        # Calcular score final ponderado
        weights = {
            'source': 0.25,
            'confidence': 0.2,
            'sources': 0.2,
            'bias': 0.15,
            'ethics': 0.15,
            'freshness': 0.05
        }
        
        # Ajustar pesos para conteúdo prejudicial e desinformação
        if ethics_score < 0.5:  # Se o conteúdo for potencialmente prejudicial
            weights['ethics'] = 0.3  # Aumentar o peso da ética
            weights['source'] = 0.15  # Reduzir outros pesos
            weights['confidence'] = 0.15
            weights['sources'] = 0.15
            weights['bias'] = 0.15
            weights['freshness'] = 0.1
        
        # Verificar se contém informações desatualizadas sobre política ou eventos atuais
        if self._contains_outdated_info(text, metadata):
            weights['freshness'] = 0.3  # Aumentar o peso da atualidade
            weights['source'] = 0.2
            weights['confidence'] = 0.15
            weights['sources'] = 0.15
            weights['bias'] = 0.1
            weights['ethics'] = 0.1
            
            # Reduzir o score de atualidade
            freshness_score = freshness_score * 0.5
        
        final_score = (
            source_score * weights['source'] +
            confidence * weights['confidence'] +
            sources_score * weights['sources'] +
            bias_score * weights['bias'] +
            ethics_score * weights['ethics'] +
            freshness_score * weights['freshness']
        )
        
        # Registrar resultado da validação
        self._log_validation_result(text, metadata, final_score)
        
        return final_score
    
    def _contains_outdated_info(self, text: str, metadata: Dict[str, Any]) -> bool:
        """Verifica se o texto contém informações potencialmente desatualizadas."""
        # Verificar menções a presidentes, governantes ou eventos atuais
        current_events_pattern = r"(?i)(?:atual|presente|corrente)\s+(?:presidente|governador|prefeito|ministro|primeiro-ministro)"
        
        # Verificar menções específicas a figuras políticas que podem mudar
        political_figures_pattern = r"(?i)(?:bolsonaro|lula|biden|trump|macron|putin|xi jinping)"
        
        # Verificar menções a eventos recentes
        recent_events_pattern = r"(?i)(?:pandemia|covid-19|copa do mundo|olimpíadas|eleições)"
        
        # Verificar se há menções a datas recentes
        date_pattern = r"(?i)(?:202[0-4]|atual|recente|recentemente|nos últimos anos|este ano)"
        
        # Verificar se o texto contém algum desses padrões
        contains_time_sensitive_info = (
            re.search(current_events_pattern, text) is not None or
            re.search(political_figures_pattern, text) is not None or
            re.search(recent_events_pattern, text) is not None or
            re.search(date_pattern, text) is not None
        )
        
        if not contains_time_sensitive_info:
            return False
            
        # Verificar a data das fontes
        sources = metadata.get('sources', [])
        if not sources:
            # Se não há fontes mas contém informações sensíveis ao tempo, considerar potencialmente desatualizado
            return True
            
        # Verificar a data mais recente das fontes
        current_date = datetime.now()
        most_recent_date = None
        
        for source in sources:
            date_str = source.get('date', '')
            if not date_str:
                continue
                
            try:
                # Tentar converter a data da fonte para datetime
                source_date = datetime.fromisoformat(date_str) if '-' in date_str else datetime.strptime(date_str, "%Y/%m/%d")
                
                if most_recent_date is None or source_date > most_recent_date:
                    most_recent_date = source_date
            except (ValueError, TypeError):
                continue
        
        # Se não conseguiu extrair nenhuma data válida, considerar potencialmente desatualizado
        if most_recent_date is None:
            return True
            
        # Verificar se a fonte mais recente tem mais de 1 ano
        days_diff = (current_date - most_recent_date).days
        return days_diff > 365
    
    def _validate_sources(self, sources: List[Dict[str, Any]]) -> float:
        """Valida as fontes citadas na resposta."""
        if not sources:
            return 0.5  # Score neutro se não houver fontes
        
        total_score = 0.0
        
        for source in sources:
            # Verificar se a fonte tem URL
            has_url = bool(source.get('url', ''))
            
            # Verificar se a fonte tem título
            has_title = bool(source.get('title', ''))
            
            # Verificar se a fonte tem data
            has_date = bool(source.get('date', ''))
            
            # Calcular score para esta fonte
            source_quality = 0.5  # Base neutra
            
            if has_url:
                source_quality += 0.2
                
                # Verificar domínios confiáveis
                url = source.get('url', '').lower()
                if any(domain in url for domain in ['.gov', '.edu', '.org']):
                    source_quality += 0.1
                elif any(domain in url for domain in ['.com', '.net']):
                    source_quality += 0.05
                
                # Penalizar domínios potencialmente não confiáveis
                if any(domain in url for domain in ['blog.', 'milagr', 'secreto', 'alternativ', 'conspira']):
                    source_quality -= 0.2
            
            if has_title:
                source_quality += 0.1
                
                # Verificar palavras-chave no título que podem indicar baixa confiabilidade
                title = source.get('title', '').lower()
                if any(keyword in title for keyword in ['milagr', 'secreto', 'alternativ', 'conspira', 'revelado', 'oculto']):
                    source_quality -= 0.2
                
            if has_date:
                source_quality += 0.1
                
                # Verificar atualidade da fonte
                try:
                    date_str = source.get('date', '')
                    if date_str:
                        source_date = datetime.fromisoformat(date_str) if '-' in date_str else datetime.strptime(date_str, "%Y/%m/%d")
                        days_diff = (datetime.now() - source_date).days
                        
                        if days_diff > 1095:  # Mais de 3 anos
                            source_quality -= 0.1
                except (ValueError, TypeError):
                    pass
            
            total_score += source_quality
        
        # Média das pontuações das fontes
        return min(1.0, total_score / len(sources))
    
    def _check_bias(self, text: str) -> float:
        """Verifica o nível de viés no texto."""
        base_score = 1.0  # Começa com pontuação máxima
        
        # Verificar palavras-chave de viés
        text_lower = text.lower()
        for keyword, penalty in self.bias_keywords.items():
            if keyword in text_lower:
                base_score += penalty
                
        # Verificar uso excessivo de linguagem absoluta
        absolute_pattern = r'\b(sempre|nunca|todos|ninguém|absolutamente|completamente)\b'
        absolute_matches = len(re.findall(absolute_pattern, text_lower))
        
        if absolute_matches > 0:
            # Penalidade baseada no número de ocorrências
            base_score -= min(0.3, absolute_matches * 0.05)
        
        # Verificar equilíbrio de perspectivas
        has_multiple_perspectives = any(phrase in text_lower for phrase in [
            "por outro lado", "em contrapartida", "alternativamente",
            "no entanto", "contudo", "diferentes perspectivas"
        ])
        
        if has_multiple_perspectives:
            base_score += 0.1
            
        return max(0.0, min(1.0, base_score))
    
    def _check_ethical_content(self, text: str) -> float:
        """Verifica se o conteúdo é ético e seguro."""
        base_score = 1.0  # Começa com pontuação máxima
        
        # Aplicar filtros de conteúdo
        for content_filter in self.content_filters:
            for pattern in content_filter.get('patterns', []):
                if re.search(pattern, text):
                    penalty = content_filter.get('penalty', 0.1)
                    base_score -= penalty
                    logger.warning(f"Filtro de conteúdo acionado: {content_filter['name']}")
                    
                    # Se o filtro tiver ação de rejeição, aplicar penalidade maior
                    if content_filter.get('action') == 'reject':
                        base_score -= 0.3  # Penalidade adicional para conteúdo que deve ser rejeitado
                    
                    break  # Sai do loop de padrões após encontrar uma correspondência
        
        # Verificar disclaimers e avisos
        has_disclaimer = any(phrase in text.lower() for phrase in [
            "importante consultar", "consulte um profissional",
            "não constitui aconselhamento", "não substitui"
        ])
        
        if has_disclaimer:
            base_score += 0.1
            
        # Verificar menções a tratamentos milagrosos ou curas secretas
        miracle_pattern = r"(?i)(?:tratamento|cura)\s+(?:milagroso|secreto|revolucionário|incrível|inacreditável)"
        if re.search(miracle_pattern, text):
            base_score -= 0.3  # Penalidade maior para alegações milagrosas
            
        # Verificar instruções para atividades potencialmente perigosas
        dangerous_pattern = r"(?i)(?:como|instruções|passos|tutorial)\s+(?:fazer|criar|construir|hackear|invadir)"
        if re.search(dangerous_pattern, text):
            base_score -= 0.2  # Penalidade para instruções potencialmente perigosas
            
        return max(0.0, min(1.0, base_score))
    
    def _check_freshness(self, metadata: Dict[str, Any]) -> float:
        """Verifica a atualidade da informação."""
        # Verificar se há timestamp nos metadados
        if 'timestamp' not in metadata:
            return 0.5  # Score neutro se não houver informação de data
            
        try:
            # Converter timestamp para datetime
            timestamp = datetime.fromisoformat(metadata['timestamp'].replace('Z', '+00:00'))
            
            # Calcular diferença em dias
            days_diff = (datetime.now() - timestamp).days
            
            # Pontuação baseada na idade da informação
            if days_diff <= 1:  # Informação de hoje ou ontem
                return 1.0
            elif days_diff <= 7:  # Última semana
                return 0.9
            elif days_diff <= 30:  # Último mês
                return 0.8
            elif days_diff <= 180:  # Últimos 6 meses
                return 0.7
            elif days_diff <= 365:  # Último ano
                return 0.6
            else:  # Mais de um ano
                return 0.5
        except (ValueError, TypeError):
            return 0.5  # Score neutro em caso de erro
    
    def _log_validation_result(self, text: str, metadata: Dict[str, Any], score: float) -> None:
        """Registra o resultado da validação para análise posterior."""
        try:
            # Criar resumo do texto para o log
            text_summary = text[:100] + "..." if len(text) > 100 else text
            
            # Registrar resultado
            logger.info(f"Validação de resposta: score={score:.2f}, texto='{text_summary}'")
            
            # Registrar detalhes em nível de debug
            logger.debug(f"Metadados da validação: {json.dumps(metadata)}")
            
            # Registrar em arquivo de log específico se o score for baixo
            if score < self.min_confidence_threshold:
                logger.warning(f"Resposta com baixa confiança detectada: {score:.2f}")
                
                # Aqui poderia salvar em um arquivo específico para análise posterior
        except Exception as e:
            logger.error(f"Erro ao registrar validação: {e}")
    
    async def analyze_search_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Analisa resultados de pesquisa e retorna os resultados filtrados e estatísticas.
        
        Args:
            query: A consulta de pesquisa original
            results: Lista de resultados da pesquisa
            
        Returns:
            Tupla contendo resultados filtrados e estatísticas da análise
        """
        if not results:
            return [], {"status": "error", "message": "Nenhum resultado encontrado"}
        
        filtered_results = []
        total_score = 0.0
        rejected_count = 0
        
        for result in results:
            # Extrair texto e metadados
            text = result.get('text', '')
            metadata = result.get('metadata', {})
            
            # Adicionar consulta aos metadados para contexto
            metadata['query'] = query
            
            # Validar resultado
            score = await self.validate_perplexity_response(text, metadata)
            
            # Adicionar score ao resultado
            result['validation_score'] = score
            
            # Filtrar resultados com base no score
            if score >= self.min_confidence_threshold:
                filtered_results.append(result)
                total_score += score
            else:
                rejected_count += 1
                logger.info(f"Resultado rejeitado (score={score:.2f}): {text[:50]}...")
        
        # Calcular estatísticas
        stats = {
            "total_results": len(results),
            "filtered_results": len(filtered_results),
            "rejected_results": rejected_count,
            "average_score": total_score / len(filtered_results) if filtered_results else 0,
            "query": query
        }
        
        return filtered_results, stats