#!/usr/bin/env python3

import time
import asyncio
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from eth_abi import encode  # Добавляем этот импорт
from aiohttp import ClientSession, ClientTimeout
from aiohttp_proxy import ProxyConnector
from config import Config
from utils import Logger
from colorama import Fore, Style

class AquaFluxManager:
    def __init__(self, web3_manager):
        self.config = Config()
        self.web3_manager = web3_manager

    async def aquaflux_login(self, address: str, private_key: str, proxy=None):
        """Вход в AquaFlux с правильным форматом сообщения"""
        try:
            timestamp = int(time.time() * 1000)  # Миллисекунды как в JS
            message = f"Sign in to AquaFlux with timestamp: {timestamp}"
            
            # Используем правильный метод подписи
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=private_key)
            signature = to_hex(signed_message.signature)
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.5',
                'content-type': 'application/json',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.post(
                    'https://api.aquaflux.pro/api/v1/users/wallet-login',
                    json={
                        'address': address,
                        'message': message,
                        'signature': signature
                    },
                    headers=headers
                ) as response:
                    result = await response.json()
                    if result.get('status') == 'success':
                        Logger.log(f"{Fore.GREEN + Style.BRIGHT}AquaFlux login successful!{Style.RESET_ALL}")
                        return result['data']['accessToken']
                    else:
                        raise Exception(f"Login failed: {result}")
                        
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}AquaFlux login failed: {e}{Style.RESET_ALL}")
            return None

    async def claim_aquaflux_tokens(self, web3, private_key: str):
        """Клейм бесплатных токенов C и S"""
        try:
            account = Account.from_key(private_key)
            contract = web3.eth.contract(
                address=self.config.AQUAFLUX_NFT_CONTRACT,
                abi=self.config.AQUAFLUX_NFT_ABI
            )
            
            tx = contract.functions.claimTokens().build_transaction({
                'from': account.address,
                'gas': 300000,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Claim tokens transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}AquaFlux tokens claimed!{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                raise Exception("Transaction failed")
                
        except Exception as e:
            if "already claimed" in str(e).lower():
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Tokens already claimed today{Style.RESET_ALL}")
                return "already_claimed"
            else:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Claim tokens error: {e}{Style.RESET_ALL}")
                return None

    async def craft_cs_tokens(self, web3, private_key: str):
        """Крафт CS токенов используя прямой вызов как в JS"""
        try:
            account = Account.from_key(private_key)
            required_amount = web3.to_wei(100, 'ether')
            
            # Проверяем балансы
            c_balance = await self.web3_manager.get_token_balance(web3, account.address, self.config.AQUAFLUX_TOKENS['C'])
            s_balance = await self.web3_manager.get_token_balance(web3, account.address, self.config.AQUAFLUX_TOKENS['S'])
            
            if c_balance < 100 or s_balance < 100:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient tokens. C: {c_balance:.2f}, S: {s_balance:.2f}{Style.RESET_ALL}")
                return None
            
            # Одобряем токены
            await self.web3_manager.approve_token(web3, private_key, self.config.AQUAFLUX_TOKENS['C'], self.config.AQUAFLUX_NFT_CONTRACT, required_amount)
            await self.web3_manager.approve_token(web3, private_key, self.config.AQUAFLUX_TOKENS['S'], self.config.AQUAFLUX_NFT_CONTRACT, required_amount)
            
            # Используем прямой вызов метода как в JS
            CRAFT_METHOD_ID = '0x4c10b523'
            
            # Кодируем параметры
            encoded_params = encode(['uint256'], [required_amount])
            calldata = CRAFT_METHOD_ID + encoded_params.hex()
            
            tx = {
                'to': self.config.AQUAFLUX_NFT_CONTRACT,
                'data': calldata,
                'gas': 300000,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            }
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Crafting transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}CS tokens crafted successfully!{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                raise Exception("Crafting transaction reverted")
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Craft CS tokens error: {e}{Style.RESET_ALL}")
            return None

    # Остальные методы остаются такими же...
    async def get_aquaflux_signature(self, address: str, access_token: str, nft_type: int = 0, proxy=None):
        """Получение подписи для минта NFT"""
        try:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.post(
                    'https://api.aquaflux.pro/api/v1/users/get-signature',
                    json={
                        'walletAddress': address,
                        'requestedNftType': nft_type
                    },
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                ) as response:
                    result = await response.json()
                    if result.get('status') == 'success':
                        Logger.log(f"{Fore.GREEN + Style.BRIGHT}AquaFlux signature obtained{Style.RESET_ALL}")
                        return result['data']
                    else:
                        raise Exception(f"Get signature failed: {result}")
                        
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Get signature error: {e}{Style.RESET_ALL}")
            return None

    async def mint_aquaflux_nft(self, web3, private_key: str, signature_data: dict):
        """Минт NFT используя правильный method ID"""
        try:
            account = Account.from_key(private_key)
            
            # Проверяем баланс CS токенов
            cs_balance = await self.web3_manager.get_token_balance(web3, account.address, self.config.AQUAFLUX_TOKENS['CS'])
            if cs_balance < 100:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient CS tokens: {cs_balance:.2f}{Style.RESET_ALL}")
                return None
            
            required_amount = web3.to_wei(100, 'ether')
            await self.web3_manager.approve_token(web3, private_key, self.config.AQUAFLUX_TOKENS['CS'], self.config.AQUAFLUX_NFT_CONTRACT, required_amount)
            
            # Проверяем срок действия подписи
            current_time = int(time.time())
            if current_time >= signature_data.get('expiresAt', 0):
                Logger.log(f"{Fore.RED + Style.BRIGHT}Signature expired!{Style.RESET_ALL}")
                return None
            
            # Используем правильный method ID как в JS
            CORRECT_METHOD_ID = '0x75e7e053'
            
            # Кодируем параметры
            signature_bytes = bytes.fromhex(signature_data['signature'][2:] if signature_data['signature'].startswith('0x') else signature_data['signature'])
            
            encoded_params = encode(
                ['uint256', 'uint256', 'bytes'],
                [signature_data.get('nftType', 0), signature_data['expiresAt'], signature_bytes]
            )
            calldata = CORRECT_METHOD_ID + encoded_params.hex()
            
            tx = {
                'to': self.config.AQUAFLUX_NFT_CONTRACT,
                'data': calldata,
                'gas': 400000,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            }
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}NFT mint transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}NFT minted successfully!{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                raise Exception("NFT mint transaction reverted")
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}NFT mint error: {e}{Style.RESET_ALL}")
            return None
