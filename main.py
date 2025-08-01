#!/usr/bin/env python3

import asyncio
import random
import warnings
from web3 import Web3
from eth_account import Account
from colorama import Fore, Style

# Отключаем предупреждения
warnings.filterwarnings("ignore", category=UserWarning)

# Импорты модулей
from config import Config
from utils import Logger, FileManager, ProxyManager
from web3_manager import Web3Manager
from faucet import FaucetManager
from aquaflux import AquaFluxManager
from swap import SwapManager
from liquidity import LiquidityManager
from tips import TipManager
from web_checkin import WebCheckinManager

class PharosBotAdvanced:
    def __init__(self):
        self.config = Config()
        self.proxy_manager = ProxyManager()
        self.web3_manager = Web3Manager()
        self.faucet_manager = FaucetManager(self.web3_manager)
        self.aquaflux_manager = AquaFluxManager(self.web3_manager)
        self.swap_manager = SwapManager(self.web3_manager)
        self.liquidity_manager = LiquidityManager(self.web3_manager)
        self.tip_manager = TipManager(self.web3_manager)
        self.web_checkin_manager = WebCheckinManager(self.web3_manager)

    def get_user_config(self):
        """Получение конфигурации от пользователя - УПРОЩЕННАЯ ВЕРСИЯ"""
        print(f"{Fore.GREEN + Style.BRIGHT}🔧 Bot Configuration{Style.RESET_ALL}")
        print(f"{Fore.YELLOW + Style.BRIGHT}Choose operations to perform:{Style.RESET_ALL}")
        
        config = {}
        
        # Faucet операции
        while True:
            faucet = input(f"{Fore.CYAN + Style.BRIGHT}Enable faucet operations? [y/n]: {Style.RESET_ALL}").strip().lower()
            if faucet in ['y', 'n']:
                config['faucet_enabled'] = faucet == 'y'
                break
            print(f"{Fore.RED + Style.BRIGHT}Please enter 'y' or 'n'{Style.RESET_ALL}")
        
        # Daily checkin
        while True:
            checkin = input(f"{Fore.CYAN + Style.BRIGHT}Enable daily checkin? [y/n]: {Style.RESET_ALL}").strip().lower()
            if checkin in ['y', 'n']:
                config['checkin_enabled'] = checkin == 'y'
                break
            print(f"{Fore.RED + Style.BRIGHT}Please enter 'y' or 'n'{Style.RESET_ALL}")
        
        # AquaFlux операции
        while True:
            aquaflux = input(f"{Fore.CYAN + Style.BRIGHT}Enable AquaFlux operations (claim, craft, mint NFT)? [y/n]: {Style.RESET_ALL}").strip().lower()
            if aquaflux in ['y', 'n']:
                config['aquaflux_enabled'] = aquaflux == 'y'
                break
            print(f"{Fore.RED + Style.BRIGHT}Please enter 'y' or 'n'{Style.RESET_ALL}")
        
        # Swap операции - УПРОЩЕНО
        while True:
            swaps = input(f"{Fore.CYAN + Style.BRIGHT}Enable swap operations? [y/n]: {Style.RESET_ALL}").strip().lower()
            if swaps in ['y', 'n']:
                config['swaps_enabled'] = swaps == 'y'
                if swaps == 'y':
                    while True:
                        try:
                            swap_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many swaps to perform per wallet [1-20]: {Style.RESET_ALL}"))
                            if 1 <= swap_count <= 20:
                                config['swap_count'] = swap_count
                                print(f"{Fore.GREEN + Style.BRIGHT}Will perform {swap_count} swaps with 1-10 sec delays{Style.RESET_ALL}")
                                break
                            print(f"{Fore.RED + Style.BRIGHT}Please enter a number between 1 and 20{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED + Style.BRIGHT}Please enter a valid number{Style.RESET_ALL}")
                break
            print(f"{Fore.RED + Style.BRIGHT}Please enter 'y' or 'n'{Style.RESET_ALL}")
        
        # Liquidity операции - УПРОЩЕНО
        while True:
            liquidity = input(f"{Fore.CYAN + Style.BRIGHT}Enable liquidity operations? [y/n]: {Style.RESET_ALL}").strip().lower()
            if liquidity in ['y', 'n']:
                config['liquidity_enabled'] = liquidity == 'y'
                if liquidity == 'y':
                    while True:
                        try:
                            liquidity_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many liquidity operations per wallet [1-10]: {Style.RESET_ALL}"))
                            if 1 <= liquidity_count <= 10:
                                config['liquidity_count'] = liquidity_count
                                print(f"{Fore.GREEN + Style.BRIGHT}Will add liquidity {liquidity_count} times with 1-10 sec delays{Style.RESET_ALL}")
                                break
                            print(f"{Fore.RED + Style.BRIGHT}Please enter a number between 1 and 10{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED + Style.BRIGHT}Please enter a valid number{Style.RESET_ALL}")
                break
            print(f"{Fore.RED + Style.BRIGHT}Please enter 'y' or 'n'{Style.RESET_ALL}")
        
        # Tip операции - УПРОЩЕНО
        while True:
            tips = input(f"{Fore.CYAN + Style.BRIGHT}Enable tip operations? [y/n]: {Style.RESET_ALL}").strip().lower()
            if tips in ['y', 'n']:
                config['tips_enabled'] = tips == 'y'
                if tips == 'y':
                    username = input(f"{Fore.YELLOW + Style.BRIGHT}Enter X username to tip (without @): {Style.RESET_ALL}").strip()
                    if username:
                        config['tip_username'] = username
                        
                        while True:
                            try:
                                tip_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many tips per wallet [1-10]: {Style.RESET_ALL}"))
                                if 1 <= tip_count <= 10:
                                    config['tip_count'] = tip_count
                                    print(f"{Fore.GREEN + Style.BRIGHT}Will send {tip_count} tips with 10-30 sec delays{Style.RESET_ALL}")
                                    break
                                print(f"{Fore.RED + Style.BRIGHT}Please enter a number between 1 and 10{Style.RESET_ALL}")
                            except ValueError:
                                print(f"{Fore.RED + Style.BRIGHT}Please enter a valid number{Style.RESET_ALL}")
                    else:
                        config['tips_enabled'] = False
                        print(f"{Fore.RED + Style.BRIGHT}No username provided, disabling tips{Style.RESET_ALL}")
                break
            print(f"{Fore.RED + Style.BRIGHT}Please enter 'y' or 'n'{Style.RESET_ALL}")
        
        # Proxy настройки
        while True:
            use_proxy = input(f"{Fore.CYAN + Style.BRIGHT}Use proxies? [y/n]: {Style.RESET_ALL}").strip().lower()
            if use_proxy in ['y', 'n']:
                config['use_proxy'] = use_proxy == 'y'
                break
            print(f"{Fore.RED + Style.BRIGHT}Please enter 'y' or 'n'{Style.RESET_ALL}")
        
        # Многопоточность - УПРОЩЕНО
        total_wallets = len(FileManager.load_private_keys())
        while True:
            try:
                parallel_wallets = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many wallets to process simultaneously [1-{total_wallets}]: {Style.RESET_ALL}"))
                if 1 <= parallel_wallets <= total_wallets:
                    config['parallel_wallets'] = parallel_wallets
                    if parallel_wallets == 1:
                        print(f"{Fore.GREEN + Style.BRIGHT}Will process wallets one by one{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN + Style.BRIGHT}Will process {parallel_wallets} wallets simultaneously{Style.RESET_ALL}")
                    break
                print(f"{Fore.RED + Style.BRIGHT}Please enter a number between 1 and {total_wallets}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Please enter a valid number{Style.RESET_ALL}")
        
        return config

    async def process_wallet(self, private_key: str, config: dict):
        """Обработка одного кошелька"""
        results = {}
        
        # Получаем адрес из приватного ключа
        account = Account.from_key(private_key)
        address = account.address
        
        # Получаем прокси для кошелька
        proxy = self.proxy_manager.get_proxy_for_account(address) if config.get('use_proxy', False) else None
        
        # Добавляем случайную задержку в начале для распределения нагрузки
        if config.get('parallel_wallets', 1) > 1:
            await asyncio.sleep(random.uniform(0.5, 3))
        
        try:
            web3 = await self.web3_manager.get_web3_connection(proxy)
            balance = await self.web3_manager.get_token_balance(web3, address, "PHRS")
            Logger.log(f"PHRS Balance: {balance}")
            
            # 1. Faucet операции
            faucet_result = None
            if config.get('faucet_enabled', False) and balance < 0.1:
                Logger.log(f"{Fore.BLUE + Style.BRIGHT}Starting faucet operations...{Style.RESET_ALL}")
                faucet_result = await self.faucet_manager.claim_faucet(web3, private_key, proxy)
                results['faucet'] = faucet_result
            else:
                Logger.log(f"{Fore.CYAN + Style.BRIGHT}Faucet disabled or sufficient balance{Style.RESET_ALL}")
                results['faucet'] = "disabled_or_sufficient"
            
            # Обработка результатов фаусета
            if faucet_result == "sufficient_balance":
                Logger.log(f"{Fore.GREEN}Skipping faucet - sufficient balance{Style.RESET_ALL}")
            elif faucet_result == "manual_required":
                Logger.log(f"{Fore.YELLOW}Manual PHRS funding required{Style.RESET_ALL}")
            
            # 2. Daily checkin - НОВАЯ ВЕРСИЯ
            checkin_result = None
            if config.get('checkin_enabled', False):
                Logger.log(f"{Fore.BLUE + Style.BRIGHT}Starting daily checkin...{Style.RESET_ALL}")
                
                # Используем новый веб чекин менеджер
                web_checkin_result = await self.web_checkin_manager.perform_web_checkin(private_key, proxy)
                
                if web_checkin_result:
                    checkin_result = web_checkin_result.get('checkin')
                    faucet_result = web_checkin_result.get('faucet')
                    
                    results['checkin'] = checkin_result
                    results['web_faucet'] = faucet_result
                    
                    # Обработка результатов
                    if checkin_result is True:
                        Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ Daily checkin completed successfully!{Style.RESET_ALL}")
                    elif checkin_result == "already_checked":
                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}⏳ Already checked in today{Style.RESET_ALL}")
                    else:
                        Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Checkin failed{Style.RESET_ALL}")
                    
                    if faucet_result is True:
                        Logger.log(f"{Fore.GREEN + Style.BRIGHT}✅ Faucet claimed successfully!{Style.RESET_ALL}")
                    elif faucet_result == "already_claimed":
                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}⏳ Faucet already claimed{Style.RESET_ALL}")
                    elif faucet_result == "not_eligible":
                        Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Not eligible for faucet{Style.RESET_ALL}")
                    
                    # Уменьшаем задержку для многопоточности
                    delay = 2 if config.get('parallel_wallets', 1) > 1 else 3
                    await asyncio.sleep(delay)
                else:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}❌ Web checkin completely failed{Style.RESET_ALL}")
                    results['checkin'] = "failed"
            else:
                Logger.log(f"{Fore.CYAN + Style.BRIGHT}Checkin disabled in configuration{Style.RESET_ALL}")
                results['checkin'] = "disabled"

            # 3. AquaFlux операции
            if config.get('aquaflux_enabled', False):
                Logger.log(f"{Fore.BLUE + Style.BRIGHT}Starting AquaFlux operations...{Style.RESET_ALL}")
                
                try:
                    access_token = await self.aquaflux_manager.aquaflux_login(address, private_key, proxy)
                    if access_token:
                        claim_result = await self.aquaflux_manager.claim_aquaflux_tokens(web3, private_key)
                        results['claim'] = claim_result
                        
                        if claim_result and claim_result != "already_claimed":
                            await asyncio.sleep(5)
                            
                            craft_result = await self.aquaflux_manager.craft_cs_tokens(web3, private_key)
                            results['craft'] = craft_result
                            
                            if craft_result:
                                await asyncio.sleep(5)
                                
                                signature_data = await self.aquaflux_manager.get_aquaflux_signature(address, access_token, 0, proxy)
                                if signature_data:
                                    mint_result = await self.aquaflux_manager.mint_aquaflux_nft(web3, private_key, signature_data)
                                    results['mint'] = mint_result
                    else:
                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}AquaFlux login failed - server may be down, skipping...{Style.RESET_ALL}")
                        results['aquaflux'] = "server_error"
                except Exception as e:
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}AquaFlux operations failed: {str(e)[:50]}... - continuing with other operations{Style.RESET_ALL}")
                    results['aquaflux'] = "error"
            
            # 4. Swap операции - УПРОЩЕННАЯ ЛОГИКА
            if config.get('swaps_enabled', False):
                Logger.log(f"{Fore.BLUE + Style.BRIGHT}Starting swap operations...{Style.RESET_ALL}")
                
                swap_pairs = [
                    (self.config.WPHRS_CONTRACT, self.config.USDC_CONTRACT, self.config.PHRS_TO_USDC_AMOUNT, "WPHRS", "USDC"),
                    (self.config.USDC_CONTRACT, self.config.WPHRS_CONTRACT, self.config.USDC_TO_PHRS_AMOUNT, "USDC", "WPHRS"),
                    (self.config.WPHRS_CONTRACT, self.config.USDT_CONTRACT, self.config.PHRS_TO_USDT_AMOUNT, "WPHRS", "USDT"),
                    (self.config.USDT_CONTRACT, self.config.WPHRS_CONTRACT, self.config.USDT_TO_PHRS_AMOUNT, "USDT", "WPHRS")
                ]
                
                successful_swaps = 0
                total_swaps = config.get('swap_count', 4)
                
                for i in range(total_swaps):
                    # Выбираем случайную пару для свапа
                    from_token, to_token, amount, from_name, to_name = random.choice(swap_pairs)
                    
                    Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Swap {i+1}/{total_swaps}: {from_name} -> {to_name}{Style.RESET_ALL}")
                    
                    from_balance = await self.web3_manager.get_token_balance(web3, address, from_token)
                    required_amount = Web3.from_wei(amount, 'ether') if from_name == "WPHRS" else amount / (10**6 if "USDC" in from_name or "USDT" in from_name else 10**18)
                    
                    if from_balance < required_amount:
                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient {from_name} balance, skipping swap{Style.RESET_ALL}")
                        continue
                    
                    if from_token.lower() != "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee":
                        await self.web3_manager.approve_token(web3, private_key, from_token, self.config.DODO_ROUTER, amount)
                    
                    route_data = await self.swap_manager.fetch_dodo_route(from_token, to_token, address, amount, proxy)
                    if route_data:
                        swap_result = await self.swap_manager.execute_swap(web3, private_key, route_data)
                        if swap_result:
                            successful_swaps += 1
                            results[f'swap_{i+1}'] = swap_result
                    
                    # Случайная задержка от 1 до 10 секунд
                    if i < total_swaps - 1:
                        delay = random.randint(1, 10)
                        Logger.log(f"{Fore.CYAN + Style.BRIGHT}Waiting {delay} seconds...{Style.RESET_ALL}")
                        await asyncio.sleep(delay)
                
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Completed {successful_swaps}/{total_swaps} swaps{Style.RESET_ALL}")
            
            # 5. Liquidity операции - УПРОЩЕННАЯ ЛОГИКА
            if config.get('liquidity_enabled', False):
                Logger.log(f"{Fore.BLUE + Style.BRIGHT}Starting liquidity operations...{Style.RESET_ALL}")
                
                liquidity_count = config.get('liquidity_count', 1)
                successful_lp = 0
                
                for lp_round in range(liquidity_count):
                    Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Liquidity operation {lp_round + 1}/{liquidity_count}{Style.RESET_ALL}")
                    
                    usdc_balance = await self.web3_manager.get_token_balance(web3, address, self.config.USDC_CONTRACT)
                    usdt_balance = await self.web3_manager.get_token_balance(web3, address, self.config.USDT_CONTRACT)
                    
                    required_usdc = self.config.USDC_LIQUIDITY_AMOUNT / 1000000
                    required_usdt = self.config.USDT_LIQUIDITY_AMOUNT / 1000000
                    
                    if usdc_balance >= required_usdc and usdt_balance >= required_usdt:
                        lp_result = await self.liquidity_manager.add_liquidity(web3, private_key, self.config.USDC_CONTRACT, self.config.USDT_CONTRACT, 
                                                       self.config.USDC_LIQUIDITY_AMOUNT, self.config.USDT_LIQUIDITY_AMOUNT)
                        if lp_result:
                            successful_lp += 1
                            results[f'liquidity_{lp_round+1}'] = lp_result
                        
                        # Случайная задержка от 1 до 10 секунд
                        if lp_round < liquidity_count - 1:
                            delay = random.randint(1, 10)
                            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Waiting {delay} seconds...{Style.RESET_ALL}")
                            await asyncio.sleep(delay)
                    else:
                        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient tokens for liquidity. USDC: {usdc_balance:.6f}/{required_usdc:.6f}, USDT: {usdt_balance:.6f}/{required_usdt:.6f}{Style.RESET_ALL}")
                        break
                
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Completed {successful_lp}/{liquidity_count} liquidity operations{Style.RESET_ALL}")

            # 6. Tip операции - УПРОЩЕННАЯ ЛОГИКА
            if config.get('tips_enabled', False) and config.get('tip_username'):
                Logger.log(f"{Fore.BLUE + Style.BRIGHT}Starting tip operations...{Style.RESET_ALL}")
                
                # Проверяем статус контракта типов
                contract_ok = await self.tip_manager.check_tip_contract_status(web3)
                if not contract_ok:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}Tip contract not available, skipping tips{Style.RESET_ALL}")
                    results['tips'] = "contract_unavailable"
                else:
                    current_balance = await self.web3_manager.get_token_balance(web3, address, "PHRS")
                    tip_count = config.get('tip_count', 1)
                    successful_tips = 0
                    
                    for tip_round in range(tip_count):
                        Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Tip {tip_round + 1}/{tip_count}{Style.RESET_ALL}")
                        
                        # Проверяем баланс перед каждым типом
                        if current_balance < 0.001:  # Минимальный баланс для типов
                            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Insufficient balance for tips: {current_balance:.6f} PHRS{Style.RESET_ALL}")
                            break
                        
                        tip_amount = self.tip_manager.generate_random_tip_amount()
                        Logger.log(f"{Fore.CYAN + Style.BRIGHT}Sending tip of {Web3.from_wei(tip_amount, 'ether'):.8f} PHRS to @{config['tip_username']}{Style.RESET_ALL}")
                        
                        tip_result = await self.tip_manager.send_tip(web3, private_key, config['tip_username'], tip_amount)
                        if tip_result:
                            successful_tips += 1
                            results[f'tip_{tip_round+1}'] = tip_result
                            current_balance -= Web3.from_wei(tip_amount, 'ether')
                        
                        # Случайная задержка от 10 до 30 секунд для типов
                        if tip_round < tip_count - 1:
                            delay = random.randint(10, 30)
                            Logger.log(f"{Fore.CYAN + Style.BRIGHT}Waiting {delay} seconds before next tip...{Style.RESET_ALL}")
                            await asyncio.sleep(delay)
                    
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}Completed {successful_tips}/{tip_count} tips{Style.RESET_ALL}")
            
            # Логируем результаты
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Wallet processing completed!{Style.RESET_ALL}")
            for operation, result in results.items():
                status = "✅" if result and result not in ["cooldown", "already_claimed", "already_checked"] else "⏳" if result in ["cooldown", "already_claimed", "already_checked"] else "❌"
                Logger.log(f"  {status} {operation}: {result or 'Failed'}")
            
            return results
            
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Wallet processing error: {e}{Style.RESET_ALL}")
            return None

    async def process_wallet_batch(self, private_keys_batch, config):
        """Обработка пакета кошельков параллельно - УПРОЩЕННАЯ ЛОГИКА"""
        tasks = []
        
        for private_key in private_keys_batch:
            task = asyncio.create_task(self.process_wallet(private_key, config))
            tasks.append(task)
            
            # Небольшая задержка между запуском задач чтобы не перегрузить сервер
            await asyncio.sleep(random.uniform(0.5, 2))
        
        # Ждем завершения всех задач в пакете
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = 0
        failed = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                Logger.log(f"{Fore.RED + Style.BRIGHT}Wallet {i+1} error: {result}{Style.RESET_ALL}")
                failed += 1
            elif result:
                successful += 1
            else:
                failed += 1
                
        return successful, failed

    async def run_bot(self):
        """Основная функция запуска бота"""
        try:
            Logger.clear_terminal()
            Logger.welcome()
            
            private_keys = FileManager.load_private_keys()
            if not private_keys:
                Logger.log(f"{Fore.RED + Style.BRIGHT}No valid private keys found in accounts.txt!{Style.RESET_ALL}")
                return
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Loaded {len(private_keys)} private keys{Style.RESET_ALL}")
            
            config = self.get_user_config()

            if config.get('use_proxy', False):
                self.proxy_manager.load_proxies()
            else:
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Running without proxies as per configuration.{Style.RESET_ALL}")
            
            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Starting bot with configuration:{Style.RESET_ALL}")
            for key, value in config.items():
                if key != 'tip_username':
                    Logger.log(f"  {key}: {value}")
                elif config.get('tips_enabled'):
                     Logger.log(f"  {key}: {value}")
            
            # Главный цикл с упрощенной многопоточностью
            while True:
                Logger.log(f"{Fore.CYAN + Style.BRIGHT}{'='*50} Starting new cycle {'='*50}{Style.RESET_ALL}")
                
                total_successful = 0
                total_failed = 0
                
                # Упрощенная логика многопоточности
                parallel_wallets = config.get('parallel_wallets', 1)
                
                if parallel_wallets == 1:
                    # Обрабатываем кошельки по одному
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}Processing {len(private_keys)} wallets one by one{Style.RESET_ALL}")
                    
                    for i, private_key in enumerate(private_keys, 1):
                        Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Processing wallet {i}/{len(private_keys)}{Style.RESET_ALL}")
                        
                        result = await self.process_wallet(private_key, config)
                        
                        if result:
                            total_successful += 1
                            Logger.log(f"{Fore.GREEN + Style.BRIGHT}Wallet {i} completed successfully{Style.RESET_ALL}")
                        else:
                            total_failed += 1
                            Logger.log(f"{Fore.RED + Style.BRIGHT}Wallet {i} failed{Style.RESET_ALL}")
                        
                        # Небольшая задержка между кошельками
                        if i < len(private_keys):
                            delay = random.randint(2, 8)
                            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Waiting {delay} seconds before next wallet...{Style.RESET_ALL}")
                            await asyncio.sleep(delay)
                else:
                    # Обрабатываем кошельки параллельно
                    Logger.log(f"{Fore.GREEN + Style.BRIGHT}Processing {len(private_keys)} wallets with {parallel_wallets} parallel workers{Style.RESET_ALL}")
                    
                    # Разбиваем кошельки на пакеты
                    batch_size = parallel_wallets
                    batches = []
                    for i in range(0, len(private_keys), batch_size):
                        batch = private_keys[i:i + batch_size]
                        batches.append(batch)
                    
                    # Обрабатываем пакеты
                    for batch_num, batch in enumerate(batches, 1):
                        Logger.log(f"{Fore.MAGENTA + Style.BRIGHT}Processing batch {batch_num}/{len(batches)} ({len(batch)} wallets){Style.RESET_ALL}")
                        
                        successful, failed = await self.process_wallet_batch(batch, config)
                        total_successful += successful
                        total_failed += failed
                        
                        Logger.log(f"{Fore.GREEN + Style.BRIGHT}Batch {batch_num} completed: {successful} successful, {failed} failed{Style.RESET_ALL}")
                        
                        # Задержка между пакетами (кроме последнего)
                        if batch_num < len(batches):
                            delay = random.randint(5, 15)
                            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Waiting {delay} seconds before next batch...{Style.RESET_ALL}")
                            await asyncio.sleep(delay)
                
                Logger.log(f"{Fore.CYAN + Style.BRIGHT}All batches completed!{Style.RESET_ALL}")
                Logger.log(f"{Fore.GREEN + Style.BRIGHT}Total successful wallets: {total_successful}{Style.RESET_ALL}")
                Logger.log(f"{Fore.RED + Style.BRIGHT}Total failed wallets: {total_failed}{Style.RESET_ALL}")
                Logger.log(f"{Fore.CYAN + Style.BRIGHT}Success rate: {(total_successful/(total_successful+total_failed)*100):.1f}%{Style.RESET_ALL}")
                
                wait_time = 24 * 60 * 60
                Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Waiting 24 hours until next cycle...{Style.RESET_ALL}")
                
                for remaining in range(wait_time, 0, -60):
                    hours = remaining // 3600
                    minutes = (remaining % 3600) // 60
                    print(f"\r{Fore.CYAN + Style.BRIGHT}Next cycle in: {hours:02d}:{minutes:02d}:00{Style.RESET_ALL}", end='', flush=True)
                    await asyncio.sleep(60)
                
                print()
                
        except KeyboardInterrupt:
            Logger.log(f"{Fore.YELLOW + Style.BRIGHT}Bot stopped by user{Style.RESET_ALL}")
        except Exception as e:
            Logger.log(f"{Fore.RED + Style.BRIGHT}Critical error: {e}{Style.RESET_ALL}")
            raise

def main():
    """Точка входа в программу"""
    try:
        import os
        if not os.path.exists('accounts.txt'):
            print(f"{Fore.RED + Style.BRIGHT}Error: accounts.txt not found!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW + Style.BRIGHT}Please create accounts.txt with your private keys (one per line){Style.RESET_ALL}")
            return
        
        bot = PharosBotAdvanced()
        asyncio.run(bot.run_bot())
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW + Style.BRIGHT}Program interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Fatal error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()