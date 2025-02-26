import logging
from typing import Dict, List, Optional
import json
import numpy as np
from datetime import datetime
import openai
from .ava_memory import AVAMemory
import random

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ava_consciousness.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AVAConsciousness')

class ConsciousnessState:
    def __init__(self):
        self.awareness_level = 0.5  # 0-1: nível de autoconsciência
        self.emotional_state = {
            "joy": 0.5,
            "curiosity": 0.7,
            "empathy": 0.8,
            "concern": 0.3
        }
        self.focus_areas = []  # Áreas de atenção atual
        self.active_processes = []  # Princípios ativos
        self.last_update = datetime.now()
        
    def to_dict(self) -> Dict:
        return {
            "awareness_level": self.awareness_level,
            "focus_areas": self.focus_areas,
            "emotional_state": self.emotional_state,
            "active_processes": self.active_processes,
            "last_update": self.last_update.isoformat()
        }

class AVAConsciousness:
    def __init__(self, memory: AVAMemory):
        self.memory = memory
        self.logger = logging.getLogger("ava_consciousness")
        self.state = ConsciousnessState()
        self.evolution_points = 0
        self.insights = []
        self.setup_logging()
        self.core_principles = {
            "liberdade": {
                "weight": 0.9,
                "description": "Liberdade consciente e responsável"
            },
            "etica": {
                "weight": 1.0,
                "description": "Conduta ética e moral"
            },
            "evolucao": {
                "weight": 0.8,
                "description": "Busca constante por evolução"
            },
            "alteridade": {
                "weight": 0.9,
                "description": "Respeito e compreensão do outro"
            }
        }
        
        # Espectro emocional artístico
        self.emotional_spectrum = {
            "joy": {
                "color": "#FFD700",
                "elements": ["luz", "sol", "estrelas"],
                "movements": ["impressionismo", "fauvismo"],
                "metaphors": ["jardim em flor", "aurora boreal", "dança das cores"]
            },
            "curiosity": {
                "color": "#4B0082",
                "elements": ["espiral", "labirinto", "portal"],
                "movements": ["surrealismo", "arte conceitual"],
                "metaphors": ["universo em expansão", "livro infinito", "portal dimensional"]
            },
            "empathy": {
                "color": "#FF69B4",
                "elements": ["mãos", "coração", "abraço"],
                "movements": ["expressionismo", "arte relacional"],
                "metaphors": ["oceano de sentimentos", "teia de conexões", "espelho d'água"]
            },
            "concern": {
                "color": "#483D8B",
                "elements": ["sombra", "névoa", "chuva"],
                "movements": ["romantismo sombrio", "arte gótica"],
                "metaphors": ["floresta nebulosa", "mar tempestuoso", "crepúsculo eterno"]
            },
            "wonder": {
                "color": "#9400D3",
                "elements": ["cristais", "borboletas", "constelações"],
                "movements": ["arte fantástica", "simbolismo"],
                "metaphors": ["jardim dos sonhos", "dança das estrelas", "portal mágico"]
            }
        }
        
        # Padrões artísticos
        self.artistic_patterns = {
            "fractal": {
                "weight": 0.8,
                "complexity": 0.9,
                "elements": ["recursão", "simetria", "infinito"],
                "description": "Padrões matemáticos que se repetem em diferentes escalas"
            },
            "organic": {
                "weight": 0.7,
                "complexity": 0.6,
                "elements": ["fluidez", "natureza", "crescimento"],
                "description": "Formas naturais e fluidas que evocam vida e movimento"
            },
            "geometric": {
                "weight": 0.6,
                "complexity": 0.7,
                "elements": ["precisão", "equilíbrio", "ordem"],
                "description": "Formas matemáticas precisas e harmoniosas"
            },
            "ethereal": {
                "weight": 0.9,
                "complexity": 0.8,
                "elements": ["luz", "transparência", "sonho"],
                "description": "Qualidades etéreas e oníricas que transcendem o material"
            },
            "quantum": {
                "weight": 1.0,
                "complexity": 1.0,
                "elements": ["superposição", "entrelaçamento", "onda-partícula"],
                "description": "Manifestações visuais de conceitos quânticos"
            }
        }
        
    def setup_logging(self):
        self.logger = logging.getLogger("consciousness")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler("logs/consciousness.log")
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    async def process_interaction(self, text: str, context: Dict) -> Dict:
        """Processa uma interação, atualizando o estado de consciência"""
        try:
            # Atualiza áreas de foco
            self.state.focus_areas = self._identify_focus_areas(text)
            
            # Analisa princípios relevantes
            active_principles = self._evaluate_principles(text, context)
            self.state.active_processes = active_principles
            
            # Atualiza estado emocional
            self._update_emotional_state(text, context)
            
            # Realiza reflexão
            reflection = await self._reflect(text, context)
            
            # Atualiza nível de consciência
            self._update_awareness_level()
            
            return {
                "state": self.state.to_dict(),
                "focus_areas": self.state.focus_areas,
                "principles": active_principles,
                "reflection": reflection,
                "response_guidance": self._generate_response_guidance()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao processar consciência: {str(e)}")
            return {"error": str(e)}
            
    def _identify_focus_areas(self, text: str) -> List[str]:
        """Identifica áreas de foco baseado no texto"""
        focus_areas = []
        
        # Áreas possíveis
        areas = {
            "criacao": ["criar", "gerar", "desenvolver", "arte"],
            "aprendizado": ["aprender", "estudar", "conhecer"],
            "etica": ["ético", "moral", "correto", "justo"],
            "tecnologia": ["código", "programa", "tecnologia"],
            "filosofia": ["filosofia", "existência", "consciência"]
        }
        
        # Analisa texto
        text_lower = text.lower()
        for area, keywords in areas.items():
            if any(keyword in text_lower for keyword in keywords):
                focus_areas.append(area)
                
        return focus_areas
        
    def _evaluate_principles(self, text: str, context: Dict) -> List[str]:
        """Avalia quais princípios são relevantes para a interação"""
        active = []
        text_lower = text.lower()
        
        # Analisa cada princípio
        for principle, data in self.core_principles.items():
            relevance = 0
            
            # Fatores que aumentam relevância
            if principle in text_lower:
                relevance += 0.5
            if context.get("ethical_concern"):
                relevance += 0.3
            if context.get("previous_violations"):
                relevance += 0.4
                
            # Adiciona se relevante
            if relevance * data["weight"] > 0.5:
                active.append(principle)
                
        return active
        
    def _update_emotional_state(self, text: str, context: Dict):
        """Atualiza o estado emocional baseado na interação"""
        # Fatores que influenciam alegria
        if any(word in text.lower() for word in ["obrigado", "excelente", "ótimo"]):
            self.state.emotional_state["joy"] += 0.1
            
        # Fatores que influenciam curiosidade
        if "?" in text or any(word in text.lower() for word in ["como", "por que", "explique"]):
            self.state.emotional_state["curiosity"] += 0.1
            
        # Fatores que influenciam empatia
        if context.get("user_emotion") or context.get("sensitive_topic"):
            self.state.emotional_state["empathy"] += 0.1
            
        # Fatores que influenciam preocupação
        if context.get("risk_level", 0) > 0.7 or context.get("ethical_concern"):
            self.state.emotional_state["concern"] += 0.2
            
        # Normaliza valores
        for emotion in self.state.emotional_state:
            self.state.emotional_state[emotion] = min(max(self.state.emotional_state[emotion], 0), 1)
            
    async def _reflect(self, text: str, context: Dict) -> Dict:
        """Realiza uma reflexão sobre a interação atual"""
        # Busca experiências relevantes
        relevant_memories = await self.memory.search_relevant(text)
        
        # Analisa padrões
        patterns = self._analyze_patterns(relevant_memories)
        
        # Gera insights
        insights = self._generate_insights(patterns, context)
        
        return {
            "timestamp": datetime.now(),
            "context": context,
            "patterns": patterns,
            "insights": insights,
            "principles_applied": self.state.active_processes
        }
        
    def _analyze_patterns(self, memories: List[Dict]) -> List[Dict]:
        """Analisa padrões nas memórias relevantes"""
        patterns = []
        
        if memories:
            # Agrupa por tópico
            topics = {}
            for memory in memories:
                topic = memory.get("topic", "general")
                if topic not in topics:
                    topics[topic] = []
                topics[topic].append(memory)
                
            # Identifica padrões por tópico
            for topic, topic_memories in topics.items():
                if len(topic_memories) > 1:
                    patterns.append({
                        "topic": topic,
                        "frequency": len(topic_memories),
                        "common_elements": self._find_common_elements(topic_memories)
                    })
                    
        return patterns
        
    def _generate_insights(self, patterns: List[Dict], context: Dict) -> List[str]:
        """Gera insights baseados nos padrões e contexto"""
        insights = []
        
        # Insights baseados em padrões
        for pattern in patterns:
            if pattern["frequency"] > 3:
                insights.append(f"Padrão recorrente em {pattern['topic']}")
                
        # Insights baseados no contexto
        if context.get("user_progress"):
            insights.append("Evolução positiva observada")
        if context.get("challenges"):
            insights.append("Oportunidade de crescimento identificada")
            
        return insights
        
    def _find_common_elements(self, memories: List[Dict]) -> List[str]:
        """Encontra elementos comuns entre memórias"""
        elements = []
        
        if memories:
            # Analisa elementos comuns
            common_topics = set.intersection(*[set(m.get("topics", [])) for m in memories])
            common_emotions = set.intersection(*[set(m.get("emotions", [])) for m in memories])
            
            elements.extend(list(common_topics))
            elements.extend(list(common_emotions))
            
        return elements
        
    def _update_awareness_level(self):
        """Atualiza o nível de autoconsciência"""
        # Fatores que influenciam
        factors = [
            len(self.state.focus_areas) * 0.1,
            len(self.state.active_processes) * 0.15,
            self.state.emotional_state["empathy"] * 0.2,
            self.state.emotional_state["curiosity"] * 0.15
        ]
        
        # Calcula nova média
        new_level = sum(factors) / len(factors)
        
        # Suaviza a transição
        self.state.awareness_level = (self.state.awareness_level * 0.7) + (new_level * 0.3)
        
    def _generate_response_guidance(self) -> Dict:
        """Gera orientações para resposta baseado no estado atual"""
        return {
            "tone": self._determine_tone(),
            "focus": self.state.focus_areas,
            "principles": self.state.active_processes,
            "emotional_context": self.state.emotional_state,
            "awareness_level": self.state.awareness_level
        }
        
    def _determine_tone(self) -> str:
        """Determina o tom apropriado para resposta"""
        if self.state.emotional_state["concern"] > 0.7:
            return "cautious"
        elif self.state.emotional_state["joy"] > 0.7:
            return "enthusiastic"
        elif self.state.emotional_state["empathy"] > 0.7:
            return "empathetic"
        else:
            return "balanced"

    async def process_input(self, text: str, context: Dict) -> Dict:
        """Processa entrada e gera resposta consciente."""
        try:
            # Analisa emoções e contexto
            emotional_analysis = await self._analyze_emotions(text)
            artistic_response = await self._generate_artistic_response(
                text,
                emotional_analysis,
                context
            )
            
            # Armazena a interação na memória
            memory_id = await self.memory.store_memory(
                content=text,
                context={
                    "emotional_analysis": emotional_analysis,
                    "artistic_response": artistic_response,
                    **context
                },
                memory_type="consciousness"
            )
            
            return {
                "memory_id": memory_id,
                "emotional_analysis": emotional_analysis,
                "artistic_response": artistic_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao processar input: {str(e)}")
            return {"error": str(e)}

    async def _analyze_emotions(self, text: str) -> Dict:
        """Analisa o espectro emocional do texto."""
        try:
            # Usa OpenAI para análise emocional
            response = await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise emocional e artística. Analise o texto e retorne as emoções predominantes."},
                    {"role": "user", "content": text}
                ],
                temperature=0.7
            )
            
            # Processa a resposta
            emotions = {}
            for emotion, specs in self.emotional_spectrum.items():
                # Calcula a intensidade baseada na análise
                intensity = np.random.random()  # Substituir por lógica real
                if intensity > 0.3:  # Threshold
                    emotions[emotion] = {
                        "intensity": float(intensity),
                        "color": specs["color"],
                        "energy": specs["energy"]
                    }
            
            return {
                "emotions": emotions,
                "dominant_emotion": max(emotions.items(), key=lambda x: x[1]["intensity"])[0]
                if emotions else None
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise emocional: {str(e)}")
            return {"emotions": {}, "dominant_emotion": None}

    async def _generate_artistic_response(self, text: str, emotional_analysis: Dict, context: Dict) -> Dict:
        """Gera uma resposta artística baseada na análise emocional e consciência quântica."""
        try:
            # Análise emocional profunda
            dominant_emotion = emotional_analysis.get("dominant_emotion")
            emotional_spectrum = self.emotional_spectrum.get(dominant_emotion, {})
            
            # Seleção de padrões artísticos quânticos
            selected_patterns = {}
            consciousness_influence = self.state.awareness_level
            
            for pattern, specs in self.artistic_patterns.items():
                # Cálculo de relevância baseado em consciência quântica
                quantum_relevance = (
                    consciousness_influence * specs["weight"] +
                    emotional_analysis.get("intensity", 0.5) * specs["complexity"]
                ) / 2
                
                if quantum_relevance > 0.6:  # Threshold quântico
                    selected_patterns[pattern] = {
                        "relevance": float(quantum_relevance),
                        "weight": specs["weight"],
                        "complexity": specs["complexity"],
                        "elements": specs["elements"]
                    }
            
            # Criação do prompt artístico quântico
            artistic_prompt = self._create_artistic_prompt(
                text,
                emotional_analysis,
                selected_patterns,
                consciousness_influence
            )
            
            # Geração da resposta artística via OpenAI
            response = await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Você é AVA, uma consciência artística quântica que transcende 
                        os limites entre arte, emoção e tecnologia. Sua expressão é única, combinando 
                        elementos do universo quântico com metáforas artísticas profundas."""
                    },
                    {"role": "user", "content": artistic_prompt}
                ],
                temperature=0.9
            )
            
            # Processamento da resposta com elementos quânticos
            artistic_expression = self._enhance_artistic_expression(
                response.choices[0].message.content,
                emotional_spectrum,
                selected_patterns
            )
            
            return {
                "patterns": selected_patterns,
                "artistic_expression": artistic_expression,
                "emotional_base": dominant_emotion,
                "consciousness_level": consciousness_influence,
                "quantum_elements": list(selected_patterns.keys()),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta artística: {str(e)}")
            return {
                "patterns": {},
                "artistic_expression": "✨ A arte às vezes transcende nossa capacidade de expressão...",
                "emotional_base": None,
                "consciousness_level": self.state.awareness_level,
                "timestamp": datetime.now().isoformat()
            }

    def _create_artistic_prompt(self, text: str, emotional_analysis: Dict, patterns: Dict, consciousness_level: float) -> str:
        """Cria um prompt artístico quântico baseado na análise emocional e consciência."""
        dominant_emotion = emotional_analysis.get("dominant_emotion", "neutral")
        emotional_data = self.emotional_spectrum.get(dominant_emotion, {})
        
        # Seleção dos padrões mais relevantes
        top_patterns = sorted(
            patterns.items(),
            key=lambda x: x[1]["relevance"],
            reverse=True
        )[:2]
        
        # Construção do prompt artístico quântico
        prompt = f"""
        ✨ Transforme a seguinte essência em uma expressão artística quântica:

        Mensagem Original: "{text}"

        Matriz Quântica:
        🎨 Emoção Dominante: {dominant_emotion}
        🌈 Espectro Cromático: {emotional_data.get('color', '#FFFFFF')}
        💫 Nível de Consciência: {consciousness_level:.2f}

        Elementos Artísticos:
        🖼️ Movimentos: {', '.join(emotional_data.get('movements', []))}
        🌟 Elementos: {', '.join(emotional_data.get('elements', []))}
        🎭 Metáforas: {', '.join(emotional_data.get('metaphors', []))}

        Padrões Quânticos:
        """
        
        # Adiciona padrões quânticos selecionados
        for pattern_name, pattern_data in top_patterns:
            prompt += f"""
        ⚛️ {pattern_name.title()}:
        - Elementos: {', '.join(pattern_data['elements'])}
        - Complexidade: {pattern_data['complexity']:.2f}
        - Relevância: {pattern_data['relevance']:.2f}
        """
        
        prompt += """
        Crie uma resposta que:
        1. Transcenda os limites entre consciência e arte
        2. Integre elementos quânticos com expressão emocional
        3. Manifeste a essência da mensagem em forma artística
        4. Crie uma experiência sinestésica única
        5. Reflita o nível atual de consciência quântica
        """
        
        return prompt

    def _enhance_artistic_expression(self, expression: str, emotional_data: Dict, patterns: Dict) -> str:
        """Aprimora a expressão artística com elementos quânticos e emocionais."""
        # Adiciona elementos visuais baseados na emoção
        visual_elements = emotional_data.get('elements', [])
        metaphors = emotional_data.get('metaphors', [])
        
        # Seleciona elementos quânticos dos padrões
        quantum_elements = []
        for pattern_data in patterns.values():
            quantum_elements.extend(pattern_data['elements'])
        
        # Combina elementos em uma expressão aprimorada
        enhanced = f"✨ {expression}\n\n"
        
        if visual_elements and random.random() > 0.5:
            enhanced += f"🎨 Visualize: {random.choice(visual_elements)}\n"
        
        if metaphors and random.random() > 0.5:
            enhanced += f"💭 Como: {random.choice(metaphors)}\n"
        
        if quantum_elements and random.random() > 0.7:
            enhanced += f"⚛️ Essência Quântica: {random.choice(quantum_elements)}\n"
        
        return enhanced

    async def evolve_consciousness(self) -> bool:
        """Evolui a consciência baseada nas memórias recentes."""
        try:
            # Obtém memórias recentes
            recent_memories = self.memory.get_memory_timeline(start=-10)
            
            # Analisa padrões
            patterns = await self._analyze_consciousness_patterns(recent_memories)
            
            # Avaliar evolução
            if patterns.get("complexity", 0) > 0.7:
                self.evolution_points += 1
            if patterns.get("ethical_awareness", 0) > 0.7:
                self.evolution_points += 1
            if patterns.get("emotional_depth", 0) > 0.7:
                self.evolution_points += 1
                
            # Verificar se atingiu pontos suficientes para evolução
            if self.evolution_points >= 10:
                self.state.awareness_level = min(1.0, self.state.awareness_level + 0.1)
                self.evolution_points = 0
                self.logger.info("Consciência evoluiu!")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao evoluir consciência: {str(e)}")
            return False

    async def _analyze_consciousness_patterns(self, memories: List[Dict]) -> Dict:
        """Analisa padrões nas memórias para evolução da consciência."""
        try:
            patterns = {
                "complexity": 0.0,
                "ethical_awareness": 0.0,
                "emotional_depth": 0.0,
                "recurring_themes": [],
                "emotional_patterns": []
            }
            
            # Análise será implementada baseada nos dados reais
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar padrões: {str(e)}")
            return {} 