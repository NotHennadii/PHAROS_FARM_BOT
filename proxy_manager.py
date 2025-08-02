#!/usr/bin/env python3

"""
Отдельный скрипт для управления прокси аккаунтов
Можно запускать независимо от основного бота
"""

import os
import sys
from colorama import Fore, Style, init
from account_proxy_manager import AccountProxyManager

# Инициализируем colorama
init()

def load_private_keys():
    """Загрузка приватных ключей"""
    try:
        with open('accounts.txt', 'r') as f:
            keys = [line.strip() for line in f.read().splitlines() if line.strip()]
        return keys
    except FileNotFoundError:
        print(f"{Fore.RED + Style.BRIGHT}accounts.txt not found!{Style.RESET_ALL}")
        return []

def main_menu():
    """Главное меню управления прокси"""
    manager = AccountProxyManager()
    
    while True:
        print(f"\n{Fore.CYAN + Style.BRIGHT}=== Proxy Manager ==={Style.RESET_ALL}")
        print("1. Interactive setup (full configuration)")
        print("2. View current configuration")
        print("3. Quick enable/disable proxy for account")
        print("4. Set proxy for specific account")
        print("5. Auto-assign proxies to all accounts")
        print("6. Disable all proxies")
        print("7. Test proxy configuration")
        print("8. Export configuration")
        print("9. Import configuration")
        print("0. Exit")
        
        choice = input(f"\n{Fore.YELLOW + Style.BRIGHT}Enter your choice [0-9]: {Style.RESET_ALL}").strip()
        
        if choice == "1":
            manager.interactive_setup()
        elif choice == "2":
            view_configuration(manager)
        elif choice == "3":
            quick_toggle_proxy(manager)
        elif choice == "4":
            set_proxy_for_account(manager)
        elif choice == "5":
            auto_assign_all(manager)
        elif choice == "6":
            disable_all_proxies(manager)
        elif choice == "7":
            test_proxy_config(manager)
        elif choice == "8":
            export_configuration(manager)
        elif choice == "9":
            import_configuration(manager)
        elif choice == "0":
            print(f"{Fore.GREEN + Style.BRIGHT}Goodbye!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED + Style.BRIGHT}Invalid choice. Please try again.{Style.RESET_ALL}")

def view_configuration(manager):
    """Просмотр текущей конфигурации"""
    try:
        private_keys = load_private_keys()
        
        if not private_keys:
            print(f"{Fore.RED + Style.BRIGHT}No accounts found in accounts.txt{Style.RESET_ALL}")
            return
        
        manager.show_current_config(private_keys)
        
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error viewing configuration: {e}{Style.RESET_ALL}")

def quick_toggle_proxy(manager):
    """Быстрое включение/отключение прокси для аккаунта"""
    try:
        from eth_account import Account
        
        private_keys = load_private_keys()
        if not private_keys:
            print(f"{Fore.RED + Style.BRIGHT}No accounts found{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN + Style.BRIGHT}=== Quick Proxy Toggle ==={Style.RESET_ALL}")
        
        # Показываем список аккаунтов
        for i, private_key in enumerate(private_keys):
            try:
                account = Account.from_key(private_key)
                address = account.address
                is_enabled = manager.is_proxy_enabled_for_account(address)
                status = "✅" if is_enabled else "❌"
                print(f"{i+1}. {address[:8]}...{address[-6:]} {status}")
            except:
                print(f"{i+1}. Invalid key")
        
        # Выбираем аккаунт
        try:
            account_num = int(input(f"\n{Fore.YELLOW + Style.BRIGHT}Select account number: {Style.RESET_ALL}")) - 1
            if 0 <= account_num < len(private_keys):
                account = Account.from_key(private_keys[account_num])
                address = account.address
                
                current_status = manager.is_proxy_enabled_for_account(address)
                action = "disable" if current_status else "enable"
                
                confirm = input(f"{Fore.CYAN + Style.BRIGHT}Do you want to {action} proxy for {address[:8]}...? [y/n]: {Style.RESET_ALL}")
                
                if confirm.lower() == 'y':
                    if current_status:
                        manager.disable_proxy_for_account(address)
                        print(f"{Fore.GREEN + Style.BRIGHT}Proxy disabled for {address[:8]}...{Style.RESET_ALL}")
                    else:
                        # Включаем с автоназначением
                        proxies = manager.load_proxies()
                        if proxies:
                            proxy_index = account_num % len(proxies)
                            manager.account_proxy_config[address] = {
                                "use_proxy": True,
                                "proxy": None,
                                "proxy_index": proxy_index
                            }
                            manager.save_config()
                            print(f"{Fore.GREEN + Style.BRIGHT}Proxy enabled for {address[:8]}... (using proxy #{proxy_index + 1}){Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED + Style.BRIGHT}No proxies available in proxy.txt{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED + Style.BRIGHT}Invalid account number{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED + Style.BRIGHT}Please enter a valid number{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error in quick toggle: {e}{Style.RESET_ALL}")

def set_proxy_for_account(manager):
    """Установка прокси для конкретного аккаунта"""
    try:
        from eth_account import Account
        
        private_keys = load_private_keys()
        if not private_keys:
            print(f"{Fore.RED + Style.BRIGHT}No accounts found{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN + Style.BRIGHT}=== Set Proxy for Account ==={Style.RESET_ALL}")
        
        # Показываем список аккаунтов
        for i, private_key in enumerate(private_keys):
            try:
                account = Account.from_key(private_key)
                address = account.address
                print(f"{i+1}. {address[:8]}...{address[-6:]}")
            except:
                print(f"{i+1}. Invalid key")
        
        # Выбираем аккаунт
        try:
            account_num = int(input(f"\n{Fore.YELLOW + Style.BRIGHT}Select account number: {Style.RESET_ALL}")) - 1
            if 0 <= account_num < len(private_keys):
                account = Account.from_key(private_keys[account_num])
                address = account.address
                
                print(f"\nSelected: {address[:8]}...{address[-6:]}")
                
                # Опции установки прокси
                print("\nProxy options:")
                print("1. Enter proxy manually")
                print("2. Choose from proxy list")
                print("3. Auto-assign")
                print("4. Disable proxy")
                
                option = input(f"{Fore.CYAN + Style.BRIGHT}Choose option [1-4]: {Style.RESET_ALL}").strip()
                
                if option == "1":
                    proxy = input(f"{Fore.YELLOW + Style.BRIGHT}Enter proxy (format: protocol://user:pass@ip:port): {Style.RESET_ALL}").strip()
                    if proxy:
                        manager.set_proxy_for_account(address, proxy, True)
                        print(f"{Fore.GREEN + Style.BRIGHT}Proxy set successfully{Style.RESET_ALL}")
                
                elif option == "2":
                    proxies = manager.load_proxies()
                    if proxies:
                        print(f"\nAvailable proxies:")
                        for i, proxy in enumerate(proxies):
                            print(f"{i+1}. {proxy}")
                        
                        try:
                            proxy_num = int(input(f"{Fore.CYAN + Style.BRIGHT}Choose proxy number: {Style.RESET_ALL}")) - 1
                            if 0 <= proxy_num < len(proxies):
                                manager.account_proxy_config[address] = {
                                    "use_proxy": True,
                                    "proxy": None,
                                    "proxy_index": proxy_num
                                }
                                manager.save_config()
                                print(f"{Fore.GREEN + Style.BRIGHT}Proxy assigned successfully{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.RED + Style.BRIGHT}Invalid proxy number{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED + Style.BRIGHT}Please enter a valid number{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}No proxies found in proxy.txt{Style.RESET_ALL}")
                
                elif option == "3":
                    proxies = manager.load_proxies()
                    if proxies:
                        proxy_index = account_num % len(proxies)
                        manager.account_proxy_config[address] = {
                            "use_proxy": True,
                            "proxy": None,
                            "proxy_index": proxy_index
                        }
                        manager.save_config()
                        print(f"{Fore.GREEN + Style.BRIGHT}Auto-assigned proxy #{proxy_index + 1}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}No proxies available{Style.RESET_ALL}")
                
                elif option == "4":
                    manager.disable_proxy_for_account(address)
                    print(f"{Fore.GREEN + Style.BRIGHT}Proxy disabled{Style.RESET_ALL}")
                
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid option{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED + Style.BRIGHT}Invalid account number{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED + Style.BRIGHT}Please enter a valid number{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error setting proxy: {e}{Style.RESET_ALL}")

def auto_assign_all(manager):
    """Автоназначение прокси для всех аккаунтов"""
    try:
        private_keys = load_private_keys()
        proxies = manager.load_proxies()
        
        if not private_keys:
            print(f"{Fore.RED + Style.BRIGHT}No accounts found{Style.RESET_ALL}")
            return
        
        if not proxies:
            print(f"{Fore.RED + Style.BRIGHT}No proxies found in proxy.txt{Style.RESET_ALL}")
            return
        
        confirm = input(f"{Fore.YELLOW + Style.BRIGHT}Auto-assign {len(proxies)} proxies to {len(private_keys)} accounts? [y/n]: {Style.RESET_ALL}")
        
        if confirm.lower() == 'y':
            manager.auto_assign_proxies(private_keys, proxies)
            print(f"{Fore.GREEN + Style.BRIGHT}Auto-assignment completed!{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN + Style.BRIGHT}Operation cancelled{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error in auto-assignment: {e}{Style.RESET_ALL}")

def disable_all_proxies(manager):
    """Отключение прокси для всех аккаунтов"""
    try:
        private_keys = load_private_keys()
        
        if not private_keys:
            print(f"{Fore.RED + Style.BRIGHT}No accounts found{Style.RESET_ALL}")
            return
        
        confirm = input(f"{Fore.YELLOW + Style.BRIGHT}Disable proxies for all {len(private_keys)} accounts? [y/n]: {Style.RESET_ALL}")
        
        if confirm.lower() == 'y':
            manager.disable_all_proxies(private_keys)
            print(f"{Fore.GREEN + Style.BRIGHT}All proxies disabled!{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN + Style.BRIGHT}Operation cancelled{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error disabling proxies: {e}{Style.RESET_ALL}")

def test_proxy_config(manager):
    """Тестирование конфигурации прокси"""
    print(f"\n{Fore.CYAN + Style.BRIGHT}=== Test Proxy Configuration ==={Style.RESET_ALL}")
    
    try:
        from utils import FileManager
        from eth_account import Account
        import aiohttp
        import asyncio
        
        async def test_proxy(proxy_url):
            """Тестирование одного прокси"""
            try:
                from aiohttp_proxy import ProxyConnector
                connector = ProxyConnector.from_url(proxy_url)
                timeout = aiohttp.ClientTimeout(total=10)
                
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    async with session.get('http://httpbin.org/ip') as response:
                        if response.status == 200:
                            data = await response.json()
                            return True, data.get('origin', 'Unknown IP')
                        else:
                            return False, f"HTTP {response.status}"
            except Exception as e:
                return False, str(e)
        
        async def test_all_proxies():
            private_keys = load_private_keys()
            if not private_keys:
                print(f"{Fore.RED + Style.BRIGHT}No accounts found{Style.RESET_ALL}")
                return
            
            proxies_to_test = set()
            
            # Собираем все уникальные прокси
            for private_key in private_keys:
                try:
                    account = Account.from_key(private_key)
                    address = account.address
                    proxy = manager.get_proxy_for_account(address)
                    if proxy:
                        proxies_to_test.add(proxy)
                except:
                    continue
            
            # Добавляем прокси из файла
            file_proxies = manager.load_proxies()
            proxies_to_test.update(file_proxies)
            
            if not proxies_to_test:
                print(f"{Fore.YELLOW + Style.BRIGHT}No proxies to test{Style.RESET_ALL}")
                return
            
            print(f"Testing {len(proxies_to_test)} unique proxies...\n")
            
            for i, proxy in enumerate(proxies_to_test, 1):
                print(f"Testing proxy {i}/{len(proxies_to_test)}: {proxy[:50]}...")
                success, result = await test_proxy(proxy)
                
                if success:
                    print(f"{Fore.GREEN + Style.BRIGHT}✅ Working - IP: {result}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Failed - {result}{Style.RESET_ALL}")
                
                print()
        
        # Запускаем тестирование
        asyncio.run(test_all_proxies())
        
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error testing proxies: {e}{Style.RESET_ALL}")

def export_configuration(manager):
    """Экспорт конфигурации"""
    try:
        import json
        
        filename = input(f"{Fore.YELLOW + Style.BRIGHT}Enter export filename (default: proxy_config_backup.json): {Style.RESET_ALL}").strip()
        if not filename:
            filename = "proxy_config_backup.json"
        
        with open(filename, 'w') as f:
            json.dump(manager.account_proxy_config, f, indent=2)
        
        print(f"{Fore.GREEN + Style.BRIGHT}Configuration exported to {filename}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error exporting configuration: {e}{Style.RESET_ALL}")

def import_configuration(manager):
    """Импорт конфигурации"""
    try:
        import json
        
        filename = input(f"{Fore.YELLOW + Style.BRIGHT}Enter import filename: {Style.RESET_ALL}").strip()
        
        if not os.path.exists(filename):
            print(f"{Fore.RED + Style.BRIGHT}File not found: {filename}{Style.RESET_ALL}")
            return
        
        with open(filename, 'r') as f:
            imported_config = json.load(f)
        
        confirm = input(f"{Fore.YELLOW + Style.BRIGHT}This will overwrite current configuration. Continue? [y/n]: {Style.RESET_ALL}")
        
        if confirm.lower() == 'y':
            manager.account_proxy_config = imported_config
            manager.save_config()
            print(f"{Fore.GREEN + Style.BRIGHT}Configuration imported successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN + Style.BRIGHT}Import cancelled{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error importing configuration: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        # Проверяем, что нужные файлы существуют
        if not os.path.exists('accounts.txt'):
            print(f"{Fore.RED + Style.BRIGHT}Error: accounts.txt not found!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW + Style.BRIGHT}Please create accounts.txt with your private keys{Style.RESET_ALL}")
            sys.exit(1)
        
        main_menu()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW + Style.BRIGHT}Program interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Fatal error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
