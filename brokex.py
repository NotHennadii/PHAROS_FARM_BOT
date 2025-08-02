#!/usr/bin/env python3

import asyncio
import random
import time
from web3 import Web3
from eth_account import Account
from config import Config
from utils import Logger
from colorama import Fore, Style

class BrokexManager:
    def __init__(self, web3_manager):
        self.config = Config()
        self.web3_manager = web3_manager
        
        # Адреса контрактов Brokex (преобразованы в checksum формат)
        self.USDT_CONTRACT_ADDRESS = Web3.to_checksum_address("0x78ac5e2d8a78a8b8e6d10c7b7274b03c10c91cef")
        self.TRADE_ROUTER_ADDRESS = Web3.to_checksum_address("0x01f61eb2e4667c6188f4c1c87c0f529155bf888c")
        
        # ABI для торговых операций
        self.ORDER_CONTRACT_ABI = [
            {
                "name": "createPendingOrder",
                "type": "function",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "assetIndex", "type": "uint256" },
                    { "internalType": "bool", "name": "isLong", "type": "bool" },
                    { "internalType": "uint256", "name": "usdSize", "type": "uint256" },
                    { "internalType": "uint256", "name": "leverage", "type": "uint256" },
                    { "internalType": "uint256", "name": "slPrice", "type": "uint256" },
                    { "internalType": "uint256", "name": "tpPrice", "type": "uint256" }
                ],
                "outputs": []
            }
        ]
        
        # Торговые пары с индексами
        self.trading_pairs = [
            { "name": "BTC_USDT", "index": 0 },
            { "name": "ETH_USDT", "index": 1 },
            { "name": "SOL_USDT", "index": 10 },
            { "name": "XRP_USDT", "index": 14 },
        ]

    async def get_usdt_balance(self, web3, address: str):
        """Получение баланса USDT"""
        try:
            return await self.web3_manager.get_token_balance(web3, address, self.USDT_CONTRACT_ADDRESS)
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Error getting USDT balance: {e}{Style.RESET_ALL}")
            return 0

    async def approve_usdt_for_trading(self, web3, private_key: str, amount: float):
        """Одобрение USDT для торговых операций"""
        try:
            return await self.web3_manager.approve_token(
                web3, 
                private_key, 
                self.USDT_CONTRACT_ADDRESS, 
                self.TRADE_ROUTER_ADDRESS, 
                int(amount * 10**6)  # USDT имеет 6 decimals
            )
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}USDT approval error: {e}{Style.RESET_ALL}")
            return False

    async def create_trade_order(self, web3, private_key: str, pair_index: int, is_long: bool, amount_usdt: float, leverage: int = 5):
        """Создание торгового ордера"""
        try:
            account = Account.from_key(private_key)
            
            # Проверяем баланс USDT
            usdt_balance = await self.get_usdt_balance(web3, account.address)
            if usdt_balance < amount_usdt:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient USDT balance: {usdt_balance:.6f} < {amount_usdt:.6f}{Style.RESET_ALL}")
                return None

            # Одобряем USDT
            approval_success = await self.approve_usdt_for_trading(web3, private_key, amount_usdt)
            if not approval_success:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Failed to approve USDT for trading{Style.RESET_ALL}")
                return None

            # Создаем контракт для торговли
            contract = web3.eth.contract(
                address=self.TRADE_ROUTER_ADDRESS,
                abi=self.ORDER_CONTRACT_ABI
            )

            # Параметры ордера
            amount_wei = int(amount_usdt * 10**6)  # USDT 6 decimals
            
            # Создаем транзакцию
            tx = contract.functions.createPendingOrder(
                pair_index,      # assetIndex
                is_long,         # isLong
                amount_wei,      # usdSize
                leverage,        # leverage
                0,               # slPrice (0 = no stop loss)
                0                # tpPrice (0 = no take profit)
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

            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Trade order created! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            
            # Ждем подтверждения
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Trade order confirmed! Block: #{receipt.blockNumber}{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                raise Exception("Trade order transaction failed")

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Create trade order error: {e}{Style.RESET_ALL}")
            return None

    async def execute_random_trades(self, web3, private_key: str, trade_count: int, amount_per_trade: float, min_delay: int = 10, max_delay: int = 30):
        """Выполнение серии случайных торговых операций"""
        try:
            account = Account.from_key(private_key)
            successful_trades = 0
            
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Starting {trade_count} random trades with {amount_per_trade} USDT each{Style.RESET_ALL}")
            
            for i in range(trade_count):
                # Выбираем случайную пару и направление
                pair = random.choice(self.trading_pairs)
                is_long = random.choice([True, False])
                
                pair_name = pair["name"]
                pair_index = pair["index"]
                direction = "LONG" if is_long else "SHORT"
                
                Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Trade {i+1}/{trade_count}: {direction} {pair_name}{Style.RESET_ALL}")
                
                # Проверяем баланс перед каждой сделкой
                usdt_balance = await self.get_usdt_balance(web3, account.address)
                Logger.log(f"{Fore.CYAN + Style.BRIGHT}USDT Balance: {usdt_balance:.6f}{Style.RESET_ALL}")
                
                if usdt_balance < amount_per_trade:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient balance for trade #{i+1}, stopping...{Style.RESET_ALL}")
                    break
                
                # Создаем ордер
                tx_hash = await self.create_trade_order(
                    web3, 
                    private_key, 
                    pair_index, 
                    is_long, 
                    amount_per_trade
                )
                
                if tx_hash:
                    successful_trades += 1
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ Trade {i+1} successful: {tx_hash}{Style.RESET_ALL}")
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Trade {i+1} failed{Style.RESET_ALL}")
                
                # Задержка между сделками (кроме последней)
                if i < trade_count - 1:
                    delay = random.randint(min_delay, max_delay)
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Waiting {delay} seconds before next trade...{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Trading session completed: {successful_trades}/{trade_count} successful trades{Style.RESET_ALL}")
            return successful_trades

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Execute trades error: {e}{Style.RESET_ALL}")
            return 0

    async def get_trading_info(self, web3, address: str):
        """Получение информации для торговли"""
        try:
            usdt_balance = await self.get_usdt_balance(web3, address)
            phrs_balance = await self.web3_manager.get_token_balance(web3, address, "PHRS")
            
            return {
                "usdt_balance": usdt_balance,
                "phrs_balance": phrs_balance,
                "can_trade": usdt_balance > 0
            }
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Get trading info error: {e}{Style.RESET_ALL}")
            return None

    async def simulate_day_trading(self, web3, private_key: str, total_budget_usdt: float, trades_per_session: int = 5):
        """Симуляция дневной торговли с управлением рисками"""
        try:
            account = Account.from_key(private_key)
            
            # Разделяем бюджет на количество сделок
            amount_per_trade = total_budget_usdt / trades_per_session
            
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Starting day trading simulation:{Style.RESET_ALL}")
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Total Budget: {total_budget_usdt} USDT{Style.RESET_ALL}")
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Trades Planned: {trades_per_session}{Style.RESET_ALL}")
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Amount per Trade: {amount_per_trade:.6f} USDT{Style.RESET_ALL}")
            
            # Выполняем торговые операции
            successful_trades = await self.execute_random_trades(
                web3, 
                private_key, 
                trades_per_session, 
                amount_per_trade,
                min_delay=15,  # Минимум 15 секунд между сделками
                max_delay=45   # Максимум 45 секунд между сделками
            )
            
            # Финальная статистика
            final_info = await self.get_trading_info(web3, account.address)
            if final_info:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Day Trading Results:{Style.RESET_ALL}")
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Successful Trades: {successful_trades}/{trades_per_session}{Style.RESET_ALL}")
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Final USDT Balance: {final_info['usdt_balance']:.6f}{Style.RESET_ALL}")
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Success Rate: {(successful_trades/trades_per_session)*100:.1f}%{Style.RESET_ALL}")
            
            return successful_trades > 0

        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Day trading simulation error: {e}{Style.RESET_ALL}")
            return False