# 🤖 VPN Telegram Bot

Профессиональный Telegram бот для продажи VPN подписок на российском рынке. Создан с чистым кодом на Python и готов к промышленному использованию.

## ✨ Основные возможности

### 👥 Для пользователей
- 🛒 Покупка VPN подписок (1, 3, 6, 12 месяцев)
- 💳 Множественные способы оплаты (ЮMoney, QIWI, криптовалюты)
- 📱 Автоматическая выдача VPN конфигураций
- 👤 Личный кабинет с управлением подпиской
- 🎁 Реферальная программа с вознаграждениями
- 💬 Техподдержка 24/7
- 🔒 QR-коды для быстрой настройки

### 🔧 Для администраторов
- 📊 Подробная статистика и аналитика
- 👥 Управление пользователями
- 🔑 Управление VPN ключами
- 📢 Массовая рассылка сообщений
- 💰 Отчеты по доходам
- 📝 Логирование всех действий

## 🚀 Быстрый старт

### Автоматическая установка (рекомендуется)

```bash
# Клонируем репозиторий
git clone https://github.com/Vlasik2010/TgBot_vpn.git
cd TgBot_vpn

# Устанавливаем зависимости
pip install -r requirements.txt

# Запускаем мастер настройки
python setup.py

# Запускаем бота
python run.py
```

### Ручная установка

#### 1. Установка зависимостей

```bash
# Клонируем репозиторий
git clone https://github.com/Vlasik2010/TgBot_vpn.git
cd TgBot_vpn

# Создаем виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Устанавливаем зависимости
pip install -r requirements.txt
```

#### 2. Настройка конфигурации

```bash
# Копируем пример конфигурации
cp .env.example .env

# Редактируем .env файл
nano .env
```

#### 3. Настройка .env файла

```bash
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_IDS=123456789,987654321

# Database Configuration  
DATABASE_URL=sqlite:///vpn_bot.db
# Для PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/vpn_bot

# Payment Configuration
YOOMONEY_TOKEN=your_yoomoney_token
QIWI_TOKEN=your_qiwi_token

# VPN Configuration
VPN_SERVER_URL=your_vpn_server.com
VPN_API_KEY=your_vpn_api_key

# Bot Configuration
DEFAULT_LANGUAGE=ru
DEBUG=False
LOG_LEVEL=INFO

# Subscription Plans (in rubles)
PLAN_1_MONTH_PRICE=299
PLAN_3_MONTH_PRICE=799
PLAN_6_MONTH_PRICE=1499
PLAN_12_MONTH_PRICE=2699
```

#### 4. Запуск бота

```bash
# Запуск бота
python run.py

# Или
python -m bot.main
```

## 📁 Структура проекта

```
TgBot_vpn/
├── bot/                    # Основной код бота
│   ├── __init__.py
│   ├── main.py            # Точка входа
│   ├── config/            # Конфигурация
│   │   ├── __init__.py
│   │   └── settings.py    # Настройки бота
│   ├── handlers/          # Обработчики команд
│   │   ├── __init__.py
│   │   ├── main.py        # Основные команды
│   │   └── admin.py       # Админ команды
│   ├── models/            # Модели базы данных
│   │   ├── __init__.py
│   │   └── database.py    # SQLAlchemy модели
│   └── utils/             # Утилиты
│       ├── __init__.py
│       └── helpers.py     # Вспомогательные функции
├── locales/               # Локализация
│   ├── __init__.py
│   └── ru.py             # Русская локализация
├── logs/                  # Логи (создается автоматически)
├── data/                  # Данные приложения
├── backups/              # Резервные копии
├── .env.example          # Пример конфигурации
├── .env                  # Ваша конфигурация (не коммитится)
├── .gitignore
├── requirements.txt      # Зависимости Python
├── setup.py             # Мастер установки
├── Dockerfile           # Docker образ
├── docker-compose.yml   # Docker композиция
├── test_bot.py          # Тесты функциональности
├── validate_bot.py      # Валидация структуры
└── README.md            # Этот файл
```

## 💳 Настройка платежных систем

### ЮMoney (Яндекс.Деньги)
1. Зарегистрируйтесь на [yoomoney.ru](https://yoomoney.ru)
2. Получите токен в разделе API
3. Добавьте токен в `.env` файл

### QIWI
1. Зарегистрируйтесь на [qiwi.com](https://qiwi.com)
2. Получите API ключ в личном кабинете
3. Добавьте ключ в `.env` файл

### Криптовалюты
- Поддержка Bitcoin платежей
- Автоматическое создание адресов
- QR-коды для удобной оплаты

## 🔧 Настройка VPN сервера

Бот поддерживает интеграцию с различными VPN серверами:

- **WireGuard** - рекомендуется для высокой производительности
- **OpenVPN** - классическое решение
- **Custom API** - собственное решение

Добавьте URL вашего VPN сервера и API ключ в конфигурацию.

## 📊 Административные команды

- `/admin` - Панель администратора
- Просмотр статистики пользователей
- Управление VPN ключами
- Массовая рассылка
- Просмотр логов

## 🛡️ Безопасность

- ✅ Валидация всех пользовательских данных
- ✅ Логирование административных действий
- ✅ Защита от SQL инъекций (SQLAlchemy ORM)
- ✅ Обработка ошибок и исключений
- ✅ Безопасное хранение конфигурации
- ✅ Timezone-aware datetime (устранены предупреждения)
- ✅ Правильная обработка сессий БД

## 📈 Мониторинг и логирование

Бот ведет подробные логи:
- Действия пользователей
- Платежи и подписки
- Административные действия
- Ошибки и исключения

Логи сохраняются в папке `logs/` с ротацией и кодировкой UTF-8.

## 🧪 Тестирование

```bash
# Полный тест функциональности
python test_bot.py

# Валидация структуры проекта
python validate_bot.py

# Проверка конфигурации
python -c "from bot.config.settings import Config; Config.validate(); print('OK')"
```

## 🐳 Развертывание с Docker

### Простое развертывание

```bash
# Сборка образа
docker build -t vpn-bot .

# Запуск с .env файлом
docker run -d --env-file .env --name vpn-bot vpn-bot
```

### Развертывание с PostgreSQL

```bash
# Запуск всей системы
docker-compose up -d

# Просмотр логов
docker-compose logs -f vpn-bot

# Остановка
docker-compose down
```

## 🔄 Обновление

```bash
# Получаем последние изменения
git pull origin main

# Обновляем зависимости
pip install -r requirements.txt

# Перезапускаем бота
systemctl restart vpn-bot  # если используете systemd
# или
docker-compose restart vpn-bot  # если используете Docker
```

## 🆕 Что исправлено в этой версии

- ✅ Устранены все предупреждения о deprecated `datetime.utcnow()`
- ✅ Исправлено предупреждение ConversationHandler
- ✅ Улучшена обработка сессий базы данных
- ✅ Добавлена поддержка криптовалютных платежей
- ✅ Улучшен VPN Manager с реалистичной генерацией ключей
- ✅ Расширена система логирования с поддержкой UTF-8
- ✅ Добавлен мастер установки `setup.py`
- ✅ Созданы Docker файлы для простого развертывания
- ✅ Улучшена структура проекта и документация
- ✅ Добавлены комплексные тесты и валидация
- ✅ Исправлены все импорты и зависимости

## 📞 Поддержка

- 📧 Email: support@example.com
- 💬 Telegram: @your_support_bot
- 📖 Документация: [Wiki](../../wiki)

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста:

1. Форкните репозиторий
2. Создайте ветку для ваших изменений
3. Сделайте коммит с описанием изменений
4. Создайте Pull Request

## ⭐ Благодарности

Спасибо всем разработчикам и контрибьюторам, которые помогли создать этот проект!

---

**Сделано с ❤️ для российского рынка VPN услуг**
