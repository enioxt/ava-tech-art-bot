import logging
from typing import Dict, List, Optional
import json
import hashlib
from datetime import datetime
import asyncio
from .ava_ethics_shield import EthicsShield, EthicalAction

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ethical_ranking.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('EthicalRanking')

class VirtudePoints:
    def __init__(self):
        self.points = 0
        self.level = 1
        self.achievements = []
        self.daily_actions = []
        self.streak = 0
        self.last_action = None
        
    def add_points(self, points: int, action_type: str):
        """Adiciona pontos de virtude."""
        self.points += points
        self.daily_actions.append({
            "type": action_type,
            "points": points,
            "timestamp": datetime.now()
        })
        self._check_level_up()
        self._check_achievements()
        
    def _check_level_up(self):
        """Verifica e realiza level up se necessário."""
        new_level = 1 + (self.points // 1000)  # Level up a cada 1000 pontos
        if new_level > self.level:
            self.achievements.append({
                "type": "level_up",
                "from": self.level,
                "to": new_level,
                "timestamp": datetime.now()
            })
            self.level = new_level
            
    def _check_achievements(self):
        """Verifica e concede conquistas."""
        # Implementar lógica de conquistas
        pass

class EthicalRanking:
    def __init__(self, ethics_shield: EthicsShield):
        """Inicializa o sistema de ranking ético."""
        self.ethics_shield = ethics_shield
        self.rankings = {}
        self.daily_challenges = []
        self.leaderboards = {
            "global": [],
            "daily": [],
            "weekly": [],
            "virtude": []
        }
        self.achievements = {
            "guardian": {
                "name": "Guardião da Ética",
                "description": "Protegeu o sistema contra 10 ameaças",
                "points": 500
            },
            "virtuous": {
                "name": "Virtuoso",
                "description": "Manteve score ético acima de 0.9 por 7 dias",
                "points": 1000
            },
            "consistent": {
                "name": "Consistente",
                "description": "Completou ações éticas por 30 dias seguidos",
                "points": 2000
            },
            "mentor": {
                "name": "Mentor",
                "description": "Ajudou outros a melhorarem seus scores éticos",
                "points": 1500
            }
        }
        
    async def process_action(self, action: EthicalAction) -> Dict:
        """Processa uma ação e atualiza rankings."""
        try:
            # Valida ação
            is_ethical = await self.ethics_shield.validate_action(action)
            
            # Gera ID anônimo
            anonymous_id = self._generate_anonymous_id(action)
            
            # Inicializa ou recupera pontos de virtude
            if anonymous_id not in self.rankings:
                self.rankings[anonymous_id] = {
                    "virtude_points": VirtudePoints(),
                    "ethical_score": 0.0,
                    "total_actions": 0,
                    "achievements": [],
                    "last_update": None
                }
                
            ranking = self.rankings[anonymous_id]
            
            # Atualiza estatísticas
            ranking["total_actions"] += 1
            ranking["ethical_score"] = (
                (ranking["ethical_score"] * (ranking["total_actions"] - 1) +
                 action.ethical_score) / ranking["total_actions"]
            )
            
            # Calcula pontos
            points = self._calculate_points(action, is_ethical)
            
            # Adiciona pontos
            ranking["virtude_points"].add_points(points, action.action_type)
            
            # Atualiza timestamp
            ranking["last_update"] = datetime.now()
            
            # Verifica conquistas
            await self._check_achievements(anonymous_id, action)
            
            # Atualiza leaderboards
            await self._update_leaderboards()
            
            return {
                "success": True,
                "points_earned": points,
                "new_achievements": ranking["achievements"],
                "current_level": ranking["virtude_points"].level,
                "ethical_score": ranking["ethical_score"]
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar ação para ranking: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _generate_anonymous_id(self, action: EthicalAction) -> str:
        """Gera ID anônimo baseado na ação."""
        action_data = f"{action.action_type}:{json.dumps(action.context)}"
        return hashlib.sha256(action_data.encode()).hexdigest()[:8]
        
    def _calculate_points(self, action: EthicalAction, is_ethical: bool) -> int:
        """Calcula pontos baseado na ação e validação ética."""
        base_points = 10
        
        if not is_ethical:
            return 0
            
        # Bônus por score ético alto
        if action.ethical_score >= 0.9:
            base_points += 20
        elif action.ethical_score >= 0.8:
            base_points += 10
            
        # Bônus por ações complexas
        if len(action.validation_chain) > 3:
            base_points += 15
            
        # Bônus por streak
        ranking = self.rankings[self._generate_anonymous_id(action)]
        if ranking["virtude_points"].streak > 0:
            base_points *= (1 + (ranking["virtude_points"].streak * 0.1))
            
        return int(base_points)
        
    async def _check_achievements(self, anonymous_id: str, action: EthicalAction):
        """Verifica e concede conquistas."""
        ranking = self.rankings[anonymous_id]
        
        # Guardião da Ética
        if (ranking["total_actions"] >= 10 and
            ranking["ethical_score"] >= 0.8):
            self._grant_achievement(anonymous_id, "guardian")
            
        # Virtuoso
        if (ranking["ethical_score"] >= 0.9 and
            ranking["virtude_points"].streak >= 7):
            self._grant_achievement(anonymous_id, "virtuous")
            
        # Consistente
        if ranking["virtude_points"].streak >= 30:
            self._grant_achievement(anonymous_id, "consistent")
            
    def _grant_achievement(self, anonymous_id: str, achievement_id: str):
        """Concede uma conquista."""
        ranking = self.rankings[anonymous_id]
        
        if achievement_id not in ranking["achievements"]:
            achievement = self.achievements[achievement_id]
            ranking["achievements"].append({
                "id": achievement_id,
                "name": achievement["name"],
                "timestamp": datetime.now()
            })
            ranking["virtude_points"].add_points(
                achievement["points"],
                "achievement"
            )
            
    async def _update_leaderboards(self):
        """Atualiza os leaderboards."""
        # Global
        self.leaderboards["global"] = sorted(
            self.rankings.items(),
            key=lambda x: x[1]["virtude_points"].points,
            reverse=True
        )[:100]
        
        # Diário
        today = datetime.now().date()
        daily_rankings = [
            (id, data) for id, data in self.rankings.items()
            if data["last_update"].date() == today
        ]
        self.leaderboards["daily"] = sorted(
            daily_rankings,
            key=lambda x: x[1]["virtude_points"].points,
            reverse=True
        )[:50]
        
        # Semanal
        # Implementar lógica semanal
        
        # Virtude
        self.leaderboards["virtude"] = sorted(
            self.rankings.items(),
            key=lambda x: x[1]["ethical_score"],
            reverse=True
        )[:100]
        
    def get_leaderboard(self, board_type: str = "global", limit: int = 10) -> List[Dict]:
        """Retorna um leaderboard específico."""
        if board_type not in self.leaderboards:
            return []
            
        return [
            {
                "position": i + 1,
                "anonymous_id": id,
                "level": data["virtude_points"].level,
                "points": data["virtude_points"].points,
                "ethical_score": round(data["ethical_score"], 2)
            }
            for i, (id, data) in enumerate(self.leaderboards[board_type][:limit])
        ]
        
    def get_player_stats(self, anonymous_id: str) -> Optional[Dict]:
        """Retorna estatísticas de um jogador específico."""
        if anonymous_id not in self.rankings:
            return None
            
        ranking = self.rankings[anonymous_id]
        
        return {
            "level": ranking["virtude_points"].level,
            "points": ranking["virtude_points"].points,
            "ethical_score": round(ranking["ethical_score"], 2),
            "total_actions": ranking["total_actions"],
            "achievements": ranking["achievements"],
            "streak": ranking["virtude_points"].streak
        }
        
    async def generate_daily_challenges(self):
        """Gera desafios diários."""
        self.daily_challenges = [
            {
                "id": "ethical_guardian",
                "name": "Guardião Ético",
                "description": "Mantenha score ético acima de 0.8 por 24h",
                "points": 100
            },
            {
                "id": "virtuous_actions",
                "name": "Ações Virtuosas",
                "description": "Complete 5 ações com score ético > 0.9",
                "points": 150
            },
            {
                "id": "consistent_ethics",
                "name": "Ética Consistente",
                "description": "Mantenha streak por 24h",
                "points": 200
            }
        ]
        
    def get_daily_challenges(self) -> List[Dict]:
        """Retorna desafios diários ativos."""
        return self.daily_challenges 