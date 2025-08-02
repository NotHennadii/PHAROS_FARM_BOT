#!/usr/bin/env python3

from web3 import Web3
from eth_account import Account
from config import Config
from utils import Logger
from colorama import Fore, Style

class Web3Manager:
    def __init__(self):
        self.config = Config()

    async def get_web3_connection(self, proxy=None):
        """Создание Web3 подключения с поддержкой прокси"""
        try:
            web3 = Web3(Web3.HTTPProvider(self.config.RPC_URL))
            
            if not web3.is_connected():
                raise Exception("Failed to connect to RPC")
                
            web3.eth.get_block_number()
            return web3
            
        except Exception as e:
            raise Exception(f"Web3 connection failed: {str(e)}")

    async def get_token_balance(self, web3, address: str, token_address: str):
        """Получение баланса токена"""
        try:
            if token_address.upper() == "PHRS" or token_address.lower() == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee":
                balance = web3.eth.get_balance(address)
                return balance / (10 ** 18)
            else:
                contract = web3.eth.contract(
                    address=token_address,
                    abi=self.config.ERC20_ABI
                )
                balance = contract.functions.balanceOf(address).call()
                decimals = contract.functions.decimals().call()
                return balance / (10 ** decimals)
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Get balance error: {e}{Style.RESET_ALL}")
            return 0

    async def approve_token(self, web3, private_key: str, token_address: str, spender: str, amount: int):
        """Одобрение токена для использования"""
        try:
            account = Account.from_key(private_key)
            contract = web3.eth.contract(
                address=token_address,
                abi=self.config.ERC20_ABI
            )
            
            current_allowance = contract.functions.allowance(account.address, spender).call()
            if current_allowance >= amount:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Token already approved{Style.RESET_ALL}")
                return True
            
            max_amount = 2**256 - 1
            
            tx = contract.functions.approve(spender, max_amount).build_transaction({
                'from': account.address,
                'gas': 100000,
                'maxFeePerGas': web3.to_wei(2, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
                'nonce': web3.eth.get_transaction_count(account.address, 'pending'),
                'chainId': self.config.CHAIN_ID
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            # Исправление: используем raw_transaction вместо rawTransaction
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Token approved successfully{Style.RESET_ALL}")
                return True
            else:
                Logger.log(f"{Fore.RED + Style.BRIGHT}Token approval failed{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Approval error: {e}{Style.RESET_ALL}")
            return False
