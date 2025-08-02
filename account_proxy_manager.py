#!/usr/bin/env python3

import os
import json
from typing import Dict, Optional, List
from eth_account import Account
from colorama import Fore, Style

class AccountProxyManager:
    def __init__(self):
        self.account_proxy_config = {}
        self.config_file = 'account_proxy_config.json'
        self.load_config()

    def log(self, message):
        """Простая функция логирования"""
        print(f"{Fore.CYAN + Style.BRIGHT}[PROXY]{Style.RESET_ALL} {message}")

    def load_config(self):
        """Загрузка конфигурации прокси для аккаунтов"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.account_proxy_config = json.load(f)
                self.log(f"{Fore.GREEN + Style.BRIGHT}Loaded proxy config for {len(self.account_proxy_config)} accounts{Style.RESET_ALL}")
            except Exception as e:
                self.log(f"{Fore.RED + Style.BRIGHT}Error loading proxy config: {e}{Style.RESET_ALL}")
                self.account_proxy_config = {}
        else:
            self.log(f"{Fore.YELLOW + Style.BRIGHT}No proxy config file found. Creating new one...{Style.RESET_ALL}")
            self.create_default_config()

    def save_config(self):
        """Сохранение конфигурации в файл"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.account_proxy_config, f, indent=2)
            self.log(f"{Fore.GREEN + Style.BRIGHT}Proxy config saved successfully{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Error saving proxy config: {e}{Style.RESET_ALL}")

    def create_default_config(self):
        """Создание конфигурации по умолчанию"""
        try:
            # Загружаем приватные ключи
            if not os.path.exists('accounts.txt'):
                self.log(f"{Fore.RED + Style.BRIGHT}accounts.txt not found!{Style.RESET_ALL}")
                return

            with open('accounts.txt', 'r') as f:
                private_keys = [line.strip() for line in f.read().splitlines() if line.strip()]

            # Загружаем прокси
            proxies = self.load_proxies()

            config = {}
            
            for i, private_key in enumerate(private_keys):
                try:
                    account = Account.from_key(private_key)
                    address = account.address
                    
                    # Пример конфигурации для каждого аккаунта
                    config[address] = {
                        "use_proxy": False,  # По умолчанию прокси отключены
                        "proxy": None,       # Прокси не назначен
                        "proxy_index": i % len(proxies) if proxies else None  # Индекс в списке прокси
                    }
                    
                except Exception as e:
                    self.log(f"{Fore.RED + Style.BRIGHT}Invalid private key #{i+1}, skipping...{Style.RESET_ALL}")
                    continue

            self.account_proxy_config = config
            self.save_config()
            
            self.log(f"{Fore.GREEN + Style.BRIGHT}Created default config for {len(config)} accounts{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}Edit {self.config_file} to configure proxies for each account{Style.RESET_ALL}")
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Error creating default config: {e}{Style.RESET_ALL}")

    def load_proxies(self) -> List[str]:
        """Загрузка прокси из файла"""
        proxy_files = ['proxy.txt', 'proxies.txt']
        
        for filename in proxy_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
                    
                    if proxies:
                        return proxies
                except Exception as e:
                    self.log(f"{Fore.RED + Style.BRIGHT}Error loading {filename}: {e}{Style.RESET_ALL}")
        
        return []

    def get_proxy_for_account(self, address: str) -> Optional[str]:
        """Получение прокси для конкретного аккаунта"""
        if address not in self.account_proxy_config:
            # Создаем конфигурацию по умолчанию для нового аккаунта
            self.account_proxy_config[address] = {
                "use_proxy": False,
                "proxy": None,
                "proxy_index": None
            }
            self.save_config()
            return None

        account_config = self.account_proxy_config[address]
        
        # Проверяем, включены ли прокси для этого аккаунта
        if not account_config.get('use_proxy', False):
            return None

        # Возвращаем прокси, если он указан напрямую
        if account_config.get('proxy'):
            return account_config['proxy']

        # Если указан индекс прокси, берем из списка
        proxy_index = account_config.get('proxy_index')
        if proxy_index is not None:
            proxies = self.load_proxies()
            if proxies and 0 <= proxy_index < len(proxies):
                return proxies[proxy_index]

        return None

    def is_proxy_enabled_for_account(self, address: str) -> bool:
        """Проверка, включены ли прокси для аккаунта"""
        if address not in self.account_proxy_config:
            return False
        return self.account_proxy_config[address].get('use_proxy', False)

    def set_proxy_for_account(self, address: str, proxy: str, enabled: bool = True):
        """Установка прокси для аккаунта"""
        if address not in self.account_proxy_config:
            self.account_proxy_config[address] = {}
        
        self.account_proxy_config[address]['use_proxy'] = enabled
        self.account_proxy_config[address]['proxy'] = proxy
        self.account_proxy_config[address]['proxy_index'] = None  # Сбрасываем индекс при прямом назначении
        
        self.save_config()

    def disable_proxy_for_account(self, address: str):
        """Отключение прокси для аккаунта"""
        if address in self.account_proxy_config:
            self.account_proxy_config[address]['use_proxy'] = False
            self.save_config()

    def interactive_setup(self):
        """Интерактивная настройка прокси для аккаунтов"""
        print(f"{Fore.CYAN + Style.BRIGHT}=== Proxy Configuration Setup ==={Style.RESET_ALL}")
        
        # Загружаем приватные ключи для получения адресов
        try:
            with open('accounts.txt', 'r') as f:
                private_keys = [line.strip() for line in f.read().splitlines() if line.strip()]
        except FileNotFoundError:
            self.log(f"{Fore.RED + Style.BRIGHT}accounts.txt not found!{Style.RESET_ALL}")
            return

        # Загружаем доступные прокси
        available_proxies = self.load_proxies()
        
        if not available_proxies:
            self.log(f"{Fore.YELLOW + Style.BRIGHT}No proxies found in proxy.txt or proxies.txt{Style.RESET_ALL}")
            print(f"{Fore.YELLOW + Style.BRIGHT}You can still manually set proxies for each account{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN + Style.BRIGHT}Available setup options:{Style.RESET_ALL}")
        print("1. Auto-assign proxies to all accounts")
        print("2. Configure each account individually")  
        print("3. Disable proxies for all accounts")
        print("4. View current configuration")
        
        while True:
            choice = input(f"\n{Fore.CYAN + Style.BRIGHT}Enter your choice [1-4]: {Style.RESET_ALL}").strip()
            
            if choice == "1":
                self.auto_assign_proxies(private_keys, available_proxies)
                break
            elif choice == "2":
                self.configure_individually(private_keys, available_proxies)
                break
            elif choice == "3":
                self.disable_all_proxies(private_keys)
                break
            elif choice == "4":
                self.show_current_config(private_keys)
                break
            else:
                print(f"{Fore.RED + Style.BRIGHT}Invalid choice. Please enter 1, 2, 3, or 4{Style.RESET_ALL}")

    def auto_assign_proxies(self, private_keys: List[str], available_proxies: List[str]):
        """Автоматическое назначение прокси для всех аккаунтов"""
        if not available_proxies:
            self.log(f"{Fore.RED + Style.BRIGHT}No proxies available for auto-assignment{Style.RESET_ALL}")
            return

        self.log(f"{Fore.CYAN + Style.BRIGHT}Auto-assigning proxies to {len(private_keys)} accounts...{Style.RESET_ALL}")
        
        for i, private_key in enumerate(private_keys):
            try:
                account = Account.from_key(private_key)
                address = account.address
                proxy_index = i % len(available_proxies)
                
                self.account_proxy_config[address] = {
                    "use_proxy": True,
                    "proxy": None,
                    "proxy_index": proxy_index
                }
                
                self.log(f"{Fore.GREEN + Style.BRIGHT}Account {address[:8]}... assigned proxy #{proxy_index + 1}{Style.RESET_ALL}")
                
            except Exception as e:
                self.log(f"{Fore.RED + Style.BRIGHT}Error processing account #{i+1}: {e}{Style.RESET_ALL}")

        self.save_config()
        self.log(f"{Fore.GREEN + Style.BRIGHT}Auto-assignment completed!{Style.RESET_ALL}")

    def configure_individually(self, private_keys: List[str], available_proxies: List[str]):
        """Индивидуальная настройка каждого аккаунта"""
        for i, private_key in enumerate(private_keys):
            try:
                account = Account.from_key(private_key)
                address = account.address
                
                print(f"\n{Fore.CYAN + Style.BRIGHT}=== Account #{i+1}: {address[:8]}...{address[-6:]} ==={Style.RESET_ALL}")
                
                # Показываем текущую конфигурацию
                current_config = self.account_proxy_config.get(address, {})
                current_use_proxy = current_config.get('use_proxy', False)
                current_proxy = current_config.get('proxy')
                current_proxy_index = current_config.get('proxy_index')
                
                print(f"Current config: use_proxy={current_use_proxy}")
                if current_proxy:
                    print(f"Current proxy: {current_proxy}")
                elif current_proxy_index is not None and available_proxies:
                    print(f"Current proxy: #{current_proxy_index + 1} ({available_proxies[current_proxy_index] if current_proxy_index < len(available_proxies) else 'Invalid index'})")
                
                # Опции для аккаунта
                print(f"\nOptions:")
                print("1. Enable proxy (auto-assign from list)")
                print("2. Enable proxy (enter manually)")
                print("3. Disable proxy")
                print("4. Skip this account")
                
                if available_proxies:
                    print("5. Choose from available proxies")
                
                while True:
                    choice = input(f"{Fore.YELLOW + Style.BRIGHT}Choice for this account [1-5]: {Style.RESET_ALL}").strip()
                    
                    if choice == "1":
                        if available_proxies:
                            proxy_index = i % len(available_proxies)
                            self.account_proxy_config[address] = {
                                "use_proxy": True,
                                "proxy": None,
                                "proxy_index": proxy_index
                            }
                            print(f"{Fore.GREEN + Style.BRIGHT}Assigned proxy #{proxy_index + 1}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED + Style.BRIGHT}No proxies available{Style.RESET_ALL}")
                            continue
                        break
                        
                    elif choice == "2":
                        proxy = input(f"{Fore.CYAN + Style.BRIGHT}Enter proxy (format: protocol://user:pass@ip:port): {Style.RESET_ALL}").strip()
                        if proxy:
                            self.account_proxy_config[address] = {
                                "use_proxy": True,
                                "proxy": proxy,
                                "proxy_index": None
                            }
                            print(f"{Fore.GREEN + Style.BRIGHT}Proxy set manually{Style.RESET_ALL}")
                        break
                        
                    elif choice == "3":
                        self.account_proxy_config[address] = {
                            "use_proxy": False,
                            "proxy": None,
                            "proxy_index": None
                        }
                        print(f"{Fore.YELLOW + Style.BRIGHT}Proxy disabled{Style.RESET_ALL}")
                        break
                        
                    elif choice == "4":
                        print(f"{Fore.CYAN + Style.BRIGHT}Skipped{Style.RESET_ALL}")
                        break
                        
                    elif choice == "5" and available_proxies:
                        print(f"\nAvailable proxies:")
                        for idx, proxy in enumerate(available_proxies):
                            print(f"{idx + 1}. {proxy}")
                        
                        try:
                            proxy_choice = int(input(f"{Fore.CYAN + Style.BRIGHT}Choose proxy number [1-{len(available_proxies)}]: {Style.RESET_ALL}")) - 1
                            if 0 <= proxy_choice < len(available_proxies):
                                self.account_proxy_config[address] = {
                                    "use_proxy": True,
                                    "proxy": None,
                                    "proxy_index": proxy_choice
                                }
                                print(f"{Fore.GREEN + Style.BRIGHT}Selected proxy #{proxy_choice + 1}{Style.RESET_ALL}")
                                break
                            else:
                                print(f"{Fore.RED + Style.BRIGHT}Invalid proxy number{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED + Style.BRIGHT}Please enter a valid number{Style.RESET_ALL}")
                        continue
                        
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Invalid choice{Style.RESET_ALL}")
                        continue
                        
            except Exception as e:
                self.log(f"{Fore.RED + Style.BRIGHT}Error configuring account #{i+1}: {e}{Style.RESET_ALL}")

        self.save_config()
        self.log(f"{Fore.GREEN + Style.BRIGHT}Individual configuration completed!{Style.RESET_ALL}")

    def disable_all_proxies(self, private_keys: List[str]):
        """Отключение прокси для всех аккаунтов"""
        self.log(f"{Fore.YELLOW + Style.BRIGHT}Disabling proxies for all accounts...{Style.RESET_ALL}")
        
        for private_key in private_keys:
            try:
                account = Account.from_key(private_key)
                address = account.address
                
                self.account_proxy_config[address] = {
                    "use_proxy": False,
                    "proxy": None,
                    "proxy_index": None
                }
                
            except Exception as e:
                self.log(f"{Fore.RED + Style.BRIGHT}Error processing account: {e}{Style.RESET_ALL}")

        self.save_config()
        self.log(f"{Fore.GREEN + Style.BRIGHT}All proxies disabled!{Style.RESET_ALL}")

    def show_current_config(self, private_keys: List[str]):
        """Показ текущей конфигурации"""
        available_proxies = self.load_proxies()
        
        print(f"\n{Fore.CYAN + Style.BRIGHT}=== Current Proxy Configuration ==={Style.RESET_ALL}")
        
        for i, private_key in enumerate(private_keys):
            try:
                account = Account.from_key(private_key)
                address = account.address
                
                config = self.account_proxy_config.get(address, {})
                use_proxy = config.get('use_proxy', False)
                proxy = config.get('proxy')
                proxy_index = config.get('proxy_index')
                
                print(f"\n{i+1}. {address[:8]}...{address[-6:]}:")
                print(f"   Use Proxy: {use_proxy}")
                
                if use_proxy:
                    if proxy:
                        print(f"   Proxy: {proxy}")
                    elif proxy_index is not None and available_proxies:
                        if proxy_index < len(available_proxies):
                            print(f"   Proxy: #{proxy_index + 1} ({available_proxies[proxy_index]})")
                        else:
                            print(f"   Proxy: #{proxy_index + 1} (INVALID INDEX)")
                    else:
                        print(f"   Proxy: Not configured")
                        
            except Exception as e:
                print(f"{i+1}. Error: {e}")

        print(f"\n{Fore.GREEN + Style.BRIGHT}Configuration review completed{Style.RESET_ALL}")