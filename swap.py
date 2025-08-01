#!/usr/bin/env python3

import time
import asyncio
from web3 import Web3
from eth_account import Account
from aiohttp import ClientSession, ClientTimeout
from aiohttp_proxy import ProxyConnector
from config import Config
from utils import Logger
from colorama import Fore, Style

class SwapManager:
    def __init__(self, web3_manager):
        self.config = Config()
        self.web3_manager = web3_manager

    async def fetch_dodo_route(self, from_token: str, to_token: str, user_address: str, amount: int, proxy=None, max_retries=5):
        """Получение маршрута от DODO API с правильными параметрами"""
        try:
            deadline = int(time.time()) + 600
            
            params = {
                "chainId": self.config.CHAIN_ID,
                "deadLine": deadline,
                "apikey": "a37546505892e1a952",
                "slippage": "3.225",
                "source": "dodoV2AndMixWasm",
                "toTokenAddress": to_token,
                "fromTokenAddress": from_token,
                "userAddr": user_address,
                "estimateGas": "true",
                "fromAmount": str(amount)
            }
            
            url = "https://api.dodoex.io/route-service/v2/widget/getdodoroute?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            for attempt in range(max_retries):
                try:
                    connector = ProxyConnector.from_url(proxy) if proxy else None
                    async with ClientSession(connector=connector, timeout=ClientTimeout(total=15)) as session:
                        async with session.get(url) as response:
                            if response.status == 200:
                                result = await response.json()
                                if result.get('status') != -1 and result.get('data', {}).get('data'):
                                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}DODO route obtained successfully{Style.RESET_ALL}")
                                    return result['data']
                                else:
                                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}DODO API status -1, retry {attempt + 1}/{max_retries}{Style.RESET_ALL}")
                            else:
                                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}DODO API HTTP {response.status}, retry {attempt + 1}/{max_retries}{Style.RESET_ALL}")
                                
                except Exception as e:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}DODO API error on attempt {attempt + 1}: {str(e)[:50]}...{Style.RESET_ALL}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
            
            raise Exception("DODO API permanently failed after all retries")
                        
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}All DODO route attempts failed: {e}{Style.RESET_ALL}")
            return None

    async def execute_swap(self, web3, private_key: str, route_data: dict):
        """Выполнение свапа с улучшенной обработкой и мониторингом"""
        try:
            account = Account.from_key(private_key)
            
            if not route_data.get('data') or route_data.get('data') == '0x':
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Invalid transaction data from DODO API{Style.RESET_ALL}")
                return None
            
            gas_limit = int(route_data.get('gasLimit', 500000))
            
            tx = {
                'to': Web3.to_checksum_address(route_data['to']),
                'data': route_data['data'],
                'value': int(route_data.get('value', 0)),
                'gas': gas_limit,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            }
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Swap transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            
            # Мониторинг статуса транзакции с прогресс-баром
            start_time = time.time()
            timeout = 300  # 5 минут
            check_interval = 10  # Проверять каждые 10 секунд
            
            while time.time() - start_time < timeout:
                try:
                    receipt = web3.eth.get_transaction_receipt(tx_hash)
                    if receipt is not None:
                        if receipt.status == 1:
                            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Swap successful! TX confirmed in block #{receipt.blockNumber}{Style.RESET_ALL}")
                            return tx_hash.hex()
                        else:
                            raise Exception("Swap transaction failed")
                except:
                    pass  # Транзакция еще не включена в блок
                
                elapsed = int(time.time() - start_time)
                Logger.log(f"{Fore.CYAN + Style.BRIGHT}Waiting for confirmation... {elapsed}s/{timeout}s{Style.RESET_ALL}")
                await asyncio.sleep(check_interval)
            
            # Если таймаут истек
            raise Exception(f"Transaction not confirmed within {timeout} seconds")
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Swap execution error: {e}{Style.RESET_ALL}")
            
            # Попытка отменить транзакцию
            try:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Attempting to cancel transaction...{Style.RESET_ALL}")
                cancel_tx = {
                    'to': account.address,
                    'value': 0,
                    'gas': 21000,
                    'maxFeePerGas': web3.to_wei(3, 'gwei'),
                    'maxPriorityFeePerGas': web3.to_wei(2, 'gwei'),
                    'nonce': tx['nonce'],
                    'chainId': self.config.CHAIN_ID
                }
                signed_cancel_tx = web3.eth.account.sign_transaction(cancel_tx, private_key)
                cancel_raw_tx = signed_cancel_tx.raw_transaction
                web3.eth.send_raw_transaction(cancel_raw_tx)
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Cancellation transaction sent{Style.RESET_ALL}")
            except Exception as cancel_e:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Failed to cancel transaction: {cancel_e}{Style.RESET_ALL}")
            
            return None
