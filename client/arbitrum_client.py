"""
Arbitrum Bridge Client with dynamic pricing
"""

import logging
from typing import Dict, Any
from web3 import Web3
from eth_utils.address import to_checksum_address

from .base_client import BaseBridgeClient

logger = logging.getLogger(__name__)


class ArbitrumBridgeClient(BaseBridgeClient):
    """Client for Arbitrum Bridge operations"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bridge_contract = config['arbitrum']['contract_address']
        self.gas_multiplier = config['bridge']['gas_multiplier']
        
        # L2 RPC connection
        self.l2_rpc_url = config['networks']['rpcs']['Arbitrum_Sepolia']
        self.w3_l2 = Web3(Web3.HTTPProvider(self.l2_rpc_url))
        
        # Inbox contract ABI
        self.INBOX_ABI = [
            {
                "inputs": [
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "l2CallValue", "type": "uint256"},
                    {"internalType": "uint256", "name": "maxSubmissionCost", "type": "uint256"},
                    {"internalType": "address", "name": "excessFeeRefundAddress", "type": "address"},
                    {"internalType": "address", "name": "callValueRefundAddress", "type": "address"},
                    {"internalType": "uint256", "name": "gasLimit", "type": "uint256"},
                    {"internalType": "uint256", "name": "maxFeePerGas", "type": "uint256"},
                    {"internalType": "bytes", "name": "data", "type": "bytes"}
                ],
                "name": "createRetryableTicket",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
    
    def calculate_submission_cost(self, gas_prices: dict) -> int:
        """Calculates dynamic submission cost"""
        web3 = self._get_web3("Ethereum")
        base_cost = web3.to_wei(0.001, 'ether')
        gas_adjustment = min(gas_prices['gas_price'] / 20000000000, 2.0)
        return int(base_cost * gas_adjustment)

    def get_l2_gas_params(self) -> tuple:
        """Gets L2 gas parameters"""
        try:
            l2_gas_price = self.w3_l2.eth.gas_price
        except Exception:
            l2_gas_price = 100000000  # 0.1 gwei fallback
        return 500000, l2_gas_price

    async def perform_bridge(self, to_address: str, amount: float) -> Dict[str, Any]:
        """Performs bridge with dynamic pricing"""
        try:
            web3 = self._get_web3("Ethereum")
            gas_prices = self.get_current_gas_prices(web3)
            amount_wei = int(amount * 10**18)
            
            submission_cost = self.calculate_submission_cost(gas_prices)
            gas_limit_l2, gas_price_l2 = self.get_l2_gas_params()
            required_value = amount_wei + submission_cost + (gas_limit_l2 * gas_price_l2)
            
            gas_estimate = self.config['arbitrum']['default_gas_limit']
            balance_check = self.check_wallet_balance(web3, self.address, required_value, gas_prices, gas_estimate)
            if not balance_check['sufficient']:
                return {
                    'success': False, 
                    'error': 'Insufficient funds',
                    'balance_info': balance_check
                }
            
            inbox_contract = web3.eth.contract(
                address=to_checksum_address(self.bridge_contract),
                abi=self.INBOX_ABI
            )
            
            transaction = inbox_contract.functions.createRetryableTicket(
                to_checksum_address(self.address), amount_wei, submission_cost,
                to_checksum_address(self.address), to_checksum_address(self.address),
                gas_limit_l2, gas_price_l2, b''
            ).build_transaction({
                'from': self.address,
                'value': required_value,
                'gas': gas_estimate,
                'maxPriorityFeePerGas': gas_prices['max_priority_fee'],
                'maxFeePerGas': gas_prices['max_fee_per_gas'],
                'nonce': web3.eth.get_transaction_count(self.address, 'pending'),
                'chainId': 11155111,
                'type': 2
            })
            
            signed_txn = web3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Handle both Web3.py versions for transaction attribute
            try:
                raw_transaction = signed_txn.raw_transaction
            except AttributeError:
                raw_transaction = signed_txn.rawTransaction
            
            tx_hash = web3.eth.send_raw_transaction(raw_transaction)
            tx_hash_hex = tx_hash.hex()
            
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt['status'] == 1:
                return {
                    'success': True,
                    'tx_hash': tx_hash_hex,
                    'block_number': receipt['blockNumber'],
                    'gas_used': receipt['gasUsed'],
                    'tx_url': f"https://sepolia.etherscan.io/tx/{tx_hash_hex}"
                }
            else:
                return {'success': False, 'error': 'Transaction failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}