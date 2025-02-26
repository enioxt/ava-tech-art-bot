"""
ETHIK Token Integration Module
Manages the integration between ethical actions and token rewards
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

from ..token.ethik_token import EthikToken, EthikTransaction
from .source_validator import SourceValidator
from .perplexity_validator import PerplexityValidator

logger = logging.getLogger(__name__)

class EthikIntegration:
    """Manages integration between ethical system and $ETHIK token"""
    
    def __init__(
        self,
        token: EthikToken,
        source_validator: SourceValidator,
        perplexity_validator: PerplexityValidator
    ):
        self.token = token
        self.source_validator = source_validator
        self.perplexity_validator = perplexity_validator
        self.action_log = []
        
    async def process_ethical_action(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict
    ) -> Dict:
        """
        Process an ethical action and reward tokens if appropriate
        
        Args:
            user_id: Unique identifier of the user
            action_type: Type of action (e.g. code_contribution, review)
            action_data: Data specific to the action type
            
        Returns:
            Dict containing action results and any rewards
        """
        try:
            # Validate action
            source_score = await self.source_validator.validate_action(
                action_type=action_type,
                action_data=action_data
            )
            
            perplexity_score = await self.perplexity_validator.validate_action(
                action_type=action_type,
                action_data=action_data
            )
            
            # Calculate ethical score (0-1)
            ethical_score = (source_score + perplexity_score) / 2
            
            # Log action
            action_log_entry = {
                "user_id": user_id,
                "action_type": action_type,
                "action_data": action_data,
                "ethical_score": ethical_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.action_log.append(action_log_entry)
            
            # Only reward if ethical score is sufficient
            if ethical_score >= 0.7:
                # Calculate reward based on score and action type
                reward_amount = self._calculate_reward(
                    ethical_score=ethical_score,
                    action_type=action_type,
                    action_data=action_data
                )
                
                # Process reward
                reward_tx = await self.token.reward_ethical_action(
                    user_id=user_id,
                    amount=reward_amount,
                    metadata={
                        "action_type": action_type,
                        "ethical_score": ethical_score,
                        "action_data": action_data
                    }
                )
                
                action_log_entry["reward"] = {
                    "amount": reward_amount,
                    "tx_hash": reward_tx.tx_hash
                }
                
                return {
                    "success": True,
                    "ethical_score": ethical_score,
                    "reward": {
                        "amount": reward_amount,
                        "tx_hash": reward_tx.tx_hash
                    }
                }
            
            return {
                "success": True,
                "ethical_score": ethical_score,
                "reward": None,
                "message": "Ethical score below reward threshold"
            }
            
        except Exception as e:
            logger.error(f"Error processing ethical action: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _calculate_reward(
        self,
        ethical_score: float,
        action_type: str,
        action_data: Dict
    ) -> Decimal:
        """Calculate reward amount based on ethical score and action metrics"""
        
        # Base reward multiplied by ethical score
        base_reward = Decimal('1.0')
        score_multiplier = Decimal(str(ethical_score))
        
        # Additional multipliers based on action type and metrics
        action_multiplier = Decimal('1.0')
        
        if action_type == "code_contribution":
            # Reward based on impact (files changed, lines modified)
            files_changed = action_data.get("files_changed", 0)
            lines_added = action_data.get("lines_added", 0)
            lines_removed = action_data.get("lines_removed", 0)
            
            impact_score = (files_changed + (lines_added + lines_removed) / 100) / 10
            action_multiplier = Decimal(str(min(impact_score, 5.0)))
            
        elif action_type == "review":
            # Reward based on review depth and quality
            comments = action_data.get("comments", 0)
            suggestions = action_data.get("suggestions", 0)
            
            review_score = (comments + suggestions) / 5
            action_multiplier = Decimal(str(min(review_score, 3.0)))
            
        # Calculate final reward
        reward = base_reward * score_multiplier * action_multiplier
        
        # Cap reward at maximum amount
        return min(reward, Decimal('10.0'))
        
    async def get_user_stats(self, user_id: str) -> Dict:
        """Get statistics for a specific user"""
        
        user_actions = [
            action for action in self.action_log
            if action["user_id"] == user_id
        ]
        
        if not user_actions:
            return {
                "user_id": user_id,
                "total_actions": 0,
                "average_ethical_score": 0,
                "total_rewards": Decimal('0'),
                "token_balance": self.token.get_balance(user_id)
            }
            
        total_score = sum(action["ethical_score"] for action in user_actions)
        total_rewards = sum(
            Decimal(str(action.get("reward", {}).get("amount", 0)))
            for action in user_actions
        )
        
        return {
            "user_id": user_id,
            "total_actions": len(user_actions),
            "average_ethical_score": total_score / len(user_actions),
            "total_rewards": total_rewards,
            "token_balance": self.token.get_balance(user_id)
        }
        
    async def get_global_stats(self) -> Dict:
        """Get global statistics for the system"""
        
        if not self.action_log:
            return {
                "total_actions": 0,
                "average_ethical_score": 0,
                "total_users": 0,
                "total_rewards": Decimal('0')
            }
            
        unique_users = len(set(action["user_id"] for action in self.action_log))
        total_score = sum(action["ethical_score"] for action in self.action_log)
        total_rewards = sum(
            Decimal(str(action.get("reward", {}).get("amount", 0)))
            for action in self.action_log
        )
        
        return {
            "total_actions": len(self.action_log),
            "average_ethical_score": total_score / len(self.action_log),
            "total_users": unique_users,
            "total_rewards": total_rewards,
            "rewards_stats": await self.token.get_rewards_stats()
        }
        
    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get leaderboard of most ethical users"""
        
        # Get unique user IDs
        user_ids = set(action["user_id"] for action in self.action_log)
        
        # Get stats for each user
        user_stats = []
        for user_id in user_ids:
            stats = await self.get_user_stats(user_id)
            user_stats.append(stats)
            
        # Sort by average ethical score and total rewards
        sorted_stats = sorted(
            user_stats,
            key=lambda x: (x["average_ethical_score"], x["total_rewards"]),
            reverse=True
        )
        
        return sorted_stats[:limit] 