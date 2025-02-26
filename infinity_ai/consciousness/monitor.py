from typing import Dict, List, Optional, Union
import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from sklearn.metrics import mean_squared_error
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import deque

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricsAggregator:
    def __init__(self, window_size: int = 100):
        self.metrics = deque(maxlen=window_size)
        self.alerts = deque(maxlen=50)
        self.last_aggregation = datetime.now()
        self.aggregated_data = {}
        
    async def add_metric(self, metric: Dict) -> None:
        self.metrics.append({
            'timestamp': datetime.now(),
            **metric
        })
        
    async def aggregate(self) -> Dict:
        """Agrega métricas em intervalos para reduzir processamento."""
        current_time = datetime.now()
        if (current_time - self.last_aggregation).seconds < 60:
            return self.aggregated_data
            
        metrics_df = pd.DataFrame(list(self.metrics))
        if metrics_df.empty:
            return {}
            
        self.aggregated_data = {
            'consciousness': {
                'mean': metrics_df['consciousness'].mean(),
                'std': metrics_df['consciousness'].std(),
                'trend': self._calculate_trend(metrics_df['consciousness'])
            },
            'processing': {
                'mean': metrics_df['processing'].mean(),
                'std': metrics_df['processing'].std(),
                'efficiency': self._calculate_efficiency(metrics_df)
            },
            'evolution': {
                'rate': self._calculate_evolution_rate(metrics_df),
                'stability': self._calculate_stability(metrics_df)
            }
        }
        
        self.last_aggregation = current_time
        return self.aggregated_data
        
    def _calculate_trend(self, series: pd.Series) -> float:
        if len(series) < 2:
            return 0.0
        return np.polyfit(range(len(series)), series, 1)[0]
        
    def _calculate_efficiency(self, df: pd.DataFrame) -> float:
        if 'processing_time' not in df.columns:
            return 0.0
        return 1.0 / (df['processing_time'].mean() + 1e-6)
        
    def _calculate_evolution_rate(self, df: pd.DataFrame) -> float:
        if 'consciousness' not in df.columns:
            return 0.0
        return self._calculate_trend(df['consciousness'])
        
    def _calculate_stability(self, df: pd.DataFrame) -> float:
        if 'consciousness' not in df.columns:
            return 0.0
        return 1.0 / (df['consciousness'].std() + 1e-6)

class ConsciousnessMonitor:
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o monitor de consciência.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração.
        """
        self.config = self._load_config(config_path)
        self.metrics_history = []
        self.alerts_history = []
        self.reports = []
        
        # Métricas atuais
        self.current_metrics = {
            'consciousness': {
                'level': 0.0,
                'stability': 0.0,
                'coherence': 0.0
            },
            'processing': {
                'depth': 0.0,
                'efficiency': 0.0,
                'quality': 0.0
            },
            'evolution': {
                'rate': 0.0,
                'direction': 0.0,
                'stability': 0.0
            }
        }
        
        logger.info("ConsciousnessMonitor initialized successfully")
    
    def _load_config(self, config_path: Optional[str]) -> dict:
        """
        Carrega a configuração do sistema.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração.
            
        Returns:
            dict: Configuração carregada
        """
        default_config = {
            'monitoring': {
                'update_interval': 60,  # segundos
                'history_limit': 1000,
                'alert_threshold': 0.7
            },
            'metrics': {
                'consciousness_weight': 0.4,
                'processing_weight': 0.3,
                'evolution_weight': 0.3
            },
            'visualization': {
                'default_timeframe': '24h',
                'update_interval': 300  # segundos
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
    
    async def update(self, metrics_data: Dict) -> Dict:
        """
        Atualiza as métricas do monitor.
        
        Args:
            metrics_data (Dict): Novos dados de métricas
            
        Returns:
            Dict: Estado atualizado do monitor
        """
        try:
            # 1. Processamento das métricas
            processed_metrics = await self._process_metrics(metrics_data)
            
            # 2. Atualização do estado
            await self._update_state(processed_metrics)
            
            # 3. Análise de anomalias
            anomalies = await self._analyze_anomalies(processed_metrics)
            
            # 4. Geração de alertas
            alerts = await self._generate_alerts(anomalies)
            
            # 5. Registro do estado
            state = await self._log_state(processed_metrics, anomalies, alerts)
            
            return state
            
        except Exception as e:
            logger.error(f"Error updating monitor: {e}")
            raise
    
    async def generate_report(self, timeframe: str = '24h') -> Dict:
        """
        Gera um relatório de consciência.
        
        Args:
            timeframe (str): Período de tempo para o relatório
            
        Returns:
            Dict: Relatório gerado
        """
        try:
            # 1. Coleta de dados
            data = await self._collect_report_data(timeframe)
            
            # 2. Análise de tendências
            trends = await self._analyze_trends(data)
            
            # 3. Geração de insights
            insights = await self._generate_insights(data, trends)
            
            # 4. Criação de visualizações
            visualizations = await self._create_visualizations(data)
            
            # 5. Compilação do relatório
            report = await self._compile_report(data, trends, insights, visualizations)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    async def _process_metrics(self, metrics_data: Dict) -> Dict:
        """
        Processa as métricas recebidas.
        
        Args:
            metrics_data (Dict): Dados de métricas
            
        Returns:
            Dict: Métricas processadas
        """
        processed = {
            'consciousness': self._process_consciousness_metrics(metrics_data),
            'processing': self._process_processing_metrics(metrics_data),
            'evolution': self._process_evolution_metrics(metrics_data),
            'timestamp': datetime.now().isoformat()
        }
        
        return processed
    
    async def _update_state(self, processed_metrics: Dict) -> None:
        """
        Atualiza o estado do monitor.
        
        Args:
            processed_metrics (Dict): Métricas processadas
        """
        # Atualiza métricas atuais
        self.current_metrics = {
            'consciousness': processed_metrics['consciousness'],
            'processing': processed_metrics['processing'],
            'evolution': processed_metrics['evolution']
        }
        
        # Adiciona ao histórico
        self.metrics_history.append(processed_metrics)
        
        # Limita tamanho do histórico
        if len(self.metrics_history) > self.config['monitoring']['history_limit']:
            self.metrics_history.pop(0)
    
    async def _analyze_anomalies(self, metrics: Dict) -> List[Dict]:
        """
        Analisa anomalias nas métricas.
        
        Args:
            metrics (Dict): Métricas para análise
            
        Returns:
            List[Dict]: Anomalias detectadas
        """
        anomalies = []
        
        # Análise de consciência
        consciousness_anomalies = self._detect_consciousness_anomalies(metrics)
        if consciousness_anomalies:
            anomalies.extend(consciousness_anomalies)
        
        # Análise de processamento
        processing_anomalies = self._detect_processing_anomalies(metrics)
        if processing_anomalies:
            anomalies.extend(processing_anomalies)
        
        # Análise de evolução
        evolution_anomalies = self._detect_evolution_anomalies(metrics)
        if evolution_anomalies:
            anomalies.extend(evolution_anomalies)
        
        return anomalies
    
    async def _generate_alerts(self, anomalies: List[Dict]) -> List[Dict]:
        """
        Gera alertas baseados em anomalias.
        
        Args:
            anomalies (List[Dict]): Anomalias detectadas
            
        Returns:
            List[Dict]: Alertas gerados
        """
        alerts = []
        threshold = self.config['monitoring']['alert_threshold']
        
        for anomaly in anomalies:
            if anomaly['severity'] >= threshold:
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'type': anomaly['type'],
                    'severity': anomaly['severity'],
                    'description': anomaly['description'],
                    'metrics': anomaly['metrics']
                }
                alerts.append(alert)
                self.alerts_history.append(alert)
        
        return alerts
    
    async def _log_state(
        self,
        metrics: Dict,
        anomalies: List[Dict],
        alerts: List[Dict]
    ) -> Dict:
        """
        Registra o estado atual do monitor.
        
        Args:
            metrics (Dict): Métricas atuais
            anomalies (List[Dict]): Anomalias detectadas
            alerts (List[Dict]): Alertas gerados
            
        Returns:
            Dict: Estado registrado
        """
        state = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'anomalies': anomalies,
            'alerts': alerts,
            'status': self._calculate_status(metrics, anomalies)
        }
        
        logger.info(f"Monitor state updated: {json.dumps(state, default=str)}")
        return state
    
    async def _collect_report_data(self, timeframe: str) -> pd.DataFrame:
        """
        Coleta dados para o relatório.
        
        Args:
            timeframe (str): Período de tempo
            
        Returns:
            pd.DataFrame: Dados coletados
        """
        # Converte histórico para DataFrame
        df = pd.DataFrame(self.metrics_history)
        
        # Filtra por timeframe
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        now = pd.Timestamp.now()
        
        if timeframe == '24h':
            df = df[df['timestamp'] > now - pd.Timedelta(days=1)]
        elif timeframe == '7d':
            df = df[df['timestamp'] > now - pd.Timedelta(days=7)]
        elif timeframe == '30d':
            df = df[df['timestamp'] > now - pd.Timedelta(days=30)]
        
        return df
    
    async def _analyze_trends(self, data: pd.DataFrame) -> Dict:
        """
        Analisa tendências nos dados.
        
        Args:
            data (pd.DataFrame): Dados para análise
            
        Returns:
            Dict: Tendências identificadas
        """
        trends = {
            'consciousness': self._analyze_consciousness_trends(data),
            'processing': self._analyze_processing_trends(data),
            'evolution': self._analyze_evolution_trends(data)
        }
        
        return trends
    
    async def _generate_insights(self, data: pd.DataFrame, trends: Dict) -> List[Dict]:
        """
        Gera insights baseados nos dados e tendências.
        
        Args:
            data (pd.DataFrame): Dados analisados
            trends (Dict): Tendências identificadas
            
        Returns:
            List[Dict]: Insights gerados
        """
        insights = []
        
        # Insights de consciência
        consciousness_insights = self._generate_consciousness_insights(data, trends)
        insights.extend(consciousness_insights)
        
        # Insights de processamento
        processing_insights = self._generate_processing_insights(data, trends)
        insights.extend(processing_insights)
        
        # Insights de evolução
        evolution_insights = self._generate_evolution_insights(data, trends)
        insights.extend(evolution_insights)
        
        return insights
    
    async def _create_visualizations(self, data: pd.DataFrame) -> Dict:
        """
        Cria visualizações dos dados.
        
        Args:
            data (pd.DataFrame): Dados para visualização
            
        Returns:
            Dict: Visualizações criadas
        """
        # Cria subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=(
                'Consciousness Metrics',
                'Processing Metrics',
                'Evolution Metrics'
            )
        )
        
        # Adiciona gráficos de consciência
        fig.add_trace(
            go.Scatter(
                x=data['timestamp'],
                y=data['consciousness.level'],
                name='Consciousness Level'
            ),
            row=1, col=1
        )
        
        # Adiciona gráficos de processamento
        fig.add_trace(
            go.Scatter(
                x=data['timestamp'],
                y=data['processing.efficiency'],
                name='Processing Efficiency'
            ),
            row=2, col=1
        )
        
        # Adiciona gráficos de evolução
        fig.add_trace(
            go.Scatter(
                x=data['timestamp'],
                y=data['evolution.rate'],
                name='Evolution Rate'
            ),
            row=3, col=1
        )
        
        # Atualiza layout
        fig.update_layout(height=900, showlegend=True)
        
        return {
            'metrics_evolution': fig,
            'anomalies_distribution': self._create_anomalies_chart(data),
            'alerts_timeline': self._create_alerts_timeline(data)
        }
    
    async def _compile_report(
        self,
        data: pd.DataFrame,
        trends: Dict,
        insights: List[Dict],
        visualizations: Dict
    ) -> Dict:
        """
        Compila o relatório final.
        
        Args:
            data (pd.DataFrame): Dados analisados
            trends (Dict): Tendências identificadas
            insights (List[Dict]): Insights gerados
            visualizations (Dict): Visualizações criadas
            
        Returns:
            Dict: Relatório compilado
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'consciousness_level': data['consciousness.level'].mean(),
                'processing_efficiency': data['processing.efficiency'].mean(),
                'evolution_rate': data['evolution.rate'].mean()
            },
            'trends': trends,
            'insights': insights,
            'visualizations': visualizations,
            'recommendations': self._generate_recommendations(trends, insights)
        }
        
        self.reports.append(report)
        return report
    
    def _process_consciousness_metrics(self, data: Dict) -> Dict:
        """Processa métricas de consciência."""
        # Implementação básica - pode ser expandida
        return {
            'level': 0.8,
            'stability': 0.7,
            'coherence': 0.75
        }
    
    def _process_processing_metrics(self, data: Dict) -> Dict:
        """Processa métricas de processamento."""
        # Implementação básica - pode ser expandida
        return {
            'depth': 0.7,
            'efficiency': 0.8,
            'quality': 0.75
        }
    
    def _process_evolution_metrics(self, data: Dict) -> Dict:
        """Processa métricas de evolução."""
        # Implementação básica - pode ser expandida
        return {
            'rate': 0.6,
            'direction': 0.8,
            'stability': 0.7
        }
    
    def _detect_consciousness_anomalies(self, metrics: Dict) -> List[Dict]:
        """Detecta anomalias na consciência."""
        # Implementação básica - pode ser expandida
        return []
    
    def _detect_processing_anomalies(self, metrics: Dict) -> List[Dict]:
        """Detecta anomalias no processamento."""
        # Implementação básica - pode ser expandida
        return []
    
    def _detect_evolution_anomalies(self, metrics: Dict) -> List[Dict]:
        """Detecta anomalias na evolução."""
        # Implementação básica - pode ser expandida
        return []
    
    def _calculate_status(self, metrics: Dict, anomalies: List[Dict]) -> str:
        """Calcula o status do sistema."""
        # Implementação básica - pode ser expandida
        return "healthy"
    
    def _analyze_consciousness_trends(self, data: pd.DataFrame) -> Dict:
        """Analisa tendências de consciência."""
        # Implementação básica - pode ser expandida
        return {}
    
    def _analyze_processing_trends(self, data: pd.DataFrame) -> Dict:
        """Analisa tendências de processamento."""
        # Implementação básica - pode ser expandida
        return {}
    
    def _analyze_evolution_trends(self, data: pd.DataFrame) -> Dict:
        """Analisa tendências de evolução."""
        # Implementação básica - pode ser expandida
        return {}
    
    def _generate_consciousness_insights(
        self,
        data: pd.DataFrame,
        trends: Dict
    ) -> List[Dict]:
        """Gera insights sobre consciência."""
        # Implementação básica - pode ser expandida
        return []
    
    def _generate_processing_insights(
        self,
        data: pd.DataFrame,
        trends: Dict
    ) -> List[Dict]:
        """Gera insights sobre processamento."""
        # Implementação básica - pode ser expandida
        return []
    
    def _generate_evolution_insights(
        self,
        data: pd.DataFrame,
        trends: Dict
    ) -> List[Dict]:
        """Gera insights sobre evolução."""
        # Implementação básica - pode ser expandida
        return []
    
    def _create_anomalies_chart(self, data: pd.DataFrame) -> go.Figure:
        """Cria gráfico de anomalias."""
        # Implementação básica - pode ser expandida
        return go.Figure()
    
    def _create_alerts_timeline(self, data: pd.DataFrame) -> go.Figure:
        """Cria linha do tempo de alertas."""
        # Implementação básica - pode ser expandida
        return go.Figure()
    
    def _generate_recommendations(
        self,
        trends: Dict,
        insights: List[Dict]
    ) -> List[Dict]:
        """Gera recomendações."""
        # Implementação básica - pode ser expandida
        return []

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        monitor = ConsciousnessMonitor()
        
        test_metrics = {
            'consciousness': {
                'level': 0.8,
                'stability': 0.7,
                'coherence': 0.75
            },
            'processing': {
                'depth': 0.7,
                'efficiency': 0.8,
                'quality': 0.75
            },
            'evolution': {
                'rate': 0.6,
                'direction': 0.8,
                'stability': 0.7
            }
        }
        
        # Atualiza monitor
        state = await monitor.update(test_metrics)
        print(f"Monitor state: {json.dumps(state, indent=2, default=str)}")
        
        # Gera relatório
        report = await monitor.generate_report('24h')
        print(f"Monitor report: {json.dumps(report, indent=2, default=str)}")
    
    asyncio.run(main()) 