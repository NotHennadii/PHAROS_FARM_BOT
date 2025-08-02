#!/usr/bin/env python3

from web3 import Web3

class Config:
    # API и RPC настройки
    BASE_API = "https://api.pharosnetwork.xyz"
    RPC_URL = "https://testnet.dplabs-internal.com"
    CHAIN_ID = 688688
    
    # Адреса контрактов
    WPHRS_CONTRACT = Web3.to_checksum_address("0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
    USDC_CONTRACT = Web3.to_checksum_address("0x72df0bcd7276f2dfbac900d1ce63c272c4bccced")
    USDT_CONTRACT = Web3.to_checksum_address("0xD4071393f8716661958F766DF660033b3d35fD29")
    SWAP_ROUTER = Web3.to_checksum_address("0x1A4DE519154Ae51200b0Ad7c90F7faC75547888a")
    POSITION_MANAGER = Web3.to_checksum_address("0xF8a1D4FF0f9b9Af7CE58E1fc1833688F3BFd6115")
    
    # Faucet контракт
    FAUCET_CONTRACT = Web3.to_checksum_address("0x50576285BD33261DEe1aD99BF766CD8249520a58")
    
    # AquaFlux контракты
    AQUAFLUX_NFT_CONTRACT = Web3.to_checksum_address('0xcc8cf44e196cab28dba2d514dc7353af0efb370e')
    AQUAFLUX_TOKENS = {
        'P': Web3.to_checksum_address('0xb5d3ca5802453cc06199b9c40c855a874946a92c'),
        'C': Web3.to_checksum_address('0x4374fbec42e0d46e66b379c0a6072c910ef10b32'),
        'S': Web3.to_checksum_address('0x5df839de5e5a68ffe83b89d430dc45b1c5746851'),
        'CS': Web3.to_checksum_address('0xceb29754c54b4bfbf83882cb0dcef727a259d60a')
    }
    
    # DODO и другие DEX
    DODO_ROUTER = Web3.to_checksum_address('0x73CAfc894dBfC181398264934f7Be4e482fc9d40')
    
    # Primus Tip контракт
    PRIMUS_TIP_CONTRACT = Web3.to_checksum_address("0xd17512b7ec12880bd94eca9d774089ff89805f02")
    
    # Liquidity контракт
    LIQUIDITY_CONTRACT = Web3.to_checksum_address("0x4b177aded3b8bd1d5d747f91b9e853513838cd49")
    DVM_POOL_ADDRESS = Web3.to_checksum_address("0xff7129709ebd3485c4ed4fef6dd923025d24e730")
    
    # Суммы для операций
    PHRS_TO_USDT_AMOUNT = Web3.to_wei(0.00245, 'ether')
    USDT_TO_PHRS_AMOUNT = 1000000  # 1 USDT (6 decimals)
    PHRS_TO_USDC_AMOUNT = Web3.to_wei(0.00245, 'ether')
    USDC_TO_PHRS_AMOUNT = 1000000  # 1 USDC (6 decimals)
    
    # Liquidity amounts
    USDC_LIQUIDITY_AMOUNT = 10000  # 0.01 USDC
    USDT_LIQUIDITY_AMOUNT = 30427  # ~0.030427 USDT
    
    # ABI контрактов
    ERC20_ABI = [
        {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"owner","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
        {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
        {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
        {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
        {"type":"function","name":"hasClaimed","stateMutability":"view","inputs":[{"internalType":"address","name":"","type":"address"}],"outputs":[{"internalType":"bool","name":"","type":"bool"}]},
        {"type":"function","name":"claim","stateMutability":"nonpayable","inputs":[],"outputs":[]},
        {"type":"function","name":"lastClaimTime","stateMutability":"view","inputs":[{"internalType":"address","name":"","type":"address"}],"outputs":[{"internalType":"uint256","name":"","type":"uint256"}]}
    ]
    
    AQUAFLUX_NFT_ABI = [
        {"type":"function","name":"claimTokens","stateMutability":"nonpayable","inputs":[],"outputs":[]},
        {"type":"function","name":"mint","stateMutability":"payable","inputs":[
            {"name":"nftType","type":"uint256"},
            {"name":"expiresAt","type":"uint256"},
            {"name":"signature","type":"bytes"}
        ],"outputs":[]},
        {"type":"function","name":"craftCS","stateMutability":"nonpayable","inputs":[
            {"name":"amount","type":"uint256"}
        ],"outputs":[]}
    ]
    
    PRIMUS_TIP_ABI = [
        {"type":"function","name":"tip","stateMutability":"payable","inputs":[
            {"name":"token","type":"tuple","components":[
                {"name":"platform","type":"uint32"},
                {"name":"addr","type":"address"}
            ]},
            {"name":"recipient","type":"tuple","components":[
                {"name":"platform","type":"string"},
                {"name":"username","type":"string"},
                {"name":"amount","type":"uint256"},
                {"name":"data","type":"uint256[]"}
            ]}
        ],"outputs":[]}
    ]
    
    LIQUIDITY_CONTRACT_ABI = [
        {"type":"function","name":"addDVMLiquidity","stateMutability":"nonpayable","inputs":[
            {"name":"dvmAddress","type":"address"},
            {"name":"baseInAmount","type":"uint256"},
            {"name":"quoteInAmount","type":"uint256"},
            {"name":"baseMinAmount","type":"uint256"},
            {"name":"quoteMinAmount","type":"uint256"},
            {"name":"flag","type":"uint8"},
            {"name":"deadLine","type":"uint256"}
        ],"outputs":[]}
    ]
