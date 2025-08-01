![Python](https://github.com/NotHennadii/PHAROS_FARM_BOT/blob/main/6835835683568356.PNG?raw=true))
**Автоматизированный бот для выполнения операций в тестовой сети Pharos Network**
## PHAROS FUCKER BOT
*Автоматизированный бот для выполнения операций в тестовой сети Pharos Network**


## ✨ Возможности

- 🎯 **Daily Check-in** - автоматический ежедневный чекин
- 💰 **Faucet Claim** - клейм бесплатных токенов
- 🔄 **Token Swaps** - автоматические свапы токенов
- 💧 **Liquidity Pool** - добавление ликвидности
- 🎁 **Tips** - отправка чаевых в X (Twitter)
- 🌊 **AquaFlux** - операции с NFT и токенами
- 🧵 **Многопоточность** - параллельная обработка кошельков
- 🔒 **Proxy Support** - поддержка прокси серверов

## 📋 Требования

- Python 3.8 или выше
- Приватные ключи кошельков
- Интернет соединение
- (Опционально) Прокси серверы

## 🛠️ Установка простая скачать и запустить файл start.bat
## 🛠️ Установка для умных

### 1. Скачайте проект
```bash
git clone https://github.com/your-repo/pharos-bot.git
cd pharos-bot
```

### 2. Создайте виртуальное окружение (рекомендуется)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac  
source venv/bin/activate
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

## ⚙️ Настройка

### 1. Создайте файл `accounts.txt`
Добавьте приватные ключи ваших кошельков (по одному на строку):
```
0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
```

### 2. (Опционально) Создайте файл `proxy.txt`
Если используете прокси, добавьте их в формате:
```
http://user:pass@ip:port
socks5://user:pass@ip:port
http://ip:port
```

## 🚀 Запуск

```bash
python main.py
```

## 📖 Использование

### Настройка бота
При запуске бот предложит простую настройку:

```
🔧 Bot Configuration
Choose operations to perform:

Enable faucet operations? [y/n]: y
Enable daily checkin? [y/n]: y  
Enable AquaFlux operations? [y/n]: n
Enable swap operations? [y/n]: y
How many swaps to perform per wallet [1-20]: 8
Will perform 8 swaps with 1-10 sec delays

Enable liquidity operations? [y/n]: y
How many liquidity operations per wallet [1-10]: 3
Will add liquidity 3 times with 1-10 sec delays

Enable tip operations? [y/n]: y
Enter X username to tip (without @): username
How many tips per wallet [1-10]: 2
Will send 2 tips with 10-30 sec delays

Use proxies? [y/n]: y
How many wallets to process simultaneously [1-10]: 5
Will process 5 wallets simultaneously
```

### Рекомендуемые настройки

**Для новичков:**
- Swaps: 4-6
- Liquidity: 1-2
- Tips: 1-3
- Parallel wallets: 1 (безопасно)

**Для опытных:**
- Swaps: 8-12
- Liquidity: 3-5
- Tips: 3-5
- Parallel wallets: 5-10 (быстро)

## 🔧 Функции

### 1. Daily Check-in ✅
- Автоматический ежедневный чекин
- Получение поинтов
- Клейм фаусета (0.2 PHRS)

### 2. Token Swaps 🔄
- WPHRS ↔ USDC
- WPHRS ↔ USDT  
- USDC ↔ USDT
- Случайный выбор пар
- Автоматические задержки 1-10 сек

### 3. Liquidity Pool 💧
- Добавление ликвидности USDC/USDT
- Автоматические аппрувы
- Случайные задержки 1-10 сек

### 4. Tips 🎁
- Отправка чаевых в X (Twitter)
- Случайные суммы
- Задержки 10-30 сек для безопасности

### 5. Многопоточность 🧵
- Обработка 1-20 кошельков одновременно
- Автоматическое распределение нагрузки
- Интеллектуальные задержки

## 📊 Логи

Бот показывает подробные логи:
```
[ 16:53:01 ] | PHRS Balance: 0.392 PHRS
[ 16:53:04 ] | ✅ Daily checkin completed successfully!
[ 16:53:08 ] | ⏳ Faucet already claimed
[ 16:53:12 ] | Swap 1/8: WPHRS -> USDC
[ 16:53:15 ] | ✅ Swap successful!
```

## ⚠️ Безопасность

- **Приватные ключи**: Никогда не делитесь файлом `accounts.txt`
- **Прокси**: Используйте надежные прокси для анонимности
- **Задержки**: Встроенные случайные задержки предотвращают бан
- **Ошибки**: Бот автоматически обрабатывает ошибки и продолжает работу

## 🐛 Решение проблем

### Ошибка "Module not found"
```bash
pip install -r requirements.txt
```

### Ошибка "Invalid private key"
- Проверьте формат ключей в `accounts.txt`
- Ключи должны начинаться с `0x`

### Ошибка "Connection failed"
- Проверьте интернет соединение
- Попробуйте другие прокси

### Ошибка "Insufficient balance"
- Пополните баланс кошелька
- Включите faucet операции

## 📈 Статистика

Бот показывает статистику после каждого цикла:
```
All batches completed!
Total successful wallets: 8
Total failed wallets: 2  
Success rate: 80.0%
```

## 🔄 Циклы

- Бот работает в 24-часовых циклах
- Автоматический перезапуск каждые 24 часа
- Показывает таймер до следующего цикла

## 💡 Советы

1. **Начните с малого** - используйте 1-2 кошелька для тестирования
2. **Мониторьте балансы** - убедитесь что достаточно токенов для операций
3. **Используйте прокси** - для лучшей анонимности
4. **Проверяйте логи** - следите за ошибками и успешными операциями
5. **Настройте параллельность** - больше потоков = быстрее, но рискованнее

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи на ошибки
2. Убедитесь что все зависимости установлены
3. Проверьте формат приватных ключей
4. Попробуйте запустить с одним кошельком

## 📄 Лицензия

MIT License - свободное использование и модификация.

## ⭐ Благодарности

- Pharos Network за отличный тестнет
- Сообщество за фидбек и тестирование

---

**🚀 Удачного фарминга в Pharos Network!**
