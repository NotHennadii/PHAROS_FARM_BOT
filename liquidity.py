#!/usr/bin/env python3

import time
from web3 import Web3
from eth_account import Account
from config import Config
from utils import Logger
from colorama import Fore, Style

class LiquidityManager:
    def __init__(self, web3_manager):
        self.config = Config()
        self.web3_manager = web3_manager

    async def add_liquidity(self, web3, private_key: str, token0: str, token1: str, amount0: int, amount1: int):
        """Добавление ликвидности через DVM пул как в JS версии"""
        try:
            account = Account.from_key(private_key)
            
            # Проверяем балансы токенов
            usdc_balance = await self.web3_manager.get_token_balance(web3, account.address, token0)
            usdt_balance = await self.web3_manager.get_token_balance(web3, account.address, token1)
            
            required_usdc = amount0 / 1000000  # 6 decimals
            required_usdt = amount1 / 1000000  # 6 decimals
            
            if usdc_balance < required_usdc or usdt_balance < required_usdt:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient tokens. USDC: {usdc_balance:.6f}/{required_usdc:.6f}, USDT: {usdt_balance:.6f}/{required_usdt:.6f}{Style.RESET_ALL}")
                return None
            
            # Одобряем токены
            await self.web3_manager.approve_token(web3, private_key, token0, self.config.LIQUIDITY_CONTRACT, amount0)
            await self.web3_manager.approve_token(web3, private_key, token1, self.config.LIQUIDITY_CONTRACT, amount1)
            
            # Используем правильный ABI для addDVMLiquidity
            contract = web3.eth.contract(
                address=self.config.LIQUIDITY_CONTRACT,
                abi=self.config.LIQUIDITY_CONTRACT_ABI
            )
            
            # Параметры как в JS версии
            dvm_address = self.config.DVM_POOL_ADDRESS
            base_in_amount = amount0  # USDC amount
            quote_in_amount = amount1  # USDT amount
            base_min_amount = int(base_in_amount * 999 // 1000)  # 0.1% slippage
            quote_min_amount = int(quote_in_amount * 999 // 1000)  # 0.1% slippage
            flag = 0
            deadline = int(time.time()) + 600
            
            tx = contract.functions.addDVMLiquidity(
                dvm_address,
                base_in_amount,
                quote_in_amount,
                base_min_amount,
                quote_min_amount,
                flag,
                deadline
            ).build_transaction({
                'from': account.address,
                'gas': 600000,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Add Liquidity transaction sent! TX: {tx_hash.hex()}{Style.RESET_ALL}")
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Liquidity added successfully!{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                raise Exception("Add liquidity transaction failed")
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Add liquidity error: {e}{Style.RESET_ALL}")
            return None
