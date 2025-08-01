#!/usr/bin/env python3

import time
import asyncio
from datetime import datetime
import pytz
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from aiohttp import ClientSession, ClientTimeout, ClientResponseError
from aiohttp_proxy import ProxyConnector
from config import Config
from utils import Logger, get_headers
from colorama import Fore, Style

class WebCheckinManager:
    def __init__(self, web3_manager):
        self.config = Config()
        self.web3_manager = web3_manager
        self.BASE_API = "https://api.pharosnetwork.xyz"
        self.ref_code = "AzekAwH7kgfMHv60"  # Можете поменять на свой
        
    def generate_pharos_signature(self, private_key: str):
        """Генерация подписи для Pharos (подписываем строку 'pharos')"""
        try:
            encoded_message = encode_defunct(text="pharos")
            signed_message = Account.sign_message(encoded_message, private_key=private_key)
            signature = to_hex(signed_message.signature)
            return signature
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Generate signature error: {e}{Style.RESET_ALL}")
            return None

    async def user_login(self, address: str, signature: str, proxy=None, retries=5):
        """Логин пользователя с подписью"""
        url = f"{self.BASE_API}/user/login?address={address}&signature={signature}&wallet=OKX+Wallet&invite_code={self.ref_code}"
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization": "Bearer null",
            "Content-Length": "0"
        }
        
        await asyncio.sleep(3)
        
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get("code") == 0:
                                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Login successful!{Style.RESET_ALL}")
                                return result
                            else:
                                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Login failed: {result.get('msg', 'Unknown error')}{Style.RESET_ALL}")
                        else:
                            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Login returned status {response.status}{Style.RESET_ALL}")
                            
            except Exception as e:
                if attempt < retries - 1:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Login attempt {attempt + 1} failed: {str(e)[:50]}..., retrying...{Style.RESET_ALL}")
                    await asyncio.sleep(5)
                    continue
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}Login failed after {retries} attempts: {e}{Style.RESET_ALL}")

        return None

    async def user_profile(self, address: str, access_token: str, proxy=None, retries=5):
        """Получение профиля пользователя"""
        url = f"{self.BASE_API}/user/profile?address={address}"
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {access_token}"
        }
        
        await asyncio.sleep(3)
        
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get("msg") == "ok":
                                return result
                            elif "code" in result and result["code"] != 0:
                                await asyncio.sleep(5)
                                continue
                                
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

        return None

    async def sign_in(self, address: str, access_token: str, proxy=None, retries=10):
        """Выполнение daily sign-in (чекин)"""
        url = f"{self.BASE_API}/sign/in?address={address}"
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {access_token}",
            "Content-Length": "0"
        }
        
        await asyncio.sleep(3)
        
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            
                            if result.get("msg") == "ok":
                                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Daily check-in successful! ✅{Style.RESET_ALL}")
                                return True
                            elif result.get("msg") == "already signed in today":
                                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Already checked in today{Style.RESET_ALL}")
                                return "already_checked"
                            elif "code" in result and result["code"] not in [0, 1]:
                                await asyncio.sleep(5)
                                continue
                            else:
                                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Check-in response: {result}{Style.RESET_ALL}")
                                
            except Exception as e:
                if attempt < retries - 1:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Check-in attempt {attempt + 1} failed: {str(e)[:50]}..., retrying...{Style.RESET_ALL}")
                    await asyncio.sleep(5)
                    continue

        return None

    async def faucet_status(self, address: str, access_token: str, proxy=None, retries=10):
        """Проверка статуса фаусета"""
        url = f"{self.BASE_API}/faucet/status?address={address}"
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {access_token}"
        }
        
        await asyncio.sleep(3)
        
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get("msg") == "ok":
                                return result
                            elif "code" in result and result["code"] != 0:
                                await asyncio.sleep(5)
                                continue
                                
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

        return None
            
    async def claim_faucet(self, address: str, access_token: str, proxy=None, retries=5):
        """Клейм фаусета"""
        url = f"{self.BASE_API}/faucet/daily?address={address}"
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {access_token}",
            "Content-Length": "0"
        }
        
        await asyncio.sleep(3)
        
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            
                            if result.get("msg") == "ok":
                                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Faucet claimed successfully! 0.2 PHRS{Style.RESET_ALL}")
                                return True
                            elif result.get("msg") == "user has not bound X account":
                                Logger.log(f"{Fore.RED + Style.BRIGHT}Not eligible to claim - bind X account first{Style.RESET_ALL}")
                                return "not_eligible"
                            elif "code" in result and result["code"] not in [0, 1]:
                                await asyncio.sleep(5)
                                continue
                            else:
                                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Faucet response: {result}{Style.RESET_ALL}")
                                
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

        return None

    async def perform_web_checkin(self, private_key: str, proxy=None):
        """Основная функция для выполнения веб чекина"""
        try:
            # Получаем адрес из приватного ключа
            account = Account.from_key(private_key)
            address = account.address
            
            # Генерируем подпись для pharos
            signature = self.generate_pharos_signature(private_key)
            if not signature:
                return None
            
            # Логинимся
            login_result = await self.user_login(address, signature, proxy)
            if not login_result or login_result.get("code") != 0:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Login failed for {address[:8]}...{Style.RESET_ALL}")
                return None
            
            # Получаем access token
            access_token = login_result.get("data", {}).get("jwt")
            if not access_token:
                Logger.log(f"{Fore.RED + Style.BRIGHT}No access token received{Style.RESET_ALL}")
                return None
            
            # Получаем профиль для показа баланса поинтов
            profile = await self.user_profile(address, access_token, proxy)
            if profile and profile.get("msg") == "ok":
                points = profile.get("data", {}).get("user_info", {}).get("TotalPoints", 0)
                Logger.log(f"{Fore.CYAN + Style.BRIGHT}Current Points: {points} PTS{Style.RESET_ALL}")
            
            # Выполняем daily sign-in (чекин)
            checkin_result = await self.sign_in(address, access_token, proxy)
            
            # Проверяем статус фаусета
            faucet_status = await self.faucet_status(address, access_token, proxy)
            if faucet_status and faucet_status.get("msg") == "ok":
                is_able = faucet_status.get("data", {}).get("is_able_to_faucet", False)
                
                if is_able:
                    # Клеймим фаусет
                    faucet_result = await self.claim_faucet(address, access_token, proxy)
                    return {
                        "checkin": checkin_result,
                        "faucet": faucet_result
                    }
                else:
                    # Фаусет уже заклеймен
                    faucet_available_ts = faucet_status.get("data", {}).get("avaliable_timestamp", None)
                    if faucet_available_ts:
                        wib = pytz.timezone('Europe/Moscow')
                        faucet_available_time = datetime.fromtimestamp(faucet_available_ts).astimezone(wib).strftime('%x %X %Z')
                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Faucet already claimed - available at: {faucet_available_time}{Style.RESET_ALL}")
                    else:
                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Faucet already claimed today{Style.RESET_ALL}")
                    
                    return {
                        "checkin": checkin_result,
                        "faucet": "already_claimed"
                    }
            else:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Failed to get faucet status{Style.RESET_ALL}")
                return {
                    "checkin": checkin_result,
                    "faucet": None
                }
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Web checkin error: {e}{Style.RESET_ALL}")
            return None