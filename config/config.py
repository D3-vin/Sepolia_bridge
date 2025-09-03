"""
Configuration module with TOML support
"""

import os
from typing import Dict, Any
import tomli as tomllib


def load_config() -> Dict[str, Any]:
    """Loads configuration from config.toml and returns complete config"""
    # Point to config.toml in root directory (parent of config folder)
    config_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(config_dir)
    config_path = os.path.join(root_dir, "config.toml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found")
    
    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        raise RuntimeError(f"Error reading configuration: {e}")
    
    # Add static network configuration
    config['networks'] = {
        'rpcs': {
            'Ethereum': f"https://sepolia.infura.io/v3/{config['api']['infura_api_key']}",
            'Arbitrum_Sepolia': f"https://arbitrum-sepolia.infura.io/v3/{config['api']['infura_api_key']}"
        },
        'scans': {
            'Ethereum': 'https://sepolia.etherscan.io/tx/',
            'Arbitrum_Sepolia': 'https://sepolia.arbiscan.io/tx/'
        },
        'chain_ids': {
            'Ethereum': 11155111, 
            'Arbitrum_Sepolia': 421614
        }
    }
    
    # Add arbitrum static config
    config['arbitrum'] = {
        'bridge_url': 'https://bridge.arbitrum.io',
        'contract_address': '0xaae29b0366299461418f5324a79afc425be5ae21',
        'default_gas_limit': 100000
    }
    
    # Add wallet placeholder
    config['wallet'] = {
        'ethereum_private_key': ''
    }
    
    return config


def get_config() -> Dict[str, Any]:
    """Returns complete configuration"""
    return load_config()