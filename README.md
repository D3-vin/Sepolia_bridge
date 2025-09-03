# Arbitrum Bridge Tool

Tool for mass bridging ETH from Ethereum Sepolia to Arbitrum Sepolia testnet

## 📢 Connect with Us

- **📢 Channel**: [https://t.me/D3_vin](https://t.me/D3_vin) - Latest updates and releases
- **💬 Chat**: [https://t.me/D3vin_chat](https://t.me/D3vin_chat) - Community support and discussions
- **📁 GitHub**: [https://github.com/D3-vin](https://github.com/D3-vin) - Source code and development

![Python](https://img.shields.io/badge/Python-3.6+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-Educational%20Use-green)

## Features

- 🌉 **Automated Bridge Operations** - Mass bridge ETH from multiple wallets
- ⚡ **Dynamic Gas Pricing** - Intelligent EIP-1559 gas calculation with trend analysis
- 💰 **Multi-Wallet Support** - Process multiple private keys from file
- 🔄 **Retry Logic** - Built-in error handling and retry mechanisms
- 📊 **Real-time Statistics** - Live success/failure tracking with detailed reports
- 🎨 **Rich Console Interface** - Beautiful terminal output with panels and colors

## Requirements

- Python 3.8+
- Ethereum Sepolia testnet ETH
- Infura API key [https://www.infura.io](https://www.infura.io)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sepolia_bridge
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your settings in `config.toml`:
```toml
[api]
infura_api_key = "your_infura_key_here"

[bridge]
gas_multiplier = 1.2

[logging]
level = "INFO"
```

4. Add your private keys to `p_key.txt` (one per line)

## Usage

Run the bridge tool:
```bash
python main.py
```

Follow the interactive prompts to:
- Set bridge amount (default: 0.0001 ETH)
- Configure delay between transactions (default: 15 seconds)
- Confirm and start the bridging process

## Configuration

- **Network**: Ethereum Sepolia → Arbitrum Sepolia
- **Contract**: `0xaae29b0366299461418f5324a79afc425be5ae21`
- **Gas Optimization**: EIP-1559 with dynamic priority fees
- **Security**: Local private key management

## Statistics Output

```
📊 Final statistics:
✅ Successful: 5
❌ Failed: 0  
📈 Success rate: 100.0%
```

## Safety Features

- Balance validation before transactions
- Gas estimation and optimization
- Transaction receipt verification
- Comprehensive error logging

## Supported Networks

- **Ethereum Sepolia** (Chain ID: 11155111)
- **Arbitrum Sepolia** (Chain ID: 421614)

## Disclaimer

This tool is for educational and testing purposes on testnets only. Always verify transactions and use at your own risk.