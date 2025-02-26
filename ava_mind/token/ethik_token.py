"""
ETHIK Token Module
Manages the $ETHIK token, transactions and rewards
"""

import os
import json
import hashlib
import logging
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class TransactionType(Enum):
    """Types of token transactions"""
    MINT = "mint"
    TRANSFER = "transfer"
    REWARD = "reward"
    PIX_PURCHASE = "pix_purchase"

@dataclass
class EthikTransaction:
    """Represents a token transaction"""
    tx_type: TransactionType
    amount: Decimal
    from_address: Optional[str]
    to_address: str
    timestamp: datetime
    metadata: Dict
    tx_hash: Optional[str] = None
    
    def __post_init__(self):
        """Calculate transaction hash after initialization"""
        if not self.tx_hash:
            self.tx_hash = self._calculate_hash()
            
    def _calculate_hash(self) -> str:
        """Calculate unique hash for transaction"""
        data = {
            "type": self.tx_type.value,
            "amount": str(self.amount),
            "from": self.from_address or "",
            "to": self.to_address,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
        
        json_data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_data.encode()).hexdigest()

class EthikToken:
    """Manages the $ETHIK token and its transactions"""
    
    def __init__(self):
        self.balances: Dict[str, Decimal] = {}
        self.transactions: List[EthikTransaction] = []
        self.rewards_pool = Decimal('1000000')  # Initial rewards pool
        self.total_supply = Decimal('10000000')  # Total token supply
        self.pix_gateway = None
        self.data_dir = os.path.join(os.getcwd(), 'data', 'ethik')
        os.makedirs(self.data_dir, exist_ok=True)
        
    async def setup_pix_gateway(self):
        """Setup PIX payment gateway"""
        # TODO: Implement PIX gateway integration
        logger.info("PIX gateway setup placeholder")
        
    def get_balance(self, address: str) -> Decimal:
        """Get token balance for an address"""
        return self.balances.get(address, Decimal('0'))
        
    async def process_pix_purchase(
        self,
        user_id: str,
        pix_amount: Decimal,
        pix_id: str
    ) -> Optional[EthikTransaction]:
        """Process token purchase via PIX"""
        try:
            # Validate PIX payment
            if not await self._validate_pix_payment(pix_id, pix_amount):
                raise ValueError("Invalid PIX payment")
                
            # Calculate token amount
            token_amount = self._calculate_token_amount(pix_amount)
            
            # Create and process transaction
            tx = EthikTransaction(
                tx_type=TransactionType.PIX_PURCHASE,
                amount=token_amount,
                from_address=None,
                to_address=user_id,
                timestamp=datetime.utcnow(),
                metadata={
                    "pix_amount": str(pix_amount),
                    "pix_id": pix_id
                }
            )
            
            await self._process_transaction(tx)
            return tx
            
        except Exception as e:
            logger.error(f"Error processing PIX purchase: {e}")
            return None
            
    async def reward_ethical_action(
        self,
        user_id: str,
        amount: Decimal,
        metadata: Dict
    ) -> Optional[EthikTransaction]:
        """Reward user for ethical action"""
        try:
            if amount > self.rewards_pool:
                raise ValueError("Insufficient rewards pool")
                
            tx = EthikTransaction(
                tx_type=TransactionType.REWARD,
                amount=amount,
                from_address=None,
                to_address=user_id,
                timestamp=datetime.utcnow(),
                metadata=metadata
            )
            
            await self._process_transaction(tx)
            self.rewards_pool -= amount
            
            return tx
            
        except Exception as e:
            logger.error(f"Error processing reward: {e}")
            return None
            
    async def _process_transaction(self, tx: EthikTransaction):
        """Process a transaction and update balances"""
        
        # Update sender balance if applicable
        if tx.from_address:
            sender_balance = self.get_balance(tx.from_address)
            if sender_balance < tx.amount:
                raise ValueError("Insufficient balance")
            self.balances[tx.from_address] = sender_balance - tx.amount
            
        # Update receiver balance
        receiver_balance = self.get_balance(tx.to_address)
        self.balances[tx.to_address] = receiver_balance + tx.amount
        
        # Record transaction
        self.transactions.append(tx)
        
        # Save transaction to disk
        self._save_transaction(tx)
        
    def _save_transaction(self, tx: EthikTransaction):
        """Save transaction to disk"""
        tx_data = {
            "type": tx.tx_type.value,
            "amount": str(tx.amount),
            "from": tx.from_address,
            "to": tx.to_address,
            "timestamp": tx.timestamp.isoformat(),
            "metadata": tx.metadata,
            "hash": tx.tx_hash
        }
        
        filename = os.path.join(
            self.data_dir,
            f"tx_{tx.timestamp.strftime('%Y%m%d_%H%M%S')}_{tx.tx_hash[:8]}.json"
        )
        
        with open(filename, 'w') as f:
            json.dump(tx_data, f, indent=2)
            
    async def _validate_pix_payment(self, pix_id: str, amount: Decimal) -> bool:
        """Validate PIX payment"""
        # TODO: Implement PIX payment validation
        logger.info(f"Validating PIX payment {pix_id} for {amount}")
        return True
        
    def _calculate_token_amount(self, pix_amount: Decimal) -> Decimal:
        """Calculate token amount from PIX amount"""
        # Example: 1 BRL = 10 $ETHIK
        return pix_amount * Decimal('10')
        
    def get_transaction_history(self, address: str) -> List[EthikTransaction]:
        """Get transaction history for an address"""
        return [
            tx for tx in self.transactions
            if tx.from_address == address or tx.to_address == address
        ]
        
    async def get_rewards_stats(self) -> Dict:
        """Get statistics about rewards"""
        reward_txs = [
            tx for tx in self.transactions
            if tx.tx_type == TransactionType.REWARD
        ]
        
        total_rewards = sum(tx.amount for tx in reward_txs)
        unique_recipients = len(set(tx.to_address for tx in reward_txs))
        
        return {
            "total_rewards_distributed": total_rewards,
            "rewards_pool_remaining": self.rewards_pool,
            "unique_recipients": unique_recipients,
            "total_reward_transactions": len(reward_txs)
        }
        
    async def get_all_holders(self) -> List[str]:
        """Get list of all token holders"""
        return [
            address
            for address, balance in self.balances.items()
            if balance > 0
        ]
        
    def get_total_supply(self) -> Decimal:
        """Get total token supply"""
        return self.total_supply
        
    def get_rewards_pool(self) -> Decimal:
        """Get current rewards pool balance"""
        return self.rewards_pool 