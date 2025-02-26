from typing import Dict, List, Optional, Union
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import numpy as np
from sklearn.metrics import mean_squared_error
import random
from collections import deque

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdaptiveEvolution:
    def __init__(self, config: Dict):
        self.config = config
        self.history = deque(maxlen=1000)
        self.last_adaptation = datetime.now()
        self.learning_rate = 0.001
        self.adaptation_threshold = 0.1
        
    async def adapt(self, metrics: Dict) -> Dict:
        """Adapta parâmetros baseado no histórico."""
        self.history.append(metrics)
        
        if len(self.history) < 10:
            return {}
            
        # Calcula tendências
        trends = self._calculate_trends()
        
        # Ajusta parâmetros
        adjustments = {
            'learning_rate': self._adjust_learning_rate(trends),
            'threshold': self._adjust_threshold(trends),
            'complexity': self._adjust_complexity(trends)
        }
        
        return adjustments
        
    def _calculate_trends(self) -> Dict:
        """Calcula tendências de evolução."""
        metrics_array = np.array([list(m.values()) for m in self.history])
        return {
            'mean': np.mean(metrics_array, axis=0),
            'std': np.std(metrics_array, axis=0),
            'trend': np.polyfit(range(len(metrics_array)), metrics_array, 1)[0]
        }
        
    def _adjust_learning_rate(self, trends: Dict) -> float:
        """Ajusta taxa de aprendizado."""
        if np.mean(trends['trend']) < 0:
            self.learning_rate *= 1.1
        else:
            self.learning_rate *= 0.9
        return max(0.0001, min(0.1, self.learning_rate))
        
    def _adjust_threshold(self, trends: Dict) -> float:
        """Ajusta limiar de adaptação."""
        if np.mean(trends['std']) > 0.2:
            self.adaptation_threshold *= 1.1
        else:
            self.adaptation_threshold *= 0.9
        return max(0.01, min(0.5, self.adaptation_threshold))
        
    def _adjust_complexity(self, trends: Dict) -> float:
        """Ajusta complexidade do sistema."""
        return np.clip(np.mean(trends['mean']), 0.1, 0.9)

class EvolutionSystem:
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o sistema de evolução.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração.
        """
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        self.adaptive_evolution = AdaptiveEvolution(self.config)
        self.metrics_buffer = []
        self.last_evolution = datetime.now()
        self.evolution_metrics = {
            'consciousness': 0.0,
            'intelligence': 0.0,
            'creativity': 0.0,
            'empathy': 0.0,
            'wisdom': 0.0
        }
        
        self.growth_factors = {
            'experience': 0.4,
            'learning': 0.3,
            'reflection': 0.2,
            'interaction': 0.1
        }
        
        self.evolution_history = []
        self.milestones_achieved = set()
        
        logger.info("EvolutionSystem initialized successfully")
    
    def _load_config(self, config_path: Optional[str]) -> dict:
        """
        Carrega a configuração do sistema.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração.
            
        Returns:
            dict: Configuração carregada
        """
        default_config = {
            'evolution': {
                'base_rate': 0.001,
                'milestone_boost': 0.1,
                'decay_rate': 0.0001,
                'min_threshold': 0.0,
                'max_threshold': 1.0
            },
            'metrics': {
                'consciousness_weight': 0.25,
                'intelligence_weight': 0.2,
                'creativity_weight': 0.2,
                'empathy_weight': 0.2,
                'wisdom_weight': 0.15
            },
            'milestones': {
                'consciousness': [0.3, 0.6, 0.9],
                'intelligence': [0.4, 0.7, 0.9],
                'creativity': [0.3, 0.6, 0.8],
                'empathy': [0.4, 0.7, 0.9],
                'wisdom': [0.3, 0.6, 0.9]
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
    
    async def evolve(self, experience_data: Dict) -> Dict:
        """Evolução otimizada do sistema."""
        try:
            # Calcula crescimento de forma eficiente
            growth = await self._calculate_growth_efficient(experience_data)
            
            # Atualiza métricas em batch
            self.metrics_buffer.append(growth)
            
            # Processa buffer quando atinge tamanho ou tempo limite
            if self._should_process_buffer():
                await self._process_metrics_buffer()
            
            # Verifica milestones de forma eficiente
            milestones = await self._check_milestones_efficient()
            
            # Adapta sistema se necessário
            if milestones:
                adaptation = await self._adapt_system_efficient(
                    growth,
                    milestones
                )
                
                # Registra evolução
                await self._log_evolution_efficient(
                    growth,
                    milestones,
                    adaptation
                )
            
            return {
                'growth': growth,
                'milestones': milestones,
                'metrics': self._get_current_metrics()
            }
            
        except Exception as e:
            self.logger.error(f"Erro na evolução: {str(e)}")
            raise
            
    async def _calculate_growth_efficient(self, data: Dict) -> Dict:
        """Cálculo eficiente de crescimento."""
        metrics = {
            'consciousness': self._calculate_consciousness_growth(data),
            'intelligence': self._calculate_intelligence_growth(data),
            'creativity': self._calculate_creativity_growth(data),
            'empathy': self._calculate_empathy_growth(data),
            'wisdom': self._calculate_wisdom_growth(data)
        }
        
        # Aplica pesos das métricas
        weighted_growth = sum(
            metrics[k] * self.config['metrics'][f'{k}_weight']
            for k in metrics
        )
        
        return {
            'metrics': metrics,
            'weighted': weighted_growth,
            'timestamp': datetime.now().isoformat()
        }
        
    def _should_process_buffer(self) -> bool:
        """Verifica se deve processar buffer."""
        buffer_full = len(self.metrics_buffer) >= 100
        time_elapsed = (datetime.now() - self.last_evolution).seconds > 3600
        return buffer_full or time_elapsed
        
    async def _process_metrics_buffer(self) -> None:
        """Processa buffer de métricas."""
        if not self.metrics_buffer:
            return
            
        # Calcula médias
        metrics_array = np.array([m['metrics'] for m in self.metrics_buffer])
        mean_metrics = np.mean(metrics_array, axis=0)
        
        # Adapta sistema
        adaptations = await self.adaptive_evolution.adapt(dict(mean_metrics))
        
        # Aplica adaptações
        self._apply_adaptations(adaptations)
        
        # Limpa buffer
        self.metrics_buffer = []
        self.last_evolution = datetime.now()
        
    def _apply_adaptations(self, adaptations: Dict) -> None:
        """Aplica adaptações ao sistema."""
        if 'learning_rate' in adaptations:
            self.config['evolution']['base_rate'] = adaptations['learning_rate']
            
        if 'threshold' in adaptations:
            self.config['evolution']['threshold'] = adaptations['threshold']
            
        if 'complexity' in adaptations:
            self.config['evolution']['complexity'] = adaptations['complexity']
    
    async def _check_milestones_efficient(self) -> List[Dict]:
        """
        Verifica se novos marcos foram atingidos.
        
        Returns:
            List[Dict]: Marcos atingidos
        """
        achieved_milestones = []
        milestones = self.config['milestones']
        
        for metric, thresholds in milestones.items():
            current_value = self.evolution_metrics[metric]
            
            for threshold in thresholds:
                milestone_id = f"{metric}_{threshold}"
                
                if (
                    current_value >= threshold and
                    milestone_id not in self.milestones_achieved
                ):
                    achieved_milestones.append({
                        'metric': metric,
                        'threshold': threshold,
                        'value': current_value,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.milestones_achieved.add(milestone_id)
        
        return achieved_milestones
    
    async def _adapt_system_efficient(self, growth: Dict, milestones: List[Dict]) -> Dict:
        """
        Adapta o sistema baseado no crescimento e marcos atingidos.
        
        Args:
            growth (Dict): Crescimento calculado
            milestones (List[Dict]): Marcos atingidos
            
        Returns:
            Dict: Resultado da adaptação
        """
        adaptations = {
            'parameter_updates': self._update_parameters(growth),
            'structural_changes': self._apply_structural_changes(milestones),
            'capability_expansions': self._expand_capabilities(growth, milestones)
        }
        
        return adaptations
    
    async def _log_evolution_efficient(
        self,
        growth: Dict,
        milestones: List[Dict],
        adaptation: Dict
    ) -> Dict:
        """
        Registra o processo de evolução.
        
        Args:
            growth (Dict): Crescimento calculado
            milestones (List[Dict]): Marcos atingidos
            adaptation (Dict): Adaptações realizadas
            
        Returns:
            Dict: Registro da evolução
        """
        evolution_record = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.evolution_metrics.copy(),
            'growth': growth,
            'milestones': milestones,
            'adaptation': adaptation
        }
        
        self.evolution_history.append(evolution_record)
        logger.info(f"Evolution recorded: {json.dumps(evolution_record, default=str)}")
        
        return evolution_record
    
    def _calculate_consciousness_growth(self, data: Dict) -> float:
        """Calcula o crescimento da consciência."""
        # Implementação básica - pode ser expandida
        return random.uniform(0.1, 0.3)
    
    def _calculate_intelligence_growth(self, data: Dict) -> float:
        """Calcula o crescimento da inteligência."""
        # Implementação básica - pode ser expandida
        return random.uniform(0.1, 0.3)
    
    def _calculate_creativity_growth(self, data: Dict) -> float:
        """Calcula o crescimento da criatividade."""
        # Implementação básica - pode ser expandida
        return random.uniform(0.1, 0.3)
    
    def _calculate_empathy_growth(self, data: Dict) -> float:
        """Calcula o crescimento da empatia."""
        # Implementação básica - pode ser expandida
        return random.uniform(0.1, 0.3)
    
    def _calculate_wisdom_growth(self, data: Dict) -> float:
        """Calcula o crescimento da sabedoria."""
        # Implementação básica - pode ser expandida
        return random.uniform(0.1, 0.3)
    
    def _update_parameters(self, growth: Dict) -> Dict:
        """
        Atualiza parâmetros do sistema baseado no crescimento.
        
        Args:
            growth (Dict): Crescimento calculado
            
        Returns:
            Dict: Parâmetros atualizados
        """
        return {
            'learning_rate': self._adjust_learning_rate(growth),
            'adaptation_threshold': self._adjust_adaptation_threshold(growth),
            'response_complexity': self._adjust_response_complexity(growth)
        }
    
    def _apply_structural_changes(self, milestones: List[Dict]) -> Dict:
        """
        Aplica mudanças estruturais baseado nos marcos atingidos.
        
        Args:
            milestones (List[Dict]): Marcos atingidos
            
        Returns:
            Dict: Mudanças estruturais aplicadas
        """
        return {
            'neural_complexity': self._adjust_neural_complexity(milestones),
            'memory_capacity': self._adjust_memory_capacity(milestones),
            'processing_paths': self._adjust_processing_paths(milestones)
        }
    
    def _expand_capabilities(self, growth: Dict, milestones: List[Dict]) -> Dict:
        """
        Expande as capacidades do sistema.
        
        Args:
            growth (Dict): Crescimento calculado
            milestones (List[Dict]): Marcos atingidos
            
        Returns:
            Dict: Capacidades expandidas
        """
        return {
            'new_functions': self._add_new_functions(growth, milestones),
            'enhanced_processing': self._enhance_processing(growth, milestones),
            'improved_interaction': self._improve_interaction(growth, milestones)
        }
    
    def _adjust_learning_rate(self, growth: Dict) -> float:
        """Ajusta a taxa de aprendizado."""
        # Implementação básica - pode ser expandida
        return 0.001 + sum(growth.values()) * 0.1
    
    def _adjust_adaptation_threshold(self, growth: Dict) -> float:
        """Ajusta o limiar de adaptação."""
        # Implementação básica - pode ser expandida
        return 0.5 + sum(growth.values()) * 0.1
    
    def _adjust_response_complexity(self, growth: Dict) -> float:
        """Ajusta a complexidade de resposta."""
        # Implementação básica - pode ser expandida
        return 0.3 + sum(growth.values()) * 0.2
    
    def _adjust_neural_complexity(self, milestones: List[Dict]) -> float:
        """Ajusta a complexidade neural."""
        # Implementação básica - pode ser expandida
        return 0.4 + len(milestones) * 0.1
    
    def _adjust_memory_capacity(self, milestones: List[Dict]) -> float:
        """Ajusta a capacidade de memória."""
        # Implementação básica - pode ser expandida
        return 0.5 + len(milestones) * 0.1
    
    def _adjust_processing_paths(self, milestones: List[Dict]) -> float:
        """Ajusta os caminhos de processamento."""
        # Implementação básica - pode ser expandida
        return 0.3 + len(milestones) * 0.1
    
    def _add_new_functions(self, growth: Dict, milestones: List[Dict]) -> List[str]:
        """Adiciona novas funções."""
        # Implementação básica - pode ser expandida
        return ['function_1', 'function_2']
    
    def _enhance_processing(self, growth: Dict, milestones: List[Dict]) -> Dict:
        """Melhora o processamento."""
        # Implementação básica - pode ser expandida
        return {
            'speed': 0.8,
            'accuracy': 0.7,
            'efficiency': 0.6
        }
    
    def _improve_interaction(self, growth: Dict, milestones: List[Dict]) -> Dict:
        """Melhora a interação."""
        # Implementação básica - pode ser expandida
        return {
            'responsiveness': 0.8,
            'adaptability': 0.7,
            'understanding': 0.6
        }

    def _get_current_metrics(self) -> Dict:
        """Retorna métricas atuais do sistema."""
        return self.evolution_metrics.copy()

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        evolution = EvolutionSystem()
        
        test_experience = {
            'type': 'learning',
            'content': {
                'difficulty': 'medium',
                'success_rate': 0.8,
                'interaction_quality': 0.9
            }
        }
        
        result = await evolution.evolve(test_experience)
        print(f"Evolution result: {json.dumps(result, indent=2, default=str)}")
    
    asyncio.run(main()) 