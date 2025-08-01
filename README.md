![Python](https://github.com/NotHennadii/PHAROS_FARM_BOT/blob/main/6835835683568356.PNG?raw=true)

# PHAROS Bot v3.0

Автоматизированный бот для сети Pharos с поддержкой множественных операций и прокси.

## 🚀 Установка

1. Запустите `start.bat` - установит все зависимости автоматически
2. Создайте файлы конфигурации:

### accounts.txt
```
0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321
```

### proxy.txt (опционально)
```
http://user:pass@ip:port
socks5://user:pass@ip:port
http://192.168.1.1:8080
```

## 🔧 Основные функции

- **Faucet** - Автоматический клейм токенов
- **Daily Checkin** - Ежедневные чекины
- **AquaFlux** - Клейм, крафт, минт NFT
- **Swaps** - Автоматические обмены токенов
- **Liquidity** - Добавление ликвидности
- **Brokex Trading** - Торговые операции
- **OpenFi DeFi** - Lending/borrowing операции
- **Tips** - Отправка чаевых

## ⚙️ Запуск

```bash
python main.py
```

Бот предложит интерактивную настройку всех параметров.

## 🔒 Proxy Manager

Отдельный менеджер прокси:
```bash
python proxy_manager.py
```

Автоматически распределяет прокси по кошелькам или настраивает индивидуально.

## 📋 Особенности

- Поддержка многопоточности
- Индивидуальные прокси для каждого кошелька  
- Автоматические retry при ошибках
- 24/7 циклы с умными задержками
- Детальное логирование операций
## 📄 Лицензия

MIT License - свободное использование и модификация.

## ⭐ Благодарности

- Pharos Network за отличный тестнет
- Сообщество за фидбек и тестирование

---

**🚀 Удачного фарминга в Pharos Network!**
