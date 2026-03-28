# Telegram Meme Bot

Бот для добавления случайных подписей к картинкам.

## Функциональность

- Получение картинок от пользователя
- Добавление случайной подписи из файла-сборника
- Сохранение обработанных картинок
- Возможность поделиться картинкой в канале

## Установка

1. Клонируйте репозиторий:
\`\`\`bash
git clone https://github.com/ВАШ_USERNAME/telegram-meme-bot.git
cd telegram-meme-bot
\`\`\`

2. Создайте виртуальное окружение:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
\`\`\`

3. Установите зависимости:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Создайте файл `.env` на основе `.env.example`:
\`\`\`bash
cp .env.example .env
# Отредактируйте .env, добавьте ваш токен
\`\`\`

5. Запустите бота:
\`\`\`bash
python bot.py
\`\`\`

## Docker

\`\`\`bash
docker build -t telegram-meme-bot .
docker run -d --name meme-bot --env-file .env telegram-meme-bot
\`\`\`

## Лицензия

MIT
