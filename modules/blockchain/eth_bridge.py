#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Ethereum Blockchain Bridge
Versão: 1.1.0

Ponte para integração com blockchain Ethereum.
Suporte a distribuição de valor ético e mecanismos de governança.
"""

import os
import json
import logging
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainBridge:
    """
    Ponte para blockchain Ethereum que permite:
    - Armazenar hashes de dados importantes
    - Registrar ações do sistema
    - Verificar integridade de dados
    - Distribuir valor através de tokens
    - Facilitar governança ética descentralizada
    """
    
    def __init__(self, network="testnet", config_path="config/blockchain_config.json"):
        self.network = network
        self.config_path = config_path
        self.web3 = None
        self.contract = None
        self.account = None
        self.simulation_mode = not WEB3_AVAILABLE
        self.value_distribution_enabled = False
        self.governance_enabled = False
        
        self.data_dir = Path("data/blockchain")
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        self.transactions_file = self.data_dir / "transactions.json"
        self.value_ledger_file = self.data_dir / "value_ledger.json"
        self.governance_file = self.data_dir / "governance.json"
        
        # Inicializa arquivos se não existirem
        if not self.transactions_file.exists():
            with open(self.transactions_file, 'w', encoding='utf-8') as f:
                json.dump({"transactions": []}, f, indent=2)
                
        if not self.value_ledger_file.exists():
            with open(self.value_ledger_file, 'w', encoding='utf-8') as f:
                json.dump({"accounts": {}, "transactions": []}, f, indent=2)
                
        if not self.governance_file.exists():
            with open(self.governance_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "proposals": [],
                    "votes": {},
                    "settings": {
                        "voting_period_days": 7,
                        "approval_threshold": 0.66
                    }
                }, f, indent=2)
        
        self.load_config()
        self.connect()
        
    def load_config(self):
        """Carrega configurações da blockchain"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "networks": {
                        "mainnet": "https://mainnet.infura.io/v3/YOUR_INFURA_KEY",
                        "testnet": "https://sepolia.infura.io/v3/YOUR_INFURA_KEY",
                        "local": "http://localhost:8545"
                    },
                    "contract_address": "",
                    "abi": [],
                    "simulation_fallback": True,
                    "value_distribution": {
                        "enabled": True,
                        "token_name": "EthicValue",
                        "token_symbol": "ETV",
                        "initial_supply": 1000000,
                        "ethical_actions": {
                            "code_contribution": 10,
                            "documentation": 5,
                            "bug_report": 3,
                            "ethical_decision": 15,
                            "community_support": 7
                        }
                    },
                    "governance": {
                        "enabled": True,
                        "proposal_threshold": 100,
                        "voting_period_days": 7,
                        "execution_delay_days": 2
                    }
                }
                
                config_file.parent.mkdir(exist_ok=True, parents=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2)
                    
            # Extrair configurações específicas
            self.value_distribution_enabled = self.config.get("value_distribution", {}).get("enabled", False)
            self.governance_enabled = self.config.get("governance", {}).get("enabled", False)
            
        except Exception as e:
            logger.error(f"Erro ao carregar configuração da blockchain: {e}")
            
    def connect(self):
        """Conecta à rede blockchain ou ativa modo de simulação"""
        if not WEB3_AVAILABLE:
            logger.warning("Pacote web3 não disponível. Operando em modo de simulação.")
            self.simulation_mode = True
            return
            
        try:
            # Tenta conectar à rede especificada
            provider_url = self.config["networks"].get(self.network)
            if not provider_url:
                logger.warning(f"URL do provedor para rede {self.network} não encontrada. Operando em modo de simulação.")
                self.simulation_mode = True
                return
                
            self.web3 = Web3(Web3.HTTPProvider(provider_url))
            if not self.web3.is_connected():
                logger.warning("Não foi possível conectar à blockchain. Operando em modo de simulação.")
                self.simulation_mode = True
                return
                
            logger.info(f"Conectado à rede blockchain: {self.network}")
            self.simulation_mode = False
            
            # Carrega contrato se o endereço estiver especificado
            if self.config.get("contract_address") and self.config.get("abi"):
                contract_address = self.web3.to_checksum_address(self.config["contract_address"])
                self.contract = self.web3.eth.contract(address=contract_address, abi=self.config["abi"])
                logger.info(f"Contrato carregado: {contract_address}")
                
        except Exception as e:
            logger.error(f"Erro ao conectar à blockchain: {e}")
            logger.warning("Operando em modo de simulação.")
            self.simulation_mode = True
    
    def _generate_tx_hash(self) -> str:
        """Gera um hash de transação simulado"""
        return f"0x{hashlib.sha256(str(time.time()).encode()).hexdigest()}"
    
    def _save_transaction(self, tx_type: str, data: Dict, tx_hash: str):
        """Salva uma transação no registro local"""
        try:
            with open(self.transactions_file, 'r', encoding='utf-8') as f:
                transactions = json.load(f)
                
            tx_record = {
                "tx_hash": tx_hash,
                "type": tx_type,
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "block_number": 0 if self.simulation_mode else self.web3.eth.block_number
            }
            
            transactions["transactions"].append(tx_record)
            
            with open(self.transactions_file, 'w', encoding='utf-8') as f:
                json.dump(transactions, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao salvar transação: {e}")
    
    def store_hash(self, data_hash: str, metadata: Dict) -> Optional[str]:
        """
        Armazena um hash na blockchain ou no sistema de simulação
        Retorna o transaction hash se bem-sucedido
        """
        if self.simulation_mode:
            # Modo de simulação - armazena localmente
            tx_hash = self._generate_tx_hash()
            self._save_transaction("store_hash", {
                "data_hash": data_hash,
                "metadata": metadata
            }, tx_hash)
            
            logger.info(f"Hash armazenado (simulação): {data_hash[:10]}... - TX: {tx_hash[:10]}...")
            return tx_hash
        else:
            # Implementação real com Web3
            # Este é um placeholder para quando tivermos um contrato real implantado
            tx_hash = self._generate_tx_hash()
            self._save_transaction("store_hash", {
                "data_hash": data_hash,
                "metadata": metadata
            }, tx_hash)
            
            logger.info(f"Hash armazenado: {data_hash[:10]}... - TX: {tx_hash[:10]}...")
            return tx_hash
    
    def verify_hash(self, data_hash: str) -> bool:
        """Verifica se um hash existe na blockchain ou no sistema de simulação"""
        try:
            with open(self.transactions_file, 'r', encoding='utf-8') as f:
                transactions = json.load(f)
                
            for tx in transactions["transactions"]:
                if tx["type"] == "store_hash" and tx["data"]["data_hash"] == data_hash:
                    logger.info(f"Hash verificado: {data_hash[:10]}...")
                    return True
                    
            logger.info(f"Hash não encontrado: {data_hash[:10]}...")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar hash: {e}")
            return False
    
    def _update_value_ledger(self, recipient: str, amount: float, reason: str):
        """Atualiza o ledger de valor ético"""
        try:
            with open(self.value_ledger_file, 'r', encoding='utf-8') as f:
                ledger = json.load(f)
                
            # Atualiza ou cria conta do recipient
            if recipient not in ledger["accounts"]:
                ledger["accounts"][recipient] = {
                    "balance": 0,
                    "last_updated": datetime.now().isoformat()
                }
                
            # Atualiza saldo
            ledger["accounts"][recipient]["balance"] += amount
            ledger["accounts"][recipient]["last_updated"] = datetime.now().isoformat()
            
            # Registra transação
            tx_record = {
                "recipient": recipient,
                "amount": amount,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "tx_hash": self._generate_tx_hash()
            }
            
            ledger["transactions"].append(tx_record)
            
            # Salva ledger
            with open(self.value_ledger_file, 'w', encoding='utf-8') as f:
                json.dump(ledger, f, indent=2)
                
            return tx_record["tx_hash"]
            
        except Exception as e:
            logger.error(f"Erro ao atualizar ledger de valor: {e}")
            return None
    
    def distribute_value(self, recipient: str, amount: float, reason: str = None) -> Optional[str]:
        """Distribui valor (tokens) para um recipient"""
        if not self.value_distribution_enabled:
            logger.warning("Distribuição de valor não está habilitada")
            return None
            
        if self.simulation_mode:
            # Modo de simulação - atualiza ledger local
            tx_hash = self._update_value_ledger(recipient, amount, reason or "distribuição de valor")
            
            if tx_hash:
                logger.info(f"Valor distribuído (simulação): {amount} para {recipient} - TX: {tx_hash[:10]}...")
                
            return tx_hash
        else:
            # Implementação real com Web3
            # Este é um placeholder para quando tivermos um contrato real implantado
            tx_hash = self._update_value_ledger(recipient, amount, reason or "distribuição de valor")
            
            if tx_hash:
                logger.info(f"Valor distribuído: {amount} para {recipient} - TX: {tx_hash[:10]}...")
                
            return tx_hash
    
    def get_account_balance(self, account_id: str) -> float:
        """Retorna o saldo de valor ético de uma conta"""
        try:
            with open(self.value_ledger_file, 'r', encoding='utf-8') as f:
                ledger = json.load(f)
                
            if account_id in ledger["accounts"]:
                return ledger["accounts"][account_id]["balance"]
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Erro ao consultar saldo: {e}")
            return 0.0
    
    def create_governance_proposal(self, 
                                  proposer: str, 
                                  title: str, 
                                  description: str, 
                                  action_type: str,
                                  action_params: Dict) -> Optional[str]:
        """Cria uma proposta de governança ética"""
        if not self.governance_enabled:
            logger.warning("Governança não está habilitada")
            return None
            
        try:
            # Verificar threshold de propostas (simulação simplificada)
            balance = self.get_account_balance(proposer)
            threshold = self.config.get("governance", {}).get("proposal_threshold", 100)
            
            if balance < threshold:
                logger.warning(f"Saldo insuficiente para criar proposta. Necessário: {threshold}, Atual: {balance}")
                return None
                
            # Carregar propostas existentes
            with open(self.governance_file, 'r', encoding='utf-8') as f:
                governance = json.load(f)
                
            # Criar nova proposta
            proposal_id = hashlib.sha256(f"{proposer}:{title}:{time.time()}".encode()).hexdigest()
            
            voting_period_days = governance["settings"]["voting_period_days"]
            now = datetime.now()
            end_date = now.replace(day=now.day + voting_period_days).isoformat()
            
            new_proposal = {
                "id": proposal_id,
                "proposer": proposer,
                "title": title,
                "description": description,
                "action_type": action_type,
                "action_params": action_params,
                "created_at": now.isoformat(),
                "voting_ends_at": end_date,
                "status": "active",
                "yes_votes": 0,
                "no_votes": 0,
                "total_voting_power": 0
            }
            
            governance["proposals"].append(new_proposal)
            governance["votes"][proposal_id] = {}
            
            # Salvar governança atualizada
            with open(self.governance_file, 'w', encoding='utf-8') as f:
                json.dump(governance, f, indent=2)
                
            logger.info(f"Proposta de governança criada: {title} (ID: {proposal_id[:8]}...)")
            return proposal_id
            
        except Exception as e:
            logger.error(f"Erro ao criar proposta de governança: {e}")
            return None
    
    def vote_on_proposal(self, voter: str, proposal_id: str, vote: bool) -> bool:
        """Vota em uma proposta de governança ética"""
        if not self.governance_enabled:
            logger.warning("Governança não está habilitada")
            return False
            
        try:
            # Carregar governança
            with open(self.governance_file, 'r', encoding='utf-8') as f:
                governance = json.load(f)
                
            # Verificar se proposta existe e está ativa
            proposal = None
            for p in governance["proposals"]:
                if p["id"] == proposal_id:
                    proposal = p
                    break
                    
            if not proposal:
                logger.warning(f"Proposta não encontrada: {proposal_id}")
                return False
                
            if proposal["status"] != "active":
                logger.warning(f"Proposta não está ativa: {proposal_id}")
                return False
                
            # Verificar se o usuário já votou
            if voter in governance["votes"].get(proposal_id, {}):
                logger.warning(f"Usuário já votou nesta proposta: {voter}")
                return False
                
            # Obter poder de voto (saldo do usuário)
            voting_power = self.get_account_balance(voter)
            
            # Registrar voto
            governance["votes"][proposal_id][voter] = {
                "vote": vote,
                "voting_power": voting_power,
                "timestamp": datetime.now().isoformat()
            }
            
            # Atualizar contagem de votos na proposta
            if vote:
                proposal["yes_votes"] += voting_power
            else:
                proposal["no_votes"] += voting_power
                
            proposal["total_voting_power"] += voting_power
            
            # Salvar governança atualizada
            with open(self.governance_file, 'w', encoding='utf-8') as f:
                json.dump(governance, f, indent=2)
                
            logger.info(f"Voto registrado: {'SIM' if vote else 'NÃO'} por {voter} na proposta {proposal_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao votar em proposta: {e}")
            return False
    
    def execute_proposal(self, proposal_id: str) -> bool:
        """Executa uma proposta aprovada"""
        if not self.governance_enabled:
            logger.warning("Governança não está habilitada")
            return False
            
        try:
            # Carregar governança
            with open(self.governance_file, 'r', encoding='utf-8') as f:
                governance = json.load(f)
                
            # Verificar se proposta existe
            proposal = None
            for i, p in enumerate(governance["proposals"]):
                if p["id"] == proposal_id:
                    proposal = p
                    proposal_index = i
                    break
                    
            if not proposal:
                logger.warning(f"Proposta não encontrada: {proposal_id}")
                return False
                
            # Verificar se a proposta está ativa e o período de votação terminou
            now = datetime.now()
            voting_end = datetime.fromisoformat(proposal["voting_ends_at"])
            
            if proposal["status"] != "active":
                logger.warning(f"Proposta não está ativa: {proposal_id}")
                return False
                
            if now < voting_end:
                logger.warning(f"Período de votação ainda não terminou: {proposal_id}")
                return False
                
            # Verificar se a proposta foi aprovada
            total_votes = proposal["yes_votes"] + proposal["no_votes"]
            if total_votes == 0:
                approval_ratio = 0
            else:
                approval_ratio = proposal["yes_votes"] / total_votes
                
            threshold = governance["settings"]["approval_threshold"]
            
            if approval_ratio < threshold:
                proposal["status"] = "rejected"
                governance["proposals"][proposal_index] = proposal
                
                with open(self.governance_file, 'w', encoding='utf-8') as f:
                    json.dump(governance, f, indent=2)
                    
                logger.info(f"Proposta rejeitada: {proposal['title']} (ID: {proposal_id[:8]}...)")
                return False
                
            # Executar a proposta (simulação)
            # Aqui poderia ter lógica diferente para cada action_type
            action_type = proposal["action_type"]
            action_params = proposal["action_params"]
            
            logger.info(f"Executando proposta: {proposal['title']} - Tipo: {action_type}")
            
            # Atualizar status da proposta
            proposal["status"] = "executed"
            governance["proposals"][proposal_index] = proposal
            
            # Salvar governança atualizada
            with open(self.governance_file, 'w', encoding='utf-8') as f:
                json.dump(governance, f, indent=2)
                
            logger.info(f"Proposta executada: {proposal['title']} (ID: {proposal_id[:8]}...)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar proposta: {e}")
            return False
    
    def get_governance_proposals(self, status: str = None) -> List[Dict]:
        """Retorna lista de propostas de governança, opcionalmente filtradas por status"""
        if not self.governance_enabled:
            logger.warning("Governança não está habilitada")
            return []
            
        try:
            with open(self.governance_file, 'r', encoding='utf-8') as f:
                governance = json.load(f)
                
            if status:
                return [p for p in governance["proposals"] if p["status"] == status]
            else:
                return governance["proposals"]
                
        except Exception as e:
            logger.error(f"Erro ao obter propostas: {e}")
            return []
    
    def get_value_transactions(self, account_id: str = None, limit: int = 100) -> List[Dict]:
        """Retorna as transações de valor ético, opcionalmente filtradas por conta"""
        try:
            with open(self.value_ledger_file, 'r', encoding='utf-8') as f:
                ledger = json.load(f)
                
            if account_id:
                transactions = [tx for tx in ledger["transactions"] if tx["recipient"] == account_id]
            else:
                transactions = ledger["transactions"]
                
            # Ordena por mais recente primeiro e limita
            return sorted(transactions, key=lambda tx: tx["timestamp"], reverse=True)[:limit]
                
        except Exception as e:
            logger.error(f"Erro ao obter transações: {e}")
            return []
        
    def get_status(self) -> Dict:
        """Retorna status da conexão blockchain"""
        status = {
            "connected": not self.simulation_mode,
            "network": self.network,
            "simulation_mode": self.simulation_mode,
            "value_distribution_enabled": self.value_distribution_enabled,
            "governance_enabled": self.governance_enabled,
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.simulation_mode and self.web3:
            status.update({
                "block_number": self.web3.eth.block_number,
                "gas_price": self.web3.eth.gas_price
            })
        
        # Adiciona estatísticas
        try:
            with open(self.transactions_file, 'r', encoding='utf-8') as f:
                transactions = json.load(f)
            status["transaction_count"] = len(transactions["transactions"])
            
            with open(self.value_ledger_file, 'r', encoding='utf-8') as f:
                ledger = json.load(f)
            status["account_count"] = len(ledger["accounts"])
            status["value_transaction_count"] = len(ledger["transactions"])
            
            if self.governance_enabled:
                with open(self.governance_file, 'r', encoding='utf-8') as f:
                    governance = json.load(f)
                status["active_proposals"] = len([p for p in governance["proposals"] if p["status"] == "active"])
                status["executed_proposals"] = len([p for p in governance["proposals"] if p["status"] == "executed"])
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            
        return status

# Função para teste direto do módulo
def main():
    """Função para teste do módulo"""
    bridge = BlockchainBridge()
    
    print("\n" + "="*50)
    print("EVA & GUARANI - Ethereum Blockchain Bridge")
    print("="*50)
    
    status = bridge.get_status()
    print(f"Status: {'Conectado' if status['connected'] else 'Modo de Simulação'}")
    print(f"Rede: {status['network']}")
    print(f"Distribuição de Valor: {'Ativada' if status['value_distribution_enabled'] else 'Desativada'}")
    print(f"Governança: {'Ativada' if status['governance_enabled'] else 'Desativada'}")
    
    # Demonstração básica
    if bridge.value_distribution_enabled:
        print("\nDemonstrando distribuição de valor...")
        tx_hash = bridge.distribute_value("user123", 10.0, "contribuição de código")
        print(f"TX Hash: {tx_hash}")
        
        balance = bridge.get_account_balance("user123")
        print(f"Saldo de user123: {balance}")
        
    if bridge.governance_enabled:
        print("\nDemonstrando governança...")
        proposal_id = bridge.create_governance_proposal(
            "user123", 
            "Adicionar Novas Recompensas", 
            "Adicionar novos tipos de recompensas éticas ao sistema", 
            "add_rewards",
            {"new_reward": "mentoring", "value": 8}
        )
        
        if proposal_id:
            print(f"Proposta criada: {proposal_id}")
            
            voted = bridge.vote_on_proposal("user456", proposal_id, True)
            print(f"Voto registrado: {voted}")
            
            proposals = bridge.get_governance_proposals("active")
            print(f"Propostas ativas: {len(proposals)}")
    
    print("="*50)
    return 0

if __name__ == "__main__":
    main()
