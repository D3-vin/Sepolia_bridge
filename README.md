# Sepolia Bridge Tool v1.2

Tool for mass bridging ETH from Ethereum Sepolia to multiple Layer 2 networks

## 📢 Connect with Us

- **📢 Channel**: [https://t.me/D3_vin](https://t.me/D3_vin) - Latest updates and releases
- **💬 Chat**: [https://t.me/D3vin_chat](https://t.me/D3vin_chat) - Community support and discussions
- **📁 GitHub**: [https://github.com/D3-vin](https://github.com/D3-vin) - Source code and development

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-Educational%20Use-green)

## Features

- 🌉 **Multi-Chain Bridge Support** - Arbitrum Sepolia & Base Sepolia networks
- ⚡ **Dynamic Gas Pricing** - Intelligent EIP-1559 gas calculation
- 💰 **Multi-Wallet Support** - Process multiple private keys from file
- 🔄 **Retry Logic** - Built-in error handling and retry mechanisms
- 📊 **Real-time Statistics** - Live success/failure tracking with detailed reports
- 🎨 **Rich Console Interface** - Beautiful terminal output with panels and colors
- 🔧 **Local Transaction Building** - No external API dependencies for transaction construction

## Requirements

- Python 3.8+
- Ethereum Sepolia testnet ETH
- Infura API key [https://www.infura.io](https://www.infura.io)

## Supported Networks

**Mode 1: Ethereum Sepolia → Arbitrum Sepolia**
- Contract: `0xaae29b0366299461418f5324a79afc425be5ae21`
- Function: `createRetryableTicket`
- Chain ID: 421614

**Mode 2: Ethereum Sepolia → Base Sepolia**
- Contract: `0xfd0Bf71F60660E2f608ed56e1659C450eB113120` (L1StandardBridge)
- Function: `bridgeETHTo`
- Chain ID: 84532

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

### Interactive Menu
Select your bridge mode:
1. **ETH Sepolia → ARB Sepolia** (Arbitrum Bridge)
2. **ETH Sepolia → BASE Sepolia** (Base Bridge)
3. **Exit**

Follow the interactive prompts to:
- Set bridge amount (default: 0.0001 ETH)
- Configure delay between transactions (default: 15 seconds)
- Confirm and start the bridging process

### Navigation
- **Press Enter** after operation completion to return to main menu
- **Any other key** to exit application

## Configuration

### Arbitrum Mode
- **Network**: Ethereum Sepolia → Arbitrum Sepolia  
- **Contract**: `0xaae29b0366299461418f5324a79afc425be5ae21`
- **Gas Optimization**: EIP-1559 with dynamic submission cost calculation
- **L2 Gas**: Dynamic L2 gas price fetching

### Base Mode
- **Network**: Ethereum Sepolia → Base Sepolia
- **Contract**: `0xfd0Bf71F60660E2f608ed56e1659C450eB113120`
- **Gas Optimization**: EIP-1559 with fixed gas limit (756,499)
- **Bridge Data**: Uses "superbridge" extraData for compatibility

### Security
- Local private key management
- No external API dependencies for transaction construction

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

## Network Details

- **Ethereum Sepolia** (Chain ID: 11155111) - Source network
- **Arbitrum Sepolia** (Chain ID: 421614) - Target L2 network
- **Base Sepolia** (Chain ID: 84532) - Target L2 network

## Disclaimer

This tool is for educational and testing purposes on testnets only. Always verify transactions and use at your own risk.