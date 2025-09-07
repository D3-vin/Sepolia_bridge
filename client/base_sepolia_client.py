"""
Base Sepolia Bridge Client with local transaction building
"""

import logging
from typing import Dict, Any
from web3 import Web3
from eth_utils.address import to_checksum_address

from .base_client import BaseBridgeClient

logger = logging.getLogger(__name__)


class BaseSepoliaBridgeClient(BaseBridgeClient):
    """Client for Base Sepolia Bridge operations with local transaction building"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Base Sepolia L1StandardBridge contract address (correct one from sniffer)
        self.bridge_contract = "0xfd0Bf71F60660E2f608ed56e1659C450eB113120"
        self.gas_multiplier = config['bridge']['gas_multiplier']
        
        # L2 RPC connection
        self.l2_rpc_url = config['networks']['rpcs']['Base_Sepolia']
        self.w3_l2 = Web3(Web3.HTTPProvider(self.l2_rpc_url))
        
        # Base L1StandardBridge contract ABI with bridgeETHTo function
        self.BRIDGE_ABI = [
            {
                "inputs": [
                    {"internalType": "address", "name": "_to", "type": "address"},
                    {"internalType": "uint32", "name": "_minGasLimit", "type": "uint32"},
                    {"internalType": "bytes", "name": "_extraData", "type": "bytes"}
                ],
                "name": "bridgeETHTo",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
    
    def calculate_submission_cost(self, gas_prices: dict) -> int:
        """Base doesn't need submission cost like Arbitrum"""
        return 0  # Base bridge doesn't require additional submission cost

    def get_l2_gas_params(self) -> tuple:
        """Gets L2 gas parameters for Base - uses _minGasLimit from sniffer data"""
        # From sniffer data: _minGasLimit = 0x30d40 = 200000
        min_gas_limit = 200000  # Same as in the successful transaction
        return min_gas_limit
    
    async def perform_bridge(self, to_address: str, amount: float) -> Dict[str, Any]:
        """Performs bridge using bridgeETHTo function like in sniffer data"""
        try:
            web3 = self._get_web3("Ethereum")
            gas_prices = self.get_current_gas_prices(web3)
            amount_wei = int(amount * 10**18)
            
            # For Base bridge, we only need to send the ETH amount
            required_value = amount_wei
            
            # From sniffer data: gasLimit = 0xb8b13 = 756499
            gas_estimate = 756499
            min_gas_limit = self.get_l2_gas_params()
            
            balance_check = self.check_wallet_balance(web3, self.address, required_value, gas_prices, gas_estimate)
            if not balance_check['sufficient']:
                return {
                    'success': False, 
                    'error': 'Insufficient funds',
                    'balance_info': balance_check
                }
            
            bridge_contract = web3.eth.contract(
                address=to_checksum_address(self.bridge_contract),
                abi=self.BRIDGE_ABI
            )
            
            # From sniffer: _extraData = "superbridge" (0x7375706572627269646765)
            extra_data = "superbridge".encode('utf-8')
            
            transaction = bridge_contract.functions.bridgeETHTo(
                to_checksum_address(self.address),  # _to
                min_gas_limit,                      # _minGasLimit
                extra_data                          # _extraData
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
            
            # Handle both Web3.py versions
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
                return {'success': False, 'error': 'Transaction reverted'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}