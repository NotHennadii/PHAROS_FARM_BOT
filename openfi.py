#!/usr/bin/env python3

import asyncio
import random
import time
from web3 import Web3
from eth_account import Account
from config import Config
from utils import Logger
from colorama import Fore, Style

class OpenFiManager:
    def __init__(self, web3_manager):
        self.config = Config()
        self.web3_manager = web3_manager
        
        # Адреса контрактов OpenFi (преобразованы в checksum формат)
        self.USDT_CONTRACT_ADDRESS = Web3.to_checksum_address("0x0B00Fb1F513E02399667FBA50772B21f34c1b5D9")
        self.USDC_CONTRACT_ADDRESS = Web3.to_checksum_address("0x48249feEb47a8453023f702f15CF00206eeBdF08")
        self.WPHRS_CONTRACT_ADDRESS = Web3.to_checksum_address("0x253F3534e1e36B9E4a1b9A6F7b6dE47AC3e7AaD3")
        self.GOLD_CONTRACT_ADDRESS = Web3.to_checksum_address("0x77f532df5f46DdFf1c97CDae3115271A523fa0f4")
        self.TSLA_CONTRACT_ADDRESS = Web3.to_checksum_address("0xCDA3DF4AAB8a571688fE493EB1BdC1Ad210C09E4")
        self.BTC_CONTRACT_ADDRESS = Web3.to_checksum_address("0xA4a967FC7cF0E9815bF5c2700A055813628b65BE")
        self.NVIDIA_CONTRACT_ADDRESS = Web3.to_checksum_address("0x3299cc551B2a39926Bf14144e65630e533dF6944")
        
        # Адреса роутеров (преобразованы в checksum формат)
        self.MINT_ROUTER_ADDRESS = Web3.to_checksum_address("0x2E9D89D372837F71Cb529e5BA85bFbC1785C69Cd")
        self.DEPOSIT_ROUTER_ADDRESS = Web3.to_checksum_address("0xa8E550710Bf113DB6A1B38472118b8d6d5176D12")
        self.SUPPLY_ROUTER_ADDRESS = Web3.to_checksum_address("0xAd3B4E20412A097F87CD8e8d84FbBe17ac7C89e9")
        
        # ABI для минтинга токенов
        self.MINT_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "mint",
                "inputs": [
                    { "internalType": "address", "name": "_asset", "type": "address" },
                    { "internalType": "address", "name": "_account", "type": "address" },
                    { "internalType": "uint256", "name": "_amount", "type": "uint256" }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            }
        ]
        
        # ABI для lending операций
        self.LENDING_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "depositETH",
                "inputs": [
                    { "name": "lendingPool", "type": "address" },
                    { "name": "onBehalfOf", "type": "address" },
                    { "name": "referralCode", "type": "uint16" }
                ],
                "outputs": [],
                "stateMutability": "payable"
            },
            {
                "type": "function",
                "name": "supply",
                "inputs": [
                    { "name": "asset", "type": "address" },
                    { "name": "amount", "type": "uint256" },
                    { "name": "onBehalfOf", "type": "address" },
                    { "name": "referralCode", "type": "uint16" }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            },
            {
                "type": "function",
                "name": "borrow",
                "inputs": [
                    { "name": "asset", "type": "address" },
                    { "name": "amount", "type": "uint256" },
                    { "name": "interestRateMode", "type": "uint256" },
                    { "name": "referralCode", "type": "uint16" },
                    { "name": "onBehalfOf", "type": "address" }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            },
            {
                "type": "function",
                "name": "withdraw",
                "inputs": [
                    { "name": "asset", "type": "address" },
                    { "name": "amount", "type": "uint256" },
                    { "name": "to", "type": "address" }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            }
        ]
        
        # Доступные токены для операций (преобразованы в checksum формат)
        self.tokens = {
            "USDT": {"address": Web3.to_checksum_address("0x0B00Fb1F513E02399667FBA50772B21f34c1b5D9"), "decimals": 6},
            "USDC": {"address": Web3.to_checksum_address("0x48249feEb47a8453023f702f15CF00206eeBdF08"), "decimals": 6},
            "WPHRS": {"address": Web3.to_checksum_address("0x253F3534e1e36B9E4a1b9A6F7b6dE47AC3e7AaD3"), "decimals": 18},
            "GOLD": {"address": Web3.to_checksum_address("0x77f532df5f46DdFf1c97CDae3115271A523fa0f4"), "decimals": 18},
            "TSLA": {"address": Web3.to_checksum_address("0xCDA3DF4AAB8a571688fE493EB1BdC1Ad210C09E4"), "decimals": 18},
            "BTC": {"address": Web3.to_checksum_address("0xA4a967FC7cF0E9815bF5c2700A055813628b65BE"), "decimals": 18},
            "NVIDIA": {"address": Web3.to_checksum_address("0x3299cc551B2a39926Bf14144e65630e533dF6944"), "decimals": 18}
        }

    async def mint_token_faucet(self, web3, private_key: str, token_symbol: str, amount: float = 100):
        """Минт токенов из фаусета"""
        try:
            if token_symbol not in self.tokens:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Unknown token: {token_symbol}{Style.RESET_ALL}")
                return None

            account = Account.from_key(private_key)
            token_info = self.tokens[token_symbol]
            
            # Создаем контракт для минтинга
            contract = web3.eth.contract(
                address=self.MINT_ROUTER_ADDRESS,
                abi=self.MINT_CONTRACT_ABI
            )
            
            # Вычисляем amount с учетом decimals
            amount_wei = int(amount * (10 ** token_info["decimals"]))
            
            # Создаем транзакцию
            tx = contract.functions.mint(
                token_info["address"],
                account.address,
                amount_wei
            ).build_transaction({
                'from': account.address,
                'gas': 300000,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            })
            
            # Подписываем и отправляем
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Mint {amount} {token_symbol} transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            
            # Ждем подтверждения
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Successfully minted {amount} {token_symbol}!{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                raise Exception("Mint transaction failed")

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Mint {token_symbol} error: {e}{Style.RESET_ALL}")
            return None

    async def deposit_phrs(self, web3, private_key: str, amount: float):
        """Депозит PHRS в пул ликвидности"""
        try:
            account = Account.from_key(private_key)
            
            # Проверяем баланс PHRS
            phrs_balance = await self.web3_manager.get_token_balance(web3, account.address, "PHRS")
            if phrs_balance < amount:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient PHRS balance: {phrs_balance:.6f} < {amount:.6f}{Style.RESET_ALL}")
                return None
            
            # Создаем контракт для депозита
            contract = web3.eth.contract(
                address=self.DEPOSIT_ROUTER_ADDRESS,
                abi=self.LENDING_CONTRACT_ABI
            )
            
            amount_wei = web3.to_wei(amount, 'ether')
            
            # Создаем транзакцию депозита
            tx = contract.functions.depositETH(
                "0x0000000000000000000000000000000000000000",  # lending pool placeholder
                account.address,
                0  # referral code
            ).build_transaction({
                'from': account.address,
                'value': amount_wei,
                'gas': 400000,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            })
            
            # Подписываем и отправляем
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Deposit {amount} PHRS transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            
            # Ждем подтверждения
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Successfully deposited {amount} PHRS!{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                raise Exception("Deposit transaction failed")

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Deposit PHRS error: {e}{Style.RESET_ALL}")
            return None

    async def supply_token(self, web3, private_key: str, token_symbol: str, amount: float):
        """Поставка токенов в lending пул"""
        try:
            if token_symbol not in self.tokens:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Unknown token: {token_symbol}{Style.RESET_ALL}")
                return None

            account = Account.from_key(private_key)
            token_info = self.tokens[token_symbol]
            
            # Проверяем баланс токена
            token_balance = await self.web3_manager.get_token_balance(web3, account.address, token_info["address"])
            if token_balance < amount:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient {token_symbol} balance: {token_balance:.6f} < {amount:.6f}{Style.RESET_ALL}")
                return None
            
            # Одобряем токен
            amount_wei = int(amount * (10 ** token_info["decimals"]))
            approval_success = await self.web3_manager.approve_token(
                web3, private_key, token_info["address"], self.SUPPLY_ROUTER_ADDRESS, amount_wei
            )
            
            if not approval_success:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Failed to approve {token_symbol} for supply{Style.RESET_ALL}")
                return None
            
            # Создаем контракт для supply
            contract = web3.eth.contract(
                address=self.SUPPLY_ROUTER_ADDRESS,
                abi=self.LENDING_CONTRACT_ABI
            )
            
            # Создаем транзакцию supply
            tx = contract.functions.supply(
                token_info["address"],
                amount_wei,
                account.address,
                0  # referral code
            ).build_transaction({
                'from': account.address,
                'gas': 400000,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            })
            
            # Подписываем и отправляем
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Supply {amount} {token_symbol} transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            
            # Ждем подтверждения
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Successfully supplied {amount} {token_symbol}!{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                raise Exception("Supply transaction failed")

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Supply {token_symbol} error: {e}{Style.RESET_ALL}")
            return None

    async def borrow_token(self, web3, private_key: str, token_symbol: str, amount: float):
        """Заем токенов из lending пула"""
        try:
            if token_symbol not in self.tokens:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Unknown token: {token_symbol}{Style.RESET_ALL}")
                return None

            account = Account.from_key(private_key)
            token_info = self.tokens[token_symbol]
            
            # Создаем контракт для borrow
            contract = web3.eth.contract(
                address=self.SUPPLY_ROUTER_ADDRESS,
                abi=self.LENDING_CONTRACT_ABI
            )
            
            amount_wei = int(amount * (10 ** token_info["decimals"]))
            
            # Создаем транзакцию borrow
            tx = contract.functions.borrow(
                token_info["address"],
                amount_wei,
                2,  # variable interest rate mode
                0,  # referral code
                account.address
            ).build_transaction({
                'from': account.address,
                'gas': 400000,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            })
            
            # Подписываем и отправляем
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Borrow {amount} {token_symbol} transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            
            # Ждем подтверждения
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Successfully borrowed {amount} {token_symbol}!{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                raise Exception("Borrow transaction failed")

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Borrow {token_symbol} error: {e}{Style.RESET_ALL}")
            return None

    async def withdraw_token(self, web3, private_key: str, token_symbol: str, amount: float):
        """Вывод токенов из lending пула"""
        try:
            if token_symbol not in self.tokens:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Unknown token: {token_symbol}{Style.RESET_ALL}")
                return None

            account = Account.from_key(private_key)
            token_info = self.tokens[token_symbol]
            
            # Создаем контракт для withdraw
            contract = web3.eth.contract(
                address=self.SUPPLY_ROUTER_ADDRESS,
                abi=self.LENDING_CONTRACT_ABI
            )
            
            amount_wei = int(amount * (10 ** token_info["decimals"]))
            
            # Создаем транзакцию withdraw
            tx = contract.functions.withdraw(
                token_info["address"],
                amount_wei,
                account.address
            ).build_transaction({
                'from': account.address,
                'gas': 400000,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            })
            
            # Подписываем и отправляем
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Withdraw {amount} {token_symbol} transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            
            # Ждем подтверждения
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Successfully withdrawn {amount} {token_symbol}!{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                raise Exception("Withdraw transaction failed")

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Withdraw {token_symbol} error: {e}{Style.RESET_ALL}")
            return None

    async def mint_all_tokens(self, web3, private_key: str, amount_per_token: float = 100, delay_between_mints: int = 5):
        """Минт всех доступных токенов"""
        try:
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Starting mint of all tokens ({amount_per_token} each)...{Style.RESET_ALL}")
            
            successful_mints = 0
            total_tokens = len(self.tokens)
            
            for i, (symbol, _) in enumerate(self.tokens.items()):
                Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Minting {symbol} ({i+1}/{total_tokens})...{Style.RESET_ALL}")
                
                result = await self.mint_token_faucet(web3, private_key, symbol, amount_per_token)
                
                if result:
                    successful_mints += 1
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ {symbol} mint successful{Style.RESET_ALL}")
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}❌ {symbol} mint failed{Style.RESET_ALL}")
                
                # Задержка между минтами (кроме последнего)
                if i < total_tokens - 1:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Waiting {delay_between_mints} seconds...{Style.RESET_ALL}")
                    await asyncio.sleep(delay_between_mints)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Token minting completed: {successful_mints}/{total_tokens} successful{Style.RESET_ALL}")
            return successful_mints > 0

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Mint all tokens error: {e}{Style.RESET_ALL}")
            return False

    async def supply_all_tokens(self, web3, private_key: str, amount_per_token: float, delay_between_operations: int = 10):
        """Supply всех доступных токенов в пул"""
        try:
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Starting supply of all tokens ({amount_per_token} each)...{Style.RESET_ALL}")
            
            successful_supplies = 0
            
            # Включаем WPHRS в список для supply
            tokens_to_supply = list(self.tokens.keys())
            
            for i, symbol in enumerate(tokens_to_supply):
                Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Supplying {symbol} ({i+1}/{len(tokens_to_supply)})...{Style.RESET_ALL}")
                
                result = await self.supply_token(web3, private_key, symbol, amount_per_token)
                
                if result:
                    successful_supplies += 1
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ {symbol} supply successful{Style.RESET_ALL}")
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}❌ {symbol} supply failed{Style.RESET_ALL}")
                
                # Задержка между операциями (кроме последней)
                if i < len(tokens_to_supply) - 1:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Waiting {delay_between_operations} seconds...{Style.RESET_ALL}")
                    await asyncio.sleep(delay_between_operations)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Token supply completed: {successful_supplies}/{len(tokens_to_supply)} successful{Style.RESET_ALL}")
            return successful_supplies > 0

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Supply all tokens error: {e}{Style.RESET_ALL}")
            return False

    async def borrow_all_tokens(self, web3, private_key: str, amount_per_token: float, delay_between_operations: int = 10):
        """Заем всех доступных токенов"""
        try:
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Starting borrow of all tokens ({amount_per_token} each)...{Style.RESET_ALL}")
            
            successful_borrows = 0
            tokens_to_borrow = list(self.tokens.keys())
            
            for i, symbol in enumerate(tokens_to_borrow):
                Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Borrowing {symbol} ({i+1}/{len(tokens_to_borrow)})...{Style.RESET_ALL}")
                
                result = await self.borrow_token(web3, private_key, symbol, amount_per_token)
                
                if result:
                    successful_borrows += 1
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ {symbol} borrow successful{Style.RESET_ALL}")
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}❌ {symbol} borrow failed{Style.RESET_ALL}")
                
                # Задержка между операциями (кроме последней)
                if i < len(tokens_to_borrow) - 1:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Waiting {delay_between_operations} seconds...{Style.RESET_ALL}")
                    await asyncio.sleep(delay_between_operations)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Token borrow completed: {successful_borrows}/{len(tokens_to_borrow)} successful{Style.RESET_ALL}")
            return successful_borrows > 0

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Borrow all tokens error: {e}{Style.RESET_ALL}")
            return False

    async def withdraw_all_tokens(self, web3, private_key: str, amount_per_token: float, delay_between_operations: int = 10):
        """Вывод всех токенов из пула"""
        try:
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Starting withdraw of all tokens ({amount_per_token} each)...{Style.RESET_ALL}")
            
            successful_withdraws = 0
            tokens_to_withdraw = list(self.tokens.keys())
            
            for i, symbol in enumerate(tokens_to_withdraw):
                Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Withdrawing {symbol} ({i+1}/{len(tokens_to_withdraw)})...{Style.RESET_ALL}")
                
                result = await self.withdraw_token(web3, private_key, symbol, amount_per_token)
                
                if result:
                    successful_withdraws += 1
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ {symbol} withdraw successful{Style.RESET_ALL}")
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}❌ {symbol} withdraw failed{Style.RESET_ALL}")
                
                # Задержка между операциями (кроме последней)
                if i < len(tokens_to_withdraw) - 1:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Waiting {delay_between_operations} seconds...{Style.RESET_ALL}")
                    await asyncio.sleep(delay_between_operations)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Token withdraw completed: {successful_withdraws}/{len(tokens_to_withdraw)} successful{Style.RESET_ALL}")
            return successful_withdraws > 0

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Withdraw all tokens error: {e}{Style.RESET_ALL}")
            return False

    async def full_defi_cycle(self, web3, private_key: str, deposit_amount: float = 0.01, token_amount: float = 10, borrow_amount: float = 5, withdraw_amount: float = 5):
        """Полный цикл DeFi операций"""
        try:
            account = Account.from_key(private_key)
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Starting full DeFi cycle for {account.address[:8]}...{Style.RESET_ALL}")
            
            operations_completed = 0
            
            # 1. Минт всех токенов
            Logger.log(f"{Fore.BLUE + Style.BRIGHT}Step 1: Minting tokens...{Style.RESET_ALL}")
            if await self.mint_all_tokens(web3, private_key, 100, 3):
                operations_completed += 1
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ Token minting completed{Style.RESET_ALL}")
            else:
                Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Token minting failed{Style.RESET_ALL}")
            
            await asyncio.sleep(5)
            
            # 2. Депозит PHRS
            Logger.log(f"{Fore.BLUE + Style.BRIGHT}Step 2: Depositing PHRS...{Style.RESET_ALL}")
            if await self.deposit_phrs(web3, private_key, deposit_amount):
                operations_completed += 1
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ PHRS deposit completed{Style.RESET_ALL}")
            else:
                Logger.log(f"{Fore.RED + Style.BRIGHT}❌ PHRS deposit failed{Style.RESET_ALL}")
            
            await asyncio.sleep(5)
            
            # 3. Supply токенов
            Logger.log(f"{Fore.BLUE + Style.BRIGHT}Step 3: Supplying tokens...{Style.RESET_ALL}")
            if await self.supply_all_tokens(web3, private_key, token_amount, 5):
                operations_completed += 1
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ Token supply completed{Style.RESET_ALL}")
            else:
                Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Token supply failed{Style.RESET_ALL}")
            
            await asyncio.sleep(10)
            
            # 4. Заем токенов
            Logger.log(f"{Fore.BLUE + Style.BRIGHT}Step 4: Borrowing tokens...{Style.RESET_ALL}")
            if await self.borrow_all_tokens(web3, private_key, borrow_amount, 5):
                operations_completed += 1
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ Token borrow completed{Style.RESET_ALL}")
            else:
                Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Token borrow failed{Style.RESET_ALL}")
            
            await asyncio.sleep(10)
            
            # 5. Частичный вывод токенов
            Logger.log(f"{Fore.BLUE + Style.BRIGHT}Step 5: Withdrawing tokens...{Style.RESET_ALL}")
            if await self.withdraw_all_tokens(web3, private_key, withdraw_amount, 5):
                operations_completed += 1
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ Token withdraw completed{Style.RESET_ALL}")
            else:
                Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Token withdraw failed{Style.RESET_ALL}")
            
            # Финальная статистика
            success_rate = (operations_completed / 5) * 100
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}DeFi cycle completed: {operations_completed}/5 operations successful ({success_rate:.1f}%){Style.RESET_ALL}")
            
            return operations_completed >= 3  # Считаем успешным если 3+ операций прошли

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Full DeFi cycle error: {e}{Style.RESET_ALL}")
            return False

    async def get_lending_info(self, web3, address: str):
        """Получение информации о lending позициях"""
        try:
            info = {}
            
            # Получаем балансы всех токенов
            for symbol, token_info in self.tokens.items():
                balance = await self.web3_manager.get_token_balance(web3, address, token_info["address"])
                info[symbol] = balance
            
            # Получаем баланс PHRS
            phrs_balance = await self.web3_manager.get_token_balance(web3, address, "PHRS")
            info["PHRS"] = phrs_balance
            
            return info
            
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Get lending info error: {e}{Style.RESET_ALL}")
            return None