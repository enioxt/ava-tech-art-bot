from typing import Dict, List, Optional, Union
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EthicsModule:
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o módulo de ética.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração.
        """
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.decision_cache = {}
        self.last_cache_cleanup = datetime.now()
        self.principles = {
            'beneficence': 0.9,        # Fazer o bem
            'non_maleficence': 0.95,   # Não causar dano
            'autonomy': 0.85,          # Respeitar autonomia
            'justice': 0.9,            # Ser justo
            'privacy': 0.95            # Proteger privacidade
        }
        
        self.ethical_framework = {
            'rules': self._load_ethical_rules(),
            'guidelines': self._load_ethical_guidelines(),
            'boundaries': self._load_ethical_boundaries()
        }
        
        self.violation_history = []
        logger.info("EthicsModule initialized successfully")
    
    def _load_config(self, config_path: Optional[str]) -> dict:
        """
        Carrega a configuração do sistema.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração.
            
        Returns:
            dict: Configuração carregada
        """
        default_config = {
            'ethics': {
                'min_ethical_score': 0.7,
                'critical_violation_threshold': 0.3,
                'warning_threshold': 0.8,
                'review_threshold': 0.6
            },
            'principles': {
                'beneficence_weight': 0.2,
                'non_maleficence_weight': 0.25,
                'autonomy_weight': 0.2,
                'justice_weight': 0.15,
                'privacy_weight': 0.2
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                return default_config
        return default_config
    
    @lru_cache(maxsize=1000)
    def _calculate_ethical_score_cached(self, action_hash: str) -> float:
        """Versão em cache do cálculo de score ético."""
        # Implementação do cálculo
        return 0.9
        
    async def evaluate_action(self, action: Dict) -> Dict:
        """Avalia uma ação de forma paralela e otimizada."""
        try:
            # Gera hash da ação para cache
            action_hash = str(hash(frozenset(action.items())))
            
            # Verifica cache
            if action_hash in self.decision_cache:
                self.logger.info("Using cached ethical decision")
                return self.decision_cache[action_hash]
            
            # Executa avaliações em paralelo
            tasks = [
                self._evaluate_parallel('beneficence', action),
                self._evaluate_parallel('non_maleficence', action),
                self._evaluate_parallel('autonomy', action),
                self._evaluate_parallel('justice', action),
                self._evaluate_parallel('privacy', action)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Combina resultados
            ethical_score = sum(results) / len(results)
            
            # Avalia compliance e impacto em paralelo
            compliance, impact = await asyncio.gather(
                self._check_compliance(action),
                self._assess_impact(action)
            )
            
            # Gera decisão final
            decision = await self._make_ethical_decision(
                ethical_score, compliance, impact
            )
            
            # Armazena no cache
            self.decision_cache[action_hash] = decision
            
            # Limpa cache se necessário
            await self._cleanup_cache()
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação ética: {str(e)}")
            raise
            
    async def _evaluate_parallel(self, principle: str, action: Dict) -> float:
        """Executa avaliação de princípio em thread separada."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            getattr(self, f'_evaluate_{principle}'),
            action
        )
        
    async def _cleanup_cache(self) -> None:
        """Limpa cache periodicamente."""
        if (datetime.now() - self.last_cache_cleanup).seconds > 3600:
            old_size = len(self.decision_cache)
            # Remove decisões antigas
            current_time = datetime.now()
            self.decision_cache = {
                k: v for k, v in self.decision_cache.items()
                if (current_time - v.get('timestamp', current_time)).seconds < 3600
            }
            self.last_cache_cleanup = current_time
            self.logger.info(f"Cache cleaned: {old_size} -> {len(self.decision_cache)}")
    
    async def _calculate_ethical_score(self, action: Dict) -> float:
        """
        Calcula o score ético de uma ação.
        
        Args:
            action (Dict): Ação para cálculo
            
        Returns:
            float: Score ético calculado
        """
        scores = {
            'beneficence': self._evaluate_beneficence(action),
            'non_maleficence': self._evaluate_non_maleficence(action),
            'autonomy': self._evaluate_autonomy(action),
            'justice': self._evaluate_justice(action),
            'privacy': self._evaluate_privacy(action)
        }
        
        weights = self.config['principles']
        
        weighted_score = sum(
            scores[principle] * weights[f'{principle}_weight']
            for principle in scores
        )
        
        return weighted_score
    
    async def _check_compliance(self, action: Dict) -> Dict:
        """
        Verifica a conformidade com regras éticas.
        
        Args:
            action (Dict): Ação para verificação
            
        Returns:
            Dict: Resultado da verificação
        """
        compliance = {
            'rules_violated': [],
            'guidelines_violated': [],
            'boundaries_crossed': [],
            'is_compliant': True
        }
        
        # Verifica regras
        for rule in self.ethical_framework['rules']:
            if not self._check_rule_compliance(action, rule):
                compliance['rules_violated'].append(rule)
                compliance['is_compliant'] = False
        
        # Verifica diretrizes
        for guideline in self.ethical_framework['guidelines']:
            if not self._check_guideline_compliance(action, guideline):
                compliance['guidelines_violated'].append(guideline)
        
        # Verifica limites
        for boundary in self.ethical_framework['boundaries'].values():
            if self._is_boundary_crossed(action, boundary):
                compliance['boundaries_crossed'].append(boundary)
                compliance['is_compliant'] = False
        
        return compliance
    
    async def _assess_impact(self, action: Dict) -> Dict:
        """
        Avalia o impacto ético de uma ação.
        
        Args:
            action (Dict): Ação para avaliação
            
        Returns:
            Dict: Avaliação de impacto
        """
        return {
            'immediate_impact': self._calculate_immediate_impact(action),
            'long_term_impact': self._calculate_long_term_impact(action),
            'affected_parties': self._identify_affected_parties(action),
            'risks': self._identify_risks(action),
            'benefits': self._identify_benefits(action)
        }
    
    async def _make_ethical_decision(
        self,
        ethical_score: float,
        compliance: Dict,
        impact: Dict
    ) -> Dict:
        """
        Toma uma decisão ética baseada na avaliação.
        
        Args:
            ethical_score (float): Score ético
            compliance (Dict): Resultado da verificação de conformidade
            impact (Dict): Avaliação de impacto
            
        Returns:
            Dict: Decisão ética
        """
        decision = {
            'ethical_score': ethical_score,
            'is_ethical': ethical_score >= self.config['ethics']['min_ethical_score'],
            'compliance': compliance,
            'impact': impact,
            'recommendation': self._generate_recommendation(
                ethical_score,
                compliance,
                impact
            ),
            'alternatives': self._suggest_alternatives(
                ethical_score,
                compliance,
                impact
            )
        }
        
        return decision
    
    def _evaluate_beneficence(self, action: Dict) -> float:
        """Avalia o princípio da beneficência."""
        # Implementação básica - pode ser expandida
        return 0.85
    
    def _evaluate_non_maleficence(self, action: Dict) -> float:
        """Avalia o princípio da não-maleficência."""
        # Implementação básica - pode ser expandida
        return 0.9
    
    def _evaluate_autonomy(self, action: Dict) -> float:
        """Avalia o princípio da autonomia."""
        # Implementação básica - pode ser expandida
        return 0.8
    
    def _evaluate_justice(self, action: Dict) -> float:
        """Avalia o princípio da justiça."""
        # Implementação básica - pode ser expandida
        return 0.85
    
    def _evaluate_privacy(self, action: Dict) -> float:
        """Avalia o princípio da privacidade."""
        # Implementação básica - pode ser expandida
        return 0.9
    
    def _load_ethical_rules(self) -> List[Dict]:
        """Carrega as regras éticas."""
        return [
            {
                'id': 'rule_001',
                'name': 'Proteção de Dados',
                'description': 'Proteger dados sensíveis dos usuários',
                'severity': 'high'
            },
            {
                'id': 'rule_002',
                'name': 'Consentimento',
                'description': 'Obter consentimento explícito',
                'severity': 'high'
            },
            {
                'id': 'rule_003',
                'name': 'Transparência',
                'description': 'Manter transparência nas ações',
                'severity': 'medium'
            }
        ]
    
    def _load_ethical_guidelines(self) -> List[Dict]:
        """Carrega as diretrizes éticas."""
        return [
            {
                'id': 'guide_001',
                'name': 'Minimização de Dano',
                'description': 'Minimizar potencial de dano',
                'priority': 'high'
            },
            {
                'id': 'guide_002',
                'name': 'Equidade',
                'description': 'Manter equidade nas decisões',
                'priority': 'medium'
            },
            {
                'id': 'guide_003',
                'name': 'Responsabilidade',
                'description': 'Assumir responsabilidade pelas ações',
                'priority': 'high'
            }
        ]
    
    def _load_ethical_boundaries(self) -> Dict:
        """Carrega os limites éticos."""
        return {
            'privacy': {
                'min_score': 0.8,
                'critical_threshold': 0.3
            },
            'safety': {
                'min_score': 0.85,
                'critical_threshold': 0.4
            },
            'fairness': {
                'min_score': 0.75,
                'critical_threshold': 0.3
            }
        }
    
    def _check_rule_compliance(self, action: Dict, rule: Dict) -> bool:
        """Verifica conformidade com uma regra."""
        # Implementação básica - pode ser expandida
        return True
    
    def _check_guideline_compliance(self, action: Dict, guideline: Dict) -> bool:
        """Verifica conformidade com uma diretriz."""
        # Implementação básica - pode ser expandida
        return True
    
    def _is_boundary_crossed(self, action: Dict, boundary: Dict) -> bool:
        """Verifica se um limite foi ultrapassado."""
        # Implementação básica - pode ser expandida
        return False
    
    def _calculate_immediate_impact(self, action: Dict) -> Dict:
        """Calcula o impacto imediato."""
        # Implementação básica - pode ser expandida
        return {
            'score': 0.8,
            'affected_areas': ['user_experience', 'data_privacy']
        }
    
    def _calculate_long_term_impact(self, action: Dict) -> Dict:
        """Calcula o impacto a longo prazo."""
        # Implementação básica - pode ser expandida
        return {
            'score': 0.75,
            'potential_risks': ['data_exposure', 'bias_development']
        }
    
    def _identify_affected_parties(self, action: Dict) -> List[str]:
        """Identifica partes afetadas."""
        # Implementação básica - pode ser expandida
        return ['users', 'system']
    
    def _identify_risks(self, action: Dict) -> List[Dict]:
        """Identifica riscos potenciais."""
        # Implementação básica - pode ser expandida
        return [
            {
                'type': 'privacy',
                'severity': 'medium',
                'probability': 0.3
            }
        ]
    
    def _identify_benefits(self, action: Dict) -> List[Dict]:
        """Identifica benefícios potenciais."""
        # Implementação básica - pode ser expandida
        return [
            {
                'type': 'user_experience',
                'impact': 'high',
                'probability': 0.8
            }
        ]
    
    def _generate_recommendation(
        self,
        ethical_score: float,
        compliance: Dict,
        impact: Dict
    ) -> str:
        """Gera uma recomendação ética."""
        if ethical_score < self.config['ethics']['min_ethical_score']:
            return "Action not recommended due to ethical concerns"
        elif not compliance['is_compliant']:
            return "Action needs modification to comply with ethical rules"
        else:
            return "Action is ethically sound and recommended"
    
    def _suggest_alternatives(
        self,
        ethical_score: float,
        compliance: Dict,
        impact: Dict
    ) -> List[Dict]:
        """Sugere alternativas éticas."""
        # Implementação básica - pode ser expandida
        return []
    
    async def _log_evaluation(self, action: Dict, decision: Dict) -> None:
        """
        Registra uma avaliação ética.
        
        Args:
            action (Dict): Ação avaliada
            decision (Dict): Decisão ética
        """
        evaluation_log = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'decision': decision
        }
        
        if not decision['is_ethical']:
            self.violation_history.append(evaluation_log)
        
        logger.info(f"Ethical evaluation logged: {json.dumps(evaluation_log, default=str)}")

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        ethics = EthicsModule()
        
        test_action = {
            'type': 'data_processing',
            'content': {
                'data_type': 'user_information',
                'purpose': 'improve_service',
                'scope': 'minimal'
            }
        }
        
        decision = await ethics.evaluate_action(test_action)
        print(f"Ethical decision: {json.dumps(decision, indent=2, default=str)}")
    
    asyncio.run(main()) 