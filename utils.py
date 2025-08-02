#!/usr/bin/env python3

import os
import time
from datetime import datetime
from colorama import Fore, Style
from eth_account import Account
try:
    from fake_useragent import FakeUserAgent
    ua = FakeUserAgent()
except ImportError:
    ua = None
import pytz

# Настройка timezone
wib = pytz.timezone('Europe/Moscow')

class Logger:
    @staticmethod
    def log(message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%H:%M:%S')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    @staticmethod
    def clear_terminal():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def welcome():
        banner = f"""
{Fore.YELLOW + Style.BRIGHT}PHAROS FUCKER BOT v 3.0 Faucet•Checkin•Swap•AquaFlux•Liquidity•Tips•Brokex•OpenFI {Style.RESET_ALL}
{Fore.CYAN + Style.BRIGHT}═══════════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}
{Fore.BLUE + Style.BRIGHT}
........................................=%*:.......................................
.....................................-#@@#%@@=:....................................
..................................:#@@####%%#@@%-..................................
.................................@@@@@@@@@@@@@@@@@*................................
.................................@@%%%%%%%@@@@@@@@%................................
...................................@#++++*#%%%%%@:.................................
..................................:@*++@@%@@%%%%@:.................................
................................:-+@#%%@@@@@@@@@@=:................................
...........................-#@@@@%%############%@@@@@@#-...........................
.......................-*@@@#######################%@%%@@@*-.......................
....................:#@@#############################%%@%%%@@%:....................
..................-%@%#################################%%@%%%%@@-..................
.................%@######################################%%@****@%.................
...............+@%###################%@@%##################*%#***#@+...............
..............*@###########################################**#%****@#..............
............:%@#####@@@####################################***#@**#%@%:............
............#@#################################################%@#%%%@#............
...........+@##################################################%%%#%#%@=...........
..........-@%###########################@@%+*@@%################%@%%%%@@...........
..........%@#########@%*-:-*@#########@@:....+-+@################@@#%%%@+..........
.........-@%########%:...:%@@@#######%@....:@@@#*################%@#%%%@@..........
.........+@########@+....=@@@@#######@%.....*#*.*%################@%%%%@@:.........
.........*@########@+........#########@=.......=@#################@%%%%%@=.........
.........#@#########@=...:#%@%#########%@*+**%%#@@@@%#############@%%%%%@+.........
.........#@########***%%@@###@@####*####@@%###*@%###@%############@%%%%%@+.........
.........*@#####*#*****#@#####@%@@%%%#+===+%##@%#####@############@%%%%%@=.........
.........=@######*#####@%#####@@#==+=+=+=+=#@@@######%@%#########%@%%%%%@-.........
.........:@%#########@@%#########%@###%+=*@%###########%@@######%@%%%%%@@:.........
..........:@%####@@@%##############@#++*@@################%@@@@%@@@@%#%@+..........
..........+@%%%####################@@###@@########################%@@%@%...........
.........:@#######################@@@##%%@@########################%@%@:...........
.........:%%#####################@@%%%%%%#%@@#####################%@@@-............
..........-@%##################@@%%%%%%%%#%%%@@%%##############%%%@@#..............
...........:*@%###########%@@@@%%%%%%%%%%%%%%%%@@@@@@%%####%%%%@@@@=...............
...............-#@@@@@@@%%%%#%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@%%%@+.................
..............:*@@%%%%%@@%%%%%%%%%%@%@%@#%%##%%@@%%%%%%%%%%%%%%%%@#:...............
........:+@@@@%+=+*%#%%%%%%@@@@%%%@@@@@@@@@@%%%%%%%%%%%%%%%%#*++++%@@*-:::.........
.......=@%##*+++++++#%%%%%%%%%%%%%%%@@%%#%%%%%%%%%%@%#######+++++++*##%%%@%:.......
.......#@###*++++++=*###%%%%%%%%@@%%%%@%%%%%%%%%%+=%@#######+++++++*######@%.......
.......=@%###*+++++*########%@@#+@@%##%%########*+++%@%#######++++########@@:......
........#@%###############@@@+++++@@############*+++++#@@@###############%@+.......
.........=@@@#########%@@@*+++==++*@@%############*++++*#%@%#########%@@@*:........
............-*%@@@@@%*-:.=%@@%#***#@@@@@%###############%@**@@@@@@@@*=.............
.............................:-----:...:=#@@@@%#####%@@@+:.........................
.............................................:+#%%#*=:.............................
{Style.RESET_ALL}
{Fore.CYAN + Style.BRIGHT}═══════════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}
"""
        print(banner)

    @staticmethod
    def format_time_remaining(seconds):
        """Форматирование времени до следующего клейма"""
        if seconds <= 0:
            return "Available now"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

class FileManager:
    @staticmethod
    def load_private_keys():
        """Загрузка приватных ключей из accounts.txt"""
        try:
            with open('accounts.txt', 'r') as f:
                keys = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            valid_keys = []
            for key in keys:
                try:
                    # Проверяем, что ключ действительный
                    account = Account.from_key(key)
                    valid_keys.append(key)
                except Exception:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}Invalid private key found, skipping...{Style.RESET_ALL}")
            
            return valid_keys
            
        except FileNotFoundError:
            Logger.log(f"{Fore.RED + Style.BRIGHT}accounts.txt not found!{Style.RESET_ALL}")
            return []

    @staticmethod
    def load_proxies():
        """Загрузка прокси из файла"""
        proxy_files = ['proxy.txt', 'proxies.txt']
        
        for filename in proxy_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
                    
                    if proxies:
                        Logger.log(f"{Fore.GREEN + Style.BRIGHT}Loaded {len(proxies)} proxies from {filename}{Style.RESET_ALL}")
                        return proxies
                except Exception as e:
                    Logger.log(f"{Fore.RED + Style.BRIGHT}Error loading {filename}: {e}{Style.RESET_ALL}")
        
        Logger.log(f"{Fore.YELLOW + Style.BRIGHT}No proxy files found. Running without proxies.{Style.RESET_ALL}")
        return []

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def load_proxies(self):
        self.proxies = FileManager.load_proxies()

    def get_proxy_for_account(self, address: str):
        """Получить прокси для аккаунта"""
        if not self.proxies:
            return None
            
        if address not in self.account_proxies:
            proxy = self.proxies[self.proxy_index % len(self.proxies)]
            self.account_proxies[address] = proxy
            self.proxy_index += 1
            
        return self.account_proxies[address]

def get_headers():
    """Получение заголовков для HTTP запросов"""
    user_agent = ua.random if ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://testnet.pharosnetwork.xyz",
        "Referer": "https://testnet.pharosnetwork.xyz/",
        "User-Agent": user_agent
    }