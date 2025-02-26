import os
import logging
from web3 import Web3
from eth_account import Account
from datetime import datetime
from dotenv import load_dotenv
import json
from typing import Dict, List, Optional
import aiohttp
from secure_key_manager import key_manager

# Configuração de logging
logger = logging.getLogger("✨wallet-manager✨")

# Carrega variáveis de ambiente
load_dotenv()

class WalletManager:
    """Gerenciador de Carteiras e Tokens $eTHik"""
    
    def __init__(self):
        """Inicializa o gerenciador de carteiras."""
        # Configuração Web3
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("ETH_NODE_URL", "http://localhost:8545")))
        
        # Carrega contrato $eTHik
        self.ethik_contract = self._load_contract(
            os.getenv("ETHIK_TOKEN_ADDRESS"),
            os.getenv("ETHIK_CONTRACT_ABI")
        )
        
        # Carteira principal da AVA (sem private key)
        self.ava_wallet = {
            "address": os.getenv("AVA_WALLET_ADDRESS"),
            "key_id": None,  # Será definido quando a chave for fornecida
            "access_token": None
        }
        
        # Cache de carteiras dos usuários (sem private keys)
        self.user_wallets: Dict[int, Dict] = {}
        
        # Regras éticas e recompensas
        self.ethics_rules = {
            "basic": {
                "description": "Seguir princípios éticos básicos",
                "reward": 1,  # 1 $eTHik
                "requirements": ["respeito", "honestidade", "transparência"]
            },
            "intermediate": {
                "description": "Contribuir para discussões éticas",
                "reward": 5,  # 5 $eTHik
                "requirements": ["participação", "argumentação", "colaboração"]
            },
            "advanced": {
                "description": "Propor melhorias éticas",
                "reward": 10,  # 10 $eTHik
                "requirements": ["inovação", "impacto", "sustentabilidade"]
            }
        }
        
        # Métricas de distribuição
        self.distribution_metrics = {
            "total_distributed": 0,
            "total_users": 0,
            "last_distribution": None
        }

    def _load_contract(self, address: str, abi_path: str) -> Optional[object]:
        """Carrega contrato Ethereum."""
        try:
            with open(abi_path) as f:
                contract_abi = json.load(f)
            return self.w3.eth.contract(address=address, abi=contract_abi)
        except Exception as e:
            logger.error(f"❌ Erro ao carregar contrato: {str(e)}")
            return None

    async def set_ava_private_key(self, private_key: str) -> bool:
        """
        Define a chave privada da carteira AVA de forma segura.
        
        Args:
            private_key (str): Chave privada da carteira AVA
            
        Returns:
            bool: True se chave foi armazenada com sucesso
        """
        try:
            # Inicializa sistema de chaves se necessário
            if not key_manager.initialized:
                await key_manager.initialize()
            
            # Armazena chave de forma segura
            key_data = await key_manager.store_private_key(
                key_id=f"ava_wallet_{datetime.now().timestamp()}",
                private_key=private_key,
                ttl_hours=24  # Chave expira em 24 horas
            )
            
            if key_data:
                self.ava_wallet.update({
                    "key_id": key_data["key_id"],
                    "access_token": key_data["access_token"]
                })
                logger.info("✨ Chave privada da AVA armazenada com sucesso")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao definir chave privada: {str(e)}")
            return False

    async def create_user_wallet(self, user_id: int) -> Dict:
        """
        Cria uma nova carteira para um usuário.
        
        Args:
            user_id (int): ID do usuário Telegram
            
        Returns:
            Dict: Dados da carteira criada
        """
        try:
            # Cria nova conta
            account = Account.create()
            
            # Armazena dados da carteira (sem private key)
            wallet_data = {
                "address": account.address,
                "balance": 0,
                "created_at": datetime.now(),
                "last_reward": None
            }
            
            # Armazena chave privada de forma segura
            key_data = await key_manager.store_private_key(
                key_id=f"user_{user_id}_{datetime.now().timestamp()}",
                private_key=account.key.hex(),
                ttl_hours=1  # Chave expira em 1 hora
            )
            
            if key_data:
                wallet_data.update({
                    "key_id": key_data["key_id"],
                    "access_token": key_data["access_token"]
                })
            
            self.user_wallets[user_id] = wallet_data
            self.distribution_metrics["total_users"] += 1
            
            logger.info(f"✨ Carteira criada para usuário {user_id}")
            
            # Retorna dados sem informações sensíveis
            return {
                "address": wallet_data["address"],
                "created_at": wallet_data["created_at"]
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar carteira: {str(e)}")
            return {}

    async def get_wallet_balance(self, address: str) -> float:
        """
        Obtém o saldo de $eTHik de uma carteira.
        
        Args:
            address (str): Endereço da carteira
            
        Returns:
            float: Saldo em $eTHik
        """
        try:
            balance = await self.ethik_contract.functions.balanceOf(address).call()
            return self.w3.from_wei(balance, 'ether')
        except Exception as e:
            logger.error(f"❌ Erro ao obter saldo: {str(e)}")
            return 0.0

    async def distribute_reward(self, user_id: int, rule_level: str) -> bool:
        """
        Distribui recompensa em $eTHik para um usuário.
        
        Args:
            user_id (int): ID do usuário
            rule_level (str): Nível da regra ética completada
            
        Returns:
            bool: True se distribuição foi bem sucedida
        """
        try:
            # Verifica se AVA tem chave privada configurada
            if not self.ava_wallet.get("key_id"):
                logger.warning("⚠️ Chave privada da AVA não configurada")
                return False
                
            if user_id not in self.user_wallets:
                await self.create_user_wallet(user_id)
                
            wallet = self.user_wallets[user_id]
            reward = self.ethics_rules[rule_level]["reward"]
            
            # Recupera chave privada da AVA
            ava_private_key = await key_manager.get_private_key(
                self.ava_wallet["key_id"],
                self.ava_wallet["access_token"]
            )
            
            if not ava_private_key:
                logger.error("❌ Não foi possível recuperar chave privada da AVA")
                return False
            
            # Prepara transação
            transaction = await self.ethik_contract.functions.transfer(
                wallet["address"],
                self.w3.to_wei(reward, 'ether')
            ).build_transaction({
                'from': self.ava_wallet["address"],
                'nonce': self.w3.eth.get_transaction_count(self.ava_wallet["address"])
            })
            
            # Assina e envia transação
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                ava_private_key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Atualiza métricas
            self.distribution_metrics["total_distributed"] += reward
            self.distribution_metrics["last_distribution"] = datetime.now()
            wallet["last_reward"] = datetime.now()
            
            logger.info(f"✨ Distribuídos {reward} $eTHik para usuário {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na distribuição: {str(e)}")
            return False

    async def get_user_ethics_status(self, user_id: int) -> Dict:
        """
        Obtém status ético e de recompensas do usuário.
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            Dict: Status do usuário
        """
        try:
            if user_id not in self.user_wallets:
                return {"error": "Usuário não possui carteira"}
                
            wallet = self.user_wallets[user_id]
            balance = await self.get_wallet_balance(wallet["address"])
            
            return {
                "address": wallet["address"],
                "balance": balance,
                "last_reward": wallet["last_reward"],
                "created_at": wallet["created_at"]
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter status: {str(e)}")
            return {"error": str(e)}

    async def get_distribution_metrics(self) -> Dict:
        """
        Obtém métricas de distribuição de tokens.
        
        Returns:
            Dict: Métricas atuais
        """
        return {
            "total_distributed": self.distribution_metrics["total_distributed"],
            "total_users": self.distribution_metrics["total_users"],
            "last_distribution": self.distribution_metrics["last_distribution"],
            "active_rules": list(self.ethics_rules.keys())
        }

# Instância global do gerenciador de carteiras
wallet_manager = WalletManager() 