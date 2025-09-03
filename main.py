#!/usr/bin/env python3
"""
Main script for mass Arbitrum Bridge
Supports ETH → Arbitrum bridge from multiple wallets
"""

import asyncio
import logging
import warnings
from typing import Dict, Any, List
from eth_account import Account
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich import box

# Suppress deprecated pkg_resources warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

# Client imports
from client.arbitrum_client import ArbitrumBridgeClient
from config import get_config

# Simple logging setup to replace utils.logger
def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.get('level', 'INFO').upper()),
        format=config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    return logging.getLogger(__name__)

# Logging setup
config = get_config()
logger = setup_logging(config['logging'])


class ArbitrumBridgeService:
    """Class for mass Arbitrum bridge with dynamic pricing"""
    
    def __init__(self):
        self.config = get_config()
        self.console = Console()
        
    def display_welcome(self):
        """Displays welcome screen with logo."""
        self.console.clear()
        
        combined_text = Text()
        combined_text.append("\n📢 Channel: ", style="bold white")
        combined_text.append("https://t.me/D3_vin", style="cyan")
        combined_text.append("\n💬 Chat: ", style="bold white")
        combined_text.append("https://t.me/D3vin_chat", style="cyan")
        combined_text.append("\n📁 GitHub: ", style="bold white")
        combined_text.append("https://github.com/D3-vin", style="cyan")
        combined_text.append("\n📁 Version: ", style="bold white")
        combined_text.append("1.0", style="green")
        combined_text.append("\n")

        info_panel = Panel(
            Align.left(combined_text),
            title="[bold blue]🌉 Mass SEPOLIA Bridge[/bold blue]",
            subtitle="[bold magenta]Dev by D3vin[/bold magenta]",
            box=box.ROUNDED,
            border_style="bright_blue",
            padding=(0, 1),
            width=50
        )

        self.console.print(info_panel)
        self.console.print()
        
    def load_private_keys(self, filename: str = "p_key.txt") -> List[str]:
        """Loads private keys from file"""
        try:
            with open(filename, 'r') as f:
                keys = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        keys.append(line)
                return keys
        except FileNotFoundError:
            logger.error(f"File {filename} not found!")
            return []
        except Exception as e:
            logger.error(f"Error reading file {filename}: {e}")
            return []
    
    async def create_client_for_wallet(self, private_key: str) -> ArbitrumBridgeClient:
        """Creates client for specific wallet"""
        # Create config copy with needed private key
        wallet_config = self.config.copy()
        wallet_config['wallet']['ethereum_private_key'] = private_key
        
        return ArbitrumBridgeClient(wallet_config)
    
    async def perform_bridge_for_wallet(self, private_key: str, wallet_address: str, amount: float, delay: int = 5) -> Dict[str, Any]:
        """Performs bridge for one wallet with dynamic pricing"""
        try:
            client = await self.create_client_for_wallet(private_key)
            
            logger.debug(f"Performing dynamic bridge for {wallet_address} with amount {amount} ETH")
            
            # Perform bridge with dynamic pricing
            result = await client.perform_bridge(wallet_address, amount)
            
            if result['success']:
                print(f"✅ Bridge successful for {wallet_address}: tx hash {result['tx_hash']}")
                #if 'tx_url' in result:
                    #print(f"   View: {result['tx_url']}")                
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ {wallet_address}: {error_msg}")
                
                # Display balance info for insufficient funds error
                if error_msg == 'Insufficient funds' and 'balance_info' in result:
                    balance_info = result['balance_info']
                    print(f"   💰 Balance: {balance_info['balance_eth']:.6f} ETH")
                    print(f"   💸 Required: {balance_info['required_eth']:.6f} ETH")
                    print(f"   🌉 Bridge amount: {balance_info['bridge_amount_eth']:.6f} ETH")
                    print(f"   ⛽ Gas cost: {balance_info['gas_cost_eth']:.6f} ETH")
                    shortage = balance_info['required_eth'] - balance_info['balance_eth']
                    print(f"   📉 Shortage: {shortage:.6f} ETH")
            # Delay between wallets
            if delay > 0:
                print(f"Delay {delay} seconds...")
                await asyncio.sleep(delay)
            
            return result
            
        except Exception as e:
            error_msg = f"Error for wallet {wallet_address}: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {'success': False, 'error': str(e)}
    
    async def mass_bridge(self):
        """Performs mass bridge"""
        self.display_welcome()
        
        # Load private keys
        private_keys = self.load_private_keys()
        if not private_keys:
            print("❌ No private keys found in p_key.txt file")
            return
        
        # Get wallet addresses
        wallets = []
        for private_key in private_keys:
            try:
                account = Account.from_key(private_key)
                wallets.append((private_key, account.address))
            except Exception as e:
                logger.error(f"Error processing key {private_key[:10]}...: {e}")
                continue
        
        if not wallets:
            print("❌ Failed to process any private key")
            return
        
        print(f"📊 Found wallets: {len(wallets)}")
        
        # Settings
        amount = float(input(f"\nEnter bridge amount in ETH (default 0.0001): ") or "0.0001")
        delay = int(input(f"Enter delay between wallets (seconds, default 15): ") or "15")

        # Confirmation
        confirm = input(f"\nStart bridge with {len(wallets)} wallets for {amount} ETH each? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Operation cancelled")
            return
        
        # Perform bridge for each wallet
        print(f"\n🚀 Starting mass bridge ...")
        
        success_count = 0
        failed_count = 0
        
        for i, (private_key, wallet_address) in enumerate(wallets, 1):
            print(f"\n📤 Wallet {i}/{len(wallets)}: {wallet_address}")
            
            result = await self.perform_bridge_for_wallet(
                private_key, 
                wallet_address,
                amount,
                delay if i < len(wallets) else 0  # No delay after the last wallet
            )
            
            if result['success']:
                success_count += 1
            else:
                failed_count += 1
        
        # Final statistics
        print(f"\n📊 Final statistics:")
        print(f"✅ Successful: {success_count}")
        print(f"❌ Failed: {failed_count}")
        if wallets:
            success_rate = (success_count / len(wallets)) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")

    async def main(self):
        """Main function"""
        try:
            await self.mass_bridge()
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user")
        except Exception as e:
            logger.error(f"Critical error: {e}")
            print(f"❌ Error occurred: {e}")


async def main():
    """Entry point"""
    bridge_service = ArbitrumBridgeService()
    await bridge_service.main()


if __name__ == "__main__":
    asyncio.run(main())