#!/usr/bin/env python3
"""
CORE System Runner
Initializes and runs the CORE system with $ETHIK token integration
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from ava_mind.token.ethik_token import EthikToken, EthikTransaction
from ava_mind.ethics.source_validator import SourceValidator
from ava_mind.ethics.perplexity_validator import PerplexityValidator
from ava_mind.ethics.ethik_integration import EthikIntegration
from ava_mind.web.server import run_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('core_system.log')
    ]
)

logger = logging.getLogger(__name__)

class CoreSystem:
    """Main CORE system class that initializes and manages all components"""
    
    def __init__(self):
        self.token = EthikToken()
        self.source_validator = SourceValidator()
        self.perplexity_validator = PerplexityValidator()
        self.ethik_integration = EthikIntegration(
            token=self.token,
            source_validator=self.source_validator,
            perplexity_validator=self.perplexity_validator
        )
        self.data_dir = Path('data')
        self.logs_dir = Path('logs')
        
    async def setup(self):
        """Initialize the system"""
        logger.info("Setting up CORE system...")
        
        # Create necessary directories
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup PIX gateway
        await self.token.setup_pix_gateway()
        
        # Initialize validators
        await self.source_validator.initialize()
        await self.perplexity_validator.initialize()
        
        logger.info("CORE system setup complete")
        
    async def process_action(self, user_id: str, action_type: str, action_data: Dict) -> Dict:
        """Process a user action through the ethical system"""
        try:
            result = await self.ethik_integration.process_ethical_action(
                user_id=user_id,
                action_type=action_type,
                action_data=action_data
            )
            
            logger.info(f"Processed action for user {user_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing action: {e}")
            raise
            
    async def get_system_status(self) -> Dict:
        """Get current system status including statistics"""
        try:
            global_stats = await self.ethik_integration.get_global_stats()
            leaderboard = await self.ethik_integration.get_leaderboard(limit=10)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "global_stats": global_stats,
                "leaderboard": leaderboard,
                "token_stats": {
                    "total_supply": self.token.get_total_supply(),
                    "rewards_pool": self.token.get_rewards_pool(),
                    "active_users": len(await self.token.get_all_holders())
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            raise

async def main():
    """Main entry point for the CORE system"""
    try:
        # Initialize system
        system = CoreSystem()
        await system.setup()
        
        # Process example action
        example_action = {
            "user_id": "example_user",
            "action_type": "code_contribution",
            "action_data": {
                "repository": "core-project",
                "commit_hash": "abc123",
                "files_changed": 3,
                "lines_added": 100,
                "lines_removed": 50
            }
        }
        
        action_result = await system.process_action(
            example_action["user_id"],
            example_action["action_type"],
            example_action["action_data"]
        )
        
        logger.info(f"Example action result: {action_result}")
        
        # Get system status
        status = await system.get_system_status()
        logger.info(f"System status: {status}")
        
        # Start web server
        await run_server(system)
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down CORE system...")
        sys.exit(0) 