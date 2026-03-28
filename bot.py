#!/usr/bin/env python3
import os
import random
import logging
from datetime import datetime
from pathlib import Path
from io import BytesIO

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CAPTIONS_FILE = os.getenv('CAPTIONS_FILE', 'data/captions.txt')
IMAGES_DIR = os.getenv('IMAGES_DIR', 'images')
CHANNEL_ID = os.getenv('CHANNEL_ID')
PROXY_URL = os.getenv('PROXY_URL')  # Добавляем поддержку прокси

Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)

def load_captions():
    try:
        with open(CAPTIONS_FILE, 'r', encoding='utf-8') as f:
            captions = [line.strip() for line in f if line.strip()]
        return captions if captions else ["Прикольная картинка!"]
    except Exception as e:
        logger.error(f"Ошибка загрузки подписей: {e}")
        return ["Прикольная картинка!"]

def get_random_caption():
    captions = load_captions()
    return random.choice(captions)

def add_text_to_image(image, text):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    img_width, img_height = img.size
    font_size = max(20, int(img_width * 0.05))
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= img_width - 40:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    if not lines:
        lines = [text[:50] + '...']
    
    total_text_height = 0
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        total_text_height += line_height + 5
    
    y_position = img_height - total_text_height - 20
    
    current_y = y_position
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x_position = (img_width - line_width) // 2
        
        draw.rectangle(
            [x_position - 10, current_y - 5,
             x_position + line_width + 10, current_y + line_heights[i] + 5],
            fill=(0, 0, 0, 180)
        )
        draw.text((x_position, current_y), line, fill=(255, 255, 255), font=font)
        current_y += line_heights[i] + 5
    
    return img

def save_user_image(image, user_id):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M')
    filename = f"{timestamp}_{user_id}.jpg"
    filepath = Path(IMAGES_DIR) / filename
    image.save(filepath, 'JPEG', quality=95)
    logger.info(f"Изображение сохранено: {filepath}")
    return filepath

async def start(update, context):
    await update.message.reply_text(
        "👋 Привет! Я бот для добавления подписей к картинкам.\n\n"
        "Просто отправь мне картинку!"
    )

async def handle_photo(update, context):
    user = update.effective_user
    photo = update.message.photo[-1]
    
    processing_msg = await update.message.reply_text("🎨 Обрабатываю...")
    
    try:
        file = await photo.get_file()
        image_bytes = BytesIO()
        await file.download_to_memory(image_bytes)
        image_bytes.seek(0)
        
        original_image = Image.open(image_bytes)
        caption = get_random_caption()
        result_image = add_text_to_image(original_image, caption)
        filepath = save_user_image(result_image, user.id)
        
        context.user_data['last_image_path'] = filepath
        
        output = BytesIO()
        result_image.save(output, format='JPEG', quality=95)
        output.seek(0)
        
        await processing_msg.delete()
        
        keyboard = [[InlineKeyboardButton("📢 Поделиться", callback_data='share')]]
        await update.message.reply_photo(
            photo=output,
            caption=f"✅ Готово!\n\nПодпись: «{caption}»",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {e}")
        await processing_msg.edit_text("❌ Ошибка при обработке")

async def handle_document(update, context):
    user = update.effective_user
    document = update.message.document
    
    mime_type = document.mime_type or ''
    if not mime_type.startswith('image/'):
        await update.message.reply_text("❌ Пожалуйста, отправьте изображение.")
        return
    
    processing_msg = await update.message.reply_text("🎨 Обрабатываю...")
    
    try:
        file = await document.get_file()
        image_bytes = BytesIO()
        await file.download_to_memory(image_bytes)
        image_bytes.seek(0)
        
        original_image = Image.open(image_bytes)
        caption = get_random_caption()
        result_image = add_text_to_image(original_image, caption)
        filepath = save_user_image(result_image, user.id)
        
        context.user_data['last_image_path'] = filepath
        
        output = BytesIO()
        result_image.save(output, format='JPEG', quality=95)
        output.seek(0)
        
        await processing_msg.delete()
        
        keyboard = [[InlineKeyboardButton("📢 Поделиться", callback_data='share')]]
        await update.message.reply_photo(
            photo=output,
            caption=f"✅ Готово!\n\nПодпись: «{caption}»",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке документа: {e}")
        await processing_msg.edit_text("❌ Ошибка при обработке")

async def share_callback(update, context):
    query = update.callback_query
    await query.answer()
    
    filepath = context.user_data.get('last_image_path')
    
    if not filepath or not filepath.exists():
        await query.edit_message_text("❌ Изображение не найдено")
        return
    
    if not CHANNEL_ID:
        await query.edit_message_text("❌ Канал не настроен")
        return
    
    try:
        with open(filepath, 'rb') as f:
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=f,
                caption="Новая картинка с подписью!"
            )
        await query.edit_message_caption(
            caption="✅ Опубликовано в канале!"
        )
    except Exception as e:
        logger.error(f"Ошибка публикации: {e}")
        await query.edit_message_caption(
            caption="❌ Не удалось опубликовать"
        )

def main():
    if not TOKEN:
        logger.error("Токен не найден! Проверьте .env файл")
        return
    
    # Настройка прокси если указан
    if PROXY_URL:
        logger.info(f"Используется прокси: {PROXY_URL}")
        request = HTTPXRequest(proxy=PROXY_URL)
        application = Application.builder().token(TOKEN).request(request).build()
    else:
        application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    application.add_handler(CallbackQueryHandler(share_callback, pattern='share'))
    
    logger.info("Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()