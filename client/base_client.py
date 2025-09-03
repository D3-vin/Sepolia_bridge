"""
Base class for bridge clients
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from web3 import Web3
from eth_account import Account
from eth_utils.address import to_checksum_address

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_config

logger = logging.getLogger(__name__)


class BaseBridgeClient(ABC):
    """Base class for bridge clients"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.private_key = config['wallet']['ethereum_private_key']
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address
        self.web3_instances: Dict[str, Web3] = {}
    
    def _get_web3(self, chain: str) -> Web3:
        """Gets or creates Web3 instance for network"""
        if chain not in self.web3_instances:
            rpc_url = self.config['networks']['rpcs'].get(chain)
            if not rpc_url:
                raise ValueError(f"RPC URL not found for network {chain}")
            
            self.web3_instances[chain] = Web3(Web3.HTTPProvider(rpc_url))
            
            # Check connection
            try:
                web3_instance = self.web3_instances[chain]
                if not web3_instance.is_connected():
                    raise ConnectionError(f"Failed to connect to {chain}")
            except Exception as e:
                raise ConnectionError(f"Failed to connect to {chain}: {e}")
        
        return self.web3_instances[chain]
    
    def get_current_gas_prices(self, web3_instance: Web3) -> Dict[str, Any]:
        """Gets current gas prices with EIP-1559 calculation"""
        try:
            latest_block = web3_instance.eth.get_block('latest')
            block_number = latest_block.get('number', 0)
            
            if block_number > 0:
                prev_block = web3_instance.eth.get_block(block_number - 1)
            else:
                prev_block = latest_block
            
            base_fee_current = latest_block.get('baseFeePerGas', 0)
            base_fee_prev = prev_block.get('baseFeePerGas', 0)
            
            # Calculate trend
            base_fee_trend = (base_fee_current - base_fee_prev) / base_fee_prev if base_fee_prev > 0 else 0
            
            gas_price = web3_instance.eth.gas_price
            
            # Dynamic priority fee
            min_priority_fee = 1000000000  # 1 gwei minimum
            max_priority_fee = 5000000000  # 5 gwei maximum
            
            if base_fee_trend > 0.1:  # Base fee growing fast
                priority_fee = max_priority_fee
            elif gas_price > base_fee_current * 1.5:  # High network congestion
                priority_fee = int(min_priority_fee * 3)  # 3 gwei
            else:
                priority_fee = 2000000000  # 2 gwei default
            
            priority_fee = max(min_priority_fee, min(priority_fee, max_priority_fee))
            
            # Calculate max fee with buffer
            base_fee_buffer = 1.3 if base_fee_trend > 0 else 1.1
            max_fee = int(base_fee_current * base_fee_buffer + priority_fee)
            
            logger.debug(f"Gas price calculation:")
            logger.debug(f"  Base fee: {base_fee_current} wei ({base_fee_current/10**9:.2f} gwei)")
            logger.debug(f"  Priority fee: {priority_fee} wei ({priority_fee/10**9:.2f} gwei)")
            logger.debug(f"  Max fee: {max_fee} wei ({max_fee/10**9:.2f} gwei)")
            
            return {
                'base_fee': base_fee_current,
                'gas_price': gas_price,
                'max_priority_fee': priority_fee,
                'max_fee_per_gas': max_fee,
                'base_fee_trend': base_fee_trend
            }
        except Exception as e:
            logger.warning(f"Failed to get gas prices: {e}")
            # Fallback values
            return {
                'base_fee': 20000000000,    # 20 gwei
                'gas_price': 25000000000,   # 25 gwei  
                'max_priority_fee': 2000000000,  # 2 gwei
                'max_fee_per_gas': 22000000000,  # 22 gwei
                'base_fee_trend': 0
            }
    
    def check_wallet_balance(self, web3_instance: Web3, address: str, required_value: int, gas_prices: dict, gas_limit: int) -> Dict[str, Any]:
        """Checks if wallet has sufficient funds and returns detailed balance info"""
        try:
            balance = web3_instance.eth.get_balance(to_checksum_address(address))
            gas_cost = gas_limit * gas_prices['max_fee_per_gas']
            total_needed = required_value + gas_cost
            
            balance_info = {
                'sufficient': balance >= total_needed,
                'balance_eth': balance / 10**18,
                'required_eth': total_needed / 10**18,
                'bridge_amount_eth': required_value / 10**18,
                'gas_cost_eth': gas_cost / 10**18
            }
            
            logger.debug(f"Balance check for {address}:")
            logger.debug(f"  Balance: {balance_info['balance_eth']:.6f} ETH")
            logger.debug(f"  Required: {balance_info['required_eth']:.6f} ETH")
            logger.debug(f"  Sufficient: {'YES' if balance_info['sufficient'] else 'NO'}")
            
            return balance_info
            
        except Exception as e:
            logger.error(f"Balance check error: {e}")
            return {
                'sufficient': False,
                'balance_eth': 0,
                'required_eth': 0,
                'bridge_amount_eth': 0,
                'gas_cost_eth': 0,
                'error': str(e)
            }
    
    @abstractmethod
    async def perform_bridge(self, to_address: str, amount: float) -> Dict[str, Any]:
        """Abstract method for performing bridge"""
        pass