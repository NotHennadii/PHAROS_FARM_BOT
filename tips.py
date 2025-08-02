#!/usr/bin/env python3

import random
import time
import asyncio
from web3 import Web3
from eth_account import Account
from config import Config
from utils import Logger
from colorama import Fore, Style

class TipManager:
    def __init__(self, web3_manager):
        self.config = Config()
        self.web3_manager = web3_manager

    async def send_tip(self, web3, private_key: str, username: str, amount_wei: int, max_retries=3):
        """Отправка чаевых пользователю с улучшенной обработкой ошибок"""
        for attempt in range(max_retries):
            try:
                account = Account.from_key(private_key)
                
                # Проверяем баланс
                balance = web3.eth.get_balance(account.address)
                if balance < amount_wei + web3.to_wei(0.001, 'ether'):  # Оставляем запас на газ
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient balance for tip. Balance: {Web3.from_wei(balance, 'ether'):.6f} PHRS{Style.RESET_ALL}")
                    return None
                
                contract = web3.eth.contract(
                    address=self.config.PRIMUS_TIP_CONTRACT,
                    abi=self.config.PRIMUS_TIP_ABI
                )
                
                token_struct = (1, Web3.to_checksum_address("0x0000000000000000000000000000000000000000"))
                recipient_struct = ("x", username, amount_wei, [])
                
                # Получаем текущий nonce с небольшой задержкой для избежания коллизий
                if attempt > 0:
                    await asyncio.sleep(2)
                
                current_nonce = web3.eth.get_transaction_count(account.address, 'pending')
                
                # Добавляем случайную задержку для избежания replay attacks
                await asyncio.sleep(random.uniform(1, 3))
                
                tx = contract.functions.tip(token_struct, recipient_struct).build_transaction({
                    'from': account.address,
                    'value': amount_wei,
                    'gas': 350000,  # Увеличиваем газ лимит
                    'maxFeePerGas': web3.to_wei(3 + attempt, 'gwei'),  # Увеличиваем gas price с каждой попыткой
                    'maxPriorityFeePerGas': web3.to_wei(2 + attempt, 'gwei'),
                    'nonce': current_nonce,
                    'chainId': self.config.CHAIN_ID
                })
                
                # Подписываем транзакцию
                signed_tx = web3.eth.account.sign_transaction(tx, private_key)
                raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
                
                # Отправляем транзакцию
                tx_hash = web3.eth.send_raw_transaction(raw_tx)
                
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Tip transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
                
                # Ждем подтверждения с таймаутом
                try:
                    receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                    
                    if receipt.status == 1:
                        amount_phrs = Web3.from_wei(amount_wei, 'ether')
                        Logger.log(f"{Fore.GREEN + Style.BRIGHT}Tip sent! {amount_phrs:.8f} PHRS to @{username} | TX: {tx_hash.hex()}{Style.RESET_ALL}")
                        return tx_hash.hex()
                    else:
                        raise Exception("Tip transaction failed in receipt")
                        
                except Exception as receipt_error:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Tip transaction timeout or failed: {receipt_error}{Style.RESET_ALL}")
                    
                    # Проверяем, была ли транзакция всё же выполнена
                    await asyncio.sleep(30)
                    try:
                        receipt = web3.eth.get_transaction_receipt(tx_hash)
                        if receipt and receipt.status == 1:
                            amount_phrs = Web3.from_wei(amount_wei, 'ether')
                            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Tip confirmed after delay! {amount_phrs:.8f} PHRS to @{username} | TX: {tx_hash.hex()}{Style.RESET_ALL}")
                            return tx_hash.hex()
                    except:
                        pass
                    
                    if attempt < max_retries - 1:
                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Retrying tip transaction... ({attempt + 2}/{max_retries}){Style.RESET_ALL}")
                        continue
                    else:
                        return None
                        
            except Exception as e:
                error_msg = str(e).lower()
                
                if "replay" in error_msg or "nonce" in error_msg:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Nonce/Replay error on attempt {attempt + 1}: {e}{Style.RESET_ALL}")
                    if attempt < max_retries - 1:
                        # Ждем дольше при nonce проблемах
                        await asyncio.sleep(5 + attempt * 2)
                        continue
                elif "insufficient funds" in error_msg:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}Insufficient funds for tip{Style.RESET_ALL}")
                    return None
                elif "gas" in error_msg:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Gas error on attempt {attempt + 1}: {e}{Style.RESET_ALL}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(3)
                        continue
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}Send tip error on attempt {attempt + 1}: {e}{Style.RESET_ALL}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(3)
                        continue
                
                if attempt == max_retries - 1:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}All tip attempts failed: {e}{Style.RESET_ALL}")
                    return None
        
        return None

    def generate_random_tip_amount(self):
        """Генерация случайной суммы чаевых с большей вариативностью"""
        # Используем более широкий диапазон для уменьшения вероятности дублирования
        min_tip = Web3.to_wei(0.0000001, 'ether')  # 0.0000001 PHRS
        max_tip = Web3.to_wei(0.0000003, 'ether')  # 0.0000003 PHRS
        
        # Добавляем случайное число для большей уникальности
        base_amount = random.randint(min_tip, max_tip)
        random_addition = random.randint(1, 1000)  # Добавляем от 1 до 1000 wei
        
        return base_amount + random_addition

    async def check_tip_contract_status(self, web3):
        """Проверка статуса контракта для типов"""
        try:
            # Проверяем, существует ли контракт
            code = web3.eth.get_code(self.config.PRIMUS_TIP_CONTRACT)
            if code == '0x':
                Logger.log(f"{Fore.RED + Style.BRIGHT}Tip contract not deployed{Style.RESET_ALL}")
                return False
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Tip contract is active{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Error checking tip contract: {e}{Style.RESET_ALL}")
            return False