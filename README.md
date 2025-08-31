# service_bot

Бот в телеграм предназначенный для записи на услуги, напоминании о записи и ведения статистики

### Подготовка к запуску

```bash
git clone https://github.com/ivg97/service_bot.git
cd service_bot
python3.12 -m venv venv
sourse venv/bin/activate
pip install -r requiremenets.txt
touch .env
```
В файл .env добавить следующие значения:
```text
TELEGRAM_BOT_TOKEN=SECRET_BOT_TOKEN
ADMIN_IDS=123456789
DATABASE_URL=sqlite:///bot.db
```
#### Запуск
`pythom src/main.py`

Получаете ответ:
```text
2025-09-01 00:50:44,691 - root - INFO - Бот запущен...
2025-09-01 00:50:44,692 - aiogram.dispatcher - INFO - Start polling
2025-09-01 00:50:44,755 - aiogram.dispatcher - INFO - Run polling for bot @name_bot id=id_bot - 'NAME_BOT'
```

