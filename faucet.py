#!/usr/bin/env python3

import time
import asyncio
from datetime import datetime, timedelta
import pytz
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from aiohttp import ClientSession, ClientTimeout
from aiohttp_proxy import ProxyConnector
from config import Config
from utils import Logger, get_headers
from colorama import Fore, Style

class FaucetManager:
    def __init__(self, web3_manager):
        self.config = Config()
        self.web3_manager = web3_manager

    async def check_phrs_balance(self, web3, address: str):
        """Проверка баланса PHRS и рекомендации"""
        try:
            balance = await self.web3_manager.get_token_balance(web3, address, "PHRS")
            
            if balance < 0.01:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Low PHRS balance: {balance:.6f} PHRS{Style.RESET_ALL}")
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Please get PHRS from:${Style.RESET_ALL}")
                Logger.log(f"  • Bridge from other networks")
                Logger.log(f"  • DEX swaps")
                Logger.log(f"  • Community faucets")
                return False
            elif balance < 0.1:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Low PHRS balance: {balance:.6f} PHRS - consider getting more{Style.RESET_ALL}")
                return True
            else:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Good PHRS balance: {balance:.6f} PHRS{Style.RESET_ALL}")
                return True
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Balance check error: {e}{Style.RESET_ALL}")
            return False

    async def try_contract_faucet(self, web3, private_key: str):
        """Попытка использовать контракт крана (если он работает)"""
        try:
            account = Account.from_key(private_key)
            
            # Проверяем, существует ли контракт
            try:
                code = web3.eth.get_code(self.config.FAUCET_CONTRACT)
                if code == '0x':
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Faucet contract not deployed or inactive{Style.RESET_ALL}")
                    return "not_available"
            except:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Cannot access faucet contract{Style.RESET_ALL}")
                return "not_available"
            
            # Пробуем вызвать контракт с минимальным газом
            contract = web3.eth.contract(
                address=self.config.FAUCET_CONTRACT,
                abi=self.config.ERC20_ABI
            )
            
            # Проверяем, можем ли мы клеймить
            try:
                has_claimed = contract.functions.hasClaimed(account.address).call()
                if has_claimed:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Already claimed from contract faucet{Style.RESET_ALL}")
                    return "already_claimed"
            except:
                # Если функция не существует, пробуем клеймить
                pass
            
            # Пробуем клеймить
            tx = contract.functions.claim().build_transaction({
                'from': account.address,
                'gas': 150000,
                'maxFeePerGas': web3.to_wei(1, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(0.5, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Faucet claim sent, waiting for confirmation...{Style.RESET_ALL}")
            
            try:
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                if receipt.status == 1:
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}Contract faucet claimed! TX: {tx_hash.hex()}{Style.RESET_ALL}")
                    return tx_hash.hex()
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}Contract faucet transaction failed{Style.RESET_ALL}")
                    return None
            except:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Faucet transaction timeout - may still be processing{Style.RESET_ALL}")
                return "timeout"
                
        except Exception as e:
            error_msg = str(e).lower()
            if "already claimed" in error_msg:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Already claimed from faucet today{Style.RESET_ALL}")
                return "already_claimed"
            elif "insufficient funds" in error_msg:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Insufficient funds for faucet transaction{Style.RESET_ALL}")
                return "insufficient_funds"
            else:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Contract faucet not available: {str(e)[:100]}...{Style.RESET_ALL}")
                return "not_available"

    async def try_web_faucet(self, address: str, private_key: str, proxy=None):
        """Попытка использовать веб-фаусет через API"""
        try:
            faucet_endpoints = [
                f"{self.config.BASE_API}/faucet/claim",
                f"{self.config.BASE_API}/api/faucet/claim",
                "https://testnet.pharosnetwork.xyz/api/faucet/claim",
                "https://faucet.pharosnetwork.xyz/api/claim"
            ]
            
            timestamp = int(time.time() * 1000)
            message = f"Faucet claim for {address} at {timestamp}"
            
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=private_key)
            signature = to_hex(signed_message.signature)
            
            headers = get_headers()
            headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
            payload = {
                'address': address,
                'message': message,
                'signature': signature
            }
            
            connector = ProxyConnector.from_url(proxy) if proxy else None
            
            for endpoint in faucet_endpoints:
                try:
                    async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                        async with session.post(endpoint, json=payload, headers=headers) as response:
                            if response.status == 200:
                                result = await response.json()
                                if result.get('success') or result.get('status') == 'success':
                                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}Web faucet claim successful!{Style.RESET_ALL}")
                                    return True
                                else:
                                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Web faucet response: {result}{Style.RESET_ALL}")
                            elif response.status == 429:
                                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Faucet rate limited, try again later{Style.RESET_ALL}")
                                return "rate_limited"
                            else:
                                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Faucet endpoint {endpoint} returned {response.status}{Style.RESET_ALL}")
                                
                except Exception as e:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Faucet endpoint {endpoint} failed: {str(e)[:50]}...{Style.RESET_ALL}")
                    continue
            
            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}All web faucet endpoints failed{Style.RESET_ALL}")
            return None
            
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Web faucet error: {e}{Style.RESET_ALL}")
            return None

    async def claim_faucet(self, web3, private_key: str, proxy=None):
        """Основная функция клейма фаусета с несколькими методами"""
        try:
            account = Account.from_key(private_key)
            
            balance_ok = await self.check_phrs_balance(web3, account.address)
            
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Trying faucet methods...{Style.RESET_ALL}")
            
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Method 1: Contract faucet{Style.RESET_ALL}")
            contract_result = await self.try_contract_faucet(web3, private_key)
            
            if contract_result and contract_result not in ["not_available", "insufficient_funds"]:
                return contract_result
            
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Method 2: Web faucet{Style.RESET_ALL}")
            web_result = await self.try_web_faucet(account.address, private_key, proxy)
            
            if web_result and web_result != "rate_limited":
                return web_result
            
            if balance_ok:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Faucet not needed - sufficient balance{Style.RESET_ALL}")
                return "sufficient_balance"
            else:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Faucet unavailable - please get PHRS manually{Style.RESET_ALL}")
                Logger.log(f"{Fore.CYAN + Style.BRIGHT}Alternative sources:{Style.RESET_ALL}")
                Logger.log(f"  • Bridge from other networks")
                Logger.log(f"  • DEX trading")
                Logger.log(f"  • Community channels")
                return "manual_required"
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Faucet claim error: {e}{Style.RESET_ALL}")
            return None

    def format_time_remaining(self, seconds):
        """Форматирование времени до следующего чекина"""
        if seconds <= 0:
            return "Available now"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    async def get_checkin_status(self, address: str, private_key: str, proxy=None, force_check=False):
        """Получение статуса чекина с улучшенной проверкой"""
        try:
            timestamp = int(time.time() * 1000)
            message = f"Check status for {address} at {timestamp}"
            
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=private_key)
            signature = to_hex(signed_message.signature)
            
            connector = ProxyConnector.from_url(proxy) if proxy else None
            
            login_endpoints = [
                f'{self.config.BASE_API}/auth/login',
                f'{self.config.BASE_API}/api/auth/login',
                'https://testnet.pharosnetwork.xyz/api/auth/login'
            ]
            
            for login_endpoint in login_endpoints:
                try:
                    async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                        async with session.post(
                            login_endpoint,
                            json={
                                'address': address,
                                'message': message,
                                'signature': signature
                            },
                            headers=get_headers()
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                if result.get('success'):
                                    access_token = result.get('data', {}).get('accessToken')
                                    
                                    if not access_token:
                                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}No access token received from {login_endpoint}{Style.RESET_ALL}")
                                        continue
                                    
                                    headers_with_auth = get_headers()
                                    headers_with_auth['Authorization'] = f'Bearer {access_token}'
                                    
                                    status_endpoints = [
                                        f'{self.config.BASE_API}/user/checkin-status',
                                        f'{self.config.BASE_API}/api/user/checkin-status',
                                        'https://testnet.pharosnetwork.xyz/api/user/checkin-status'
                                    ]
                                    
                                    for status_endpoint in status_endpoints:
                                        try:
                                            async with session.get(status_endpoint, headers=headers_with_auth) as status_response:
                                                if status_response.status == 200:
                                                    status_result = await status_response.json()
                                                    if status_result.get('success'):
                                                        data = status_result.get('data', {})
                                                        last_checkin = data.get('lastCheckin')
                                                        
                                                        if force_check:
                                                            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Force check enabled, will attempt checkin{Style.RESET_ALL}")
                                                            return True
                                                        
                                                        if last_checkin:
                                                            try:
                                                                if 'T' in last_checkin:
                                                                    last_time = datetime.fromisoformat(last_checkin.replace('Z', '+00:00'))
                                                                else:
                                                                    last_time = datetime.fromtimestamp(int(last_checkin), tz=pytz.UTC)
                                                                
                                                                current_time = datetime.now(pytz.UTC)
                                                                time_diff = current_time - last_time
                                                                
                                                                if time_diff.total_seconds() < 23 * 3600:
                                                                    remaining = 24 * 3600 - time_diff.total_seconds()
                                                                    time_str = self.format_time_remaining(int(remaining))
                                                                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Checkin cooldown: {time_str} remaining{Style.RESET_ALL}")
                                                                    return False
                                                                else:
                                                                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}Checkin available - last checkin was {time_diff.total_seconds()/3600:.1f} hours ago{Style.RESET_ALL}")
                                                                    return True
                                                            except Exception as time_error:
                                                                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Time parse error: {time_error}, assuming checkin available{Style.RESET_ALL}")
                                                                return True
                                                        else:
                                                            Logger.log(f"{Fore.GREEN + Style.BRIGHT}No previous checkin found, checkin available{Style.RESET_ALL}")
                                                            return True
                                                else:
                                                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Status endpoint {status_endpoint} returned {status_response.status}{Style.RESET_ALL}")
                                        except Exception as status_error:
                                            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Status endpoint {status_endpoint} failed: {str(status_error)[:50]}...{Style.RESET_ALL}")
                                            continue
                                    
                                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Cannot check status, assuming checkin available{Style.RESET_ALL}")
                                    return True
                                else:
                                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Login failed at {login_endpoint}: {result}{Style.RESET_ALL}")
                            else:
                                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Login endpoint {login_endpoint} returned {response.status}{Style.RESET_ALL}")
                except Exception as login_error:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Login endpoint {login_endpoint} failed: {str(login_error)[:50]}...{Style.RESET_ALL}")
                    continue
            
            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Cannot determine checkin status, will attempt checkin{Style.RESET_ALL}")
            return True
                        
        except Exception as e:
            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Checkin status check failed: {e}, will try checkin{Style.RESET_ALL}")
            return True

    async def daily_checkin(self, address: str, private_key: str, proxy=None, max_retries=3, force_checkin=False):
        """Улучшенный ежедневный чекин с retry логикой"""
        
        for attempt in range(max_retries):
            try:
                if attempt == 0 and not force_checkin:
                    can_checkin = await self.get_checkin_status(address, private_key, proxy)
                    if not can_checkin:
                        return "cooldown"
                
                timestamp = int(time.time() * 1000)
                message = f"Daily checkin for {address} at {timestamp}"
                
                encoded_message = encode_defunct(text=message)
                signed_message = Account.sign_message(encoded_message, private_key=private_key)
                signature = to_hex(signed_message.signature)
                
                connector = ProxyConnector.from_url(proxy) if proxy else None
                
                login_endpoints = [
                    f'{self.config.BASE_API}/auth/login',
                    f'{self.config.BASE_API}/api/auth/login',
                    'https://testnet.pharosnetwork.xyz/api/auth/login'
                ]
                
                for login_endpoint in login_endpoints:
                    try:
                        async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                            async with session.post(
                                login_endpoint,
                                json={
                                    'address': address,
                                    'message': message,
                                    'signature': signature
                                },
                                headers=get_headers()
                            ) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    if result.get('success'):
                                        access_token = result.get('data', {}).get('accessToken')
                                        
                                        if not access_token:
                                            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}No access token from {login_endpoint}{Style.RESET_ALL}")
                                            continue
                                        
                                        headers_with_auth = get_headers()
                                        headers_with_auth['Authorization'] = f'Bearer {access_token}'
                                        
                                        checkin_endpoints = [
                                            f'{self.config.BASE_API}/user/checkin',
                                            f'{self.config.BASE_API}/api/user/checkin',
                                            'https://testnet.pharosnetwork.xyz/api/user/checkin'
                                        ]
                                        
                                        for checkin_endpoint in checkin_endpoints:
                                            try:
                                                async with session.post(checkin_endpoint, headers=headers_with_auth) as checkin_response:
                                                    if checkin_response.status == 200:
                                                        checkin_result = await checkin_response.json()
                                                        if checkin_result.get('success'):
                                                            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Daily checkin successful! ✅{Style.RESET_ALL}")
                                                            return True
                                                        elif 'already' in str(checkin_result).lower() or 'cooldown' in str(checkin_result).lower():
                                                            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Already checked in today{Style.RESET_ALL}")
                                                            return "already_checked"
                                                        else:
                                                            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Checkin response from {checkin_endpoint}: {checkin_result}{Style.RESET_ALL}")
                                                    else:
                                                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Checkin endpoint {checkin_endpoint} returned {checkin_response.status}{Style.RESET_ALL}")
                                                        continue
                                            except Exception as e:
                                                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Checkin endpoint {checkin_endpoint} failed: {str(e)[:50]}...{Style.RESET_ALL}")
                                                continue
                                        
                                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}All checkin endpoints failed for login {login_endpoint}{Style.RESET_ALL}")
                                    else:
                                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Login failed at {login_endpoint}: {result}{Style.RESET_ALL}")
                                else:
                                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Login endpoint {login_endpoint} returned {response.status}{Style.RESET_ALL}")
                    except Exception as e:
                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Login endpoint {login_endpoint} error: {str(e)[:50]}...{Style.RESET_ALL}")
                        continue
                
                if attempt < max_retries - 1:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Checkin attempt {attempt + 1} failed, retrying in 10 seconds...{Style.RESET_ALL}")
                    await asyncio.sleep(10)
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}Daily checkin failed after {max_retries} attempts{Style.RESET_ALL}")
                    return None
                            
            except Exception as e:
                if attempt < max_retries - 1:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Checkin attempt {attempt + 1} failed: {str(e)[:50]}..., retrying...{Style.RESET_ALL}")
                    await asyncio.sleep(10)
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}Daily checkin error after {max_retries} attempts: {e}{Style.RESET_ALL}")
                    return None
        
        return None