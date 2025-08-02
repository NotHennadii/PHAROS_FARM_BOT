#!/usr/bin/env python3

import asyncio
import sys
import os
from colorama import Fore, Style, init

# Инициализируем colorama
init()

# Импортируем модули
try:
    from web3_manager import Web3Manager
    from brokex import BrokexManager
    from openfi import OpenFiManager
    from utils import Logger
except ImportError as e:
    print(f"{Fore.RED + Style.BRIGHT}Import error: {e}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW + Style.BRIGHT}Make sure all required modules are in the same directory{Style.RESET_ALL}")
    sys.exit(1)

class ModuleTester:
    def __init__(self):
        self.web3_manager = Web3Manager()
        self.brokex_manager = BrokexManager(self.web3_manager)
        self.openfi_manager = OpenFiManager(self.web3_manager)

    async def test_web3_connection(self):
        """Тест подключения к Web3"""
        try:
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Testing Web3 connection...{Style.RESET_ALL}")
            web3 = await self.web3_manager.get_web3_connection()
            block_number = web3.eth.get_block_number()
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ Web3 connected! Latest block: {block_number}{Style.RESET_ALL}")
            return True
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Web3 connection failed: {e}{Style.RESET_ALL}")
            return False

    async def test_brokex_module(self, test_address: str):
        """Тест модуля Brokex"""
        try:
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Testing Brokex module...{Style.RESET_ALL}")
            
            web3 = await self.web3_manager.get_web3_connection()
            
            # Тест получения информации для торговли
            trading_info = await self.brokex_manager.get_trading_info(web3, test_address)
            
            if trading_info:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ Brokex module working!{Style.RESET_ALL}")
                Logger.log(f"   USDT Balance: {trading_info['usdt_balance']:.6f}")
                Logger.log(f"   PHRS Balance: {trading_info['phrs_balance']:.6f}")
                Logger.log(f"   Can Trade: {trading_info['can_trade']}")
                
                # Тест получения баланса USDT
                usdt_balance = await self.brokex_manager.get_usdt_balance(web3, test_address)
                Logger.log(f"   Direct USDT Check: {usdt_balance:.6f}")
                
                return True
            else:
                Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Brokex module failed to get trading info{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Brokex module test failed: {e}{Style.RESET_ALL}")
            return False

    async def test_openfi_module(self, test_address: str):
        """Тест модуля OpenFi"""
        try:
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Testing OpenFi module...{Style.RESET_ALL}")
            
            web3 = await self.web3_manager.get_web3_connection()
            
            # Тест получения информации о lending
            lending_info = await self.openfi_manager.get_lending_info(web3, test_address)
            
            if lending_info:
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ OpenFi module working!{Style.RESET_ALL}")
                Logger.log(f"   Token balances:")
                for token, balance in lending_info.items():
                    Logger.log(f"     {token}: {balance:.6f}")
                
                # Проверяем доступные токены
                Logger.log(f"   Available tokens: {list(self.openfi_manager.tokens.keys())}")
                return True
            else:
                Logger.log(f"{Fore.RED + Style.BRIGHT}❌ OpenFi module failed to get lending info{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}❌ OpenFi module test failed: {e}{Style.RESET_ALL}")
            return False

    async def test_contract_addresses(self):
        """Тест доступности контрактов"""
        try:
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Testing contract addresses...{Style.RESET_ALL}")
            
            web3 = await self.web3_manager.get_web3_connection()
            
            contracts_to_test = [
                ("Brokex USDT", self.brokex_manager.USDT_CONTRACT_ADDRESS),
                ("Brokex Trade Router", self.brokex_manager.TRADE_ROUTER_ADDRESS),
                ("OpenFi Mint Router", self.openfi_manager.MINT_ROUTER_ADDRESS),
                ("OpenFi Deposit Router", self.openfi_manager.DEPOSIT_ROUTER_ADDRESS),
                ("OpenFi Supply Router", self.openfi_manager.SUPPLY_ROUTER_ADDRESS),
            ]
            
            all_good = True
            
            for name, address in contracts_to_test:
                try:
                    code = web3.eth.get_code(address)
                    if code and code != '0x':
                        Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ {name}: {address} - Contract found{Style.RESET_ALL}")
                    else:
                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️  {name}: {address} - No contract code{Style.RESET_ALL}")
                        all_good = False
                except Exception as e:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}❌ {name}: {address} - Error: {e}{Style.RESET_ALL}")
                    all_good = False
            
            return all_good
            
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Contract address test failed: {e}{Style.RESET_ALL}")
            return False

    async def test_token_contracts(self, test_address: str):
        """Тест токенов OpenFi"""
        try:
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Testing OpenFi token contracts...{Style.RESET_ALL}")
            
            web3 = await self.web3_manager.get_web3_connection()
            
            all_good = True
            
            for symbol, token_info in self.openfi_manager.tokens.items():
                try:
                    balance = await self.web3_manager.get_token_balance(web3, test_address, token_info["address"])
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ {symbol}: {balance:.6f} (decimals: {token_info['decimals']}){Style.RESET_ALL}")
                except Exception as e:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}❌ {symbol}: Error getting balance - {e}{Style.RESET_ALL}")
                    all_good = False
            
            return all_good
            
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Token contracts test failed: {e}{Style.RESET_ALL}")
            return False

    async def run_all_tests(self, test_address: str = None):
        """Запуск всех тестов"""
        Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
        Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Starting Module Tests{Style.RESET_ALL}")
        Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
        
        if not test_address:
            test_address = "0x0000000000000000000000000000000000000000"  # Placeholder address
            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Using placeholder address for tests{Style.RESET_ALL}")
        else:
            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Using test address: {test_address[:8]}...{test_address[-6:]}{Style.RESET_ALL}")
        
        tests = [
            ("Web3 Connection", self.test_web3_connection()),
            ("Contract Addresses", self.test_contract_addresses()),
            ("Brokex Module", self.test_brokex_module(test_address)),
            ("OpenFi Module", self.test_openfi_module(test_address)),
            ("Token Contracts", self.test_token_contracts(test_address)),
        ]
        
        results = []
        
        for test_name, test_coro in tests:
            Logger.log(f"\n{Fore.BLUE + Style.BRIGHT}Running {test_name}...{Style.RESET_ALL}")
            try:
                result = await test_coro
                results.append((test_name, result))
            except Exception as e:
                Logger.log(f"{Fore.RED + Style.BRIGHT}❌ {test_name} crashed: {e}{Style.RESET_ALL}")
                results.append((test_name, False))
        
        # Итоговый отчет
        Logger.log(f"\n{Fore.MAGENTA + Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
        Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Test Results Summary{Style.RESET_ALL}")
        Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            color = Fore.GREEN if result else Fore.RED
            Logger.log(f"{color + Style.BRIGHT}{status} - {test_name}{Style.RESET_ALL}")
            if result:
                passed += 1
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        Logger.log(f"\n{Fore.CYAN + Style.BRIGHT}Overall: {passed}/{total} tests passed ({success_rate:.1f}%){Style.RESET_ALL}")
        
        if passed == total:
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}🎉 All modules are working correctly!{Style.RESET_ALL}")
            return True
        else:
            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️  Some tests failed. Check the errors above.{Style.RESET_ALL}")
            return False

def main():
    """Основная функция"""
    try:
        # Проверяем наличие test address в аргументах
        test_address = None
        if len(sys.argv) > 1:
            test_address = sys.argv[1]
            if not test_address.startswith('0x') or len(test_address) != 42:
                print(f"{Fore.RED + Style.BRIGHT}Invalid address format. Please provide a valid Ethereum address.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW + Style.BRIGHT}Usage: python test_modules.py [wallet_address]{Style.RESET_ALL}")
                return
        
        # Или пытаемся получить из accounts.txt
        if not test_address and os.path.exists('accounts.txt'):
            try:
                with open('accounts.txt', 'r') as f:
                    private_keys = [line.strip() for line in f.read().splitlines() if line.strip()]
                
                if private_keys:
                    from eth_account import Account
                    test_account = Account.from_key(private_keys[0])
                    test_address = test_account.address
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}Using first address from accounts.txt{Style.RESET_ALL}")
            except Exception as e:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Could not read from accounts.txt: {e}{Style.RESET_ALL}")
        
        # Запускаем тесты
        tester = ModuleTester()
        
        async def run_tests():
            return await tester.run_all_tests(test_address)
        
        success = asyncio.run(run_tests())
        
        if success:
            print(f"\n{Fore.GREEN + Style.BRIGHT}✅ Module testing completed successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN + Style.BRIGHT}You can now run the main bot with confidence.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW + Style.BRIGHT}⚠️  Some issues were found. Check the logs above.{Style.RESET_ALL}")
            print(f"{Fore.CYAN + Style.BRIGHT}The bot may still work, but some features might not be available.{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW + Style.BRIGHT}Test interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Test failed with error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()