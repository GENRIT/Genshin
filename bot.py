import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import logging
import json

API_KEY = '7441566490:AAEH1IMGBiIvisBjkH0DmLavDydsbd8T-24'
GEMINI_API_KEY = 'AIzaSyD5UcnXASfVpUa6UElDxYqZU6hxxwttj5M'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
bot = telebot.TeleBot(API_KEY, parse_mode="Markdown")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Пред-промпт для генерации постов
POST_PROMPT = """Создай пост в стиле вдохновляющих и познавательных бизнес-заметок с краткими, но сильными тезисами. Тема постов должна быть связана с финансами, бизнесом, финансовой грамотностью и мотивацией. Стиль постов — простой и понятный, как будто человек делится личным опытом. Каждый пост должен заканчиваться фразой, подчеркивающей основную мысль, и содержать подпись "©️ Монополист" и хештеги, например, #Бизнес или #Финграм. Тон должен быть уверенным, но не высокомерным. Приводите примеры из реальной жизни или истории компаний. Оформляй посты с короткими абзацами для удобства восприятия."""

# Функция для генерации контента через Gemini API
def generate_post():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GEMINI_API_KEY}'
    }
    data = {
        "prompt": POST_PROMPT,
        "temperature": 0.7,
        "maxOutputTokens": 300
    }
    
    response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        # Извлечение сгенерированного текста
        return result.get('generatedContent', 'Не удалось сгенерировать пост')
    else:
        logging.error(f"Error from Gemini API: {response.status_code} {response.text}")
        return 'Ошибка генерации поста'

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Нажмите кнопку для генерации бизнес-поста.")
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Сгенерировать пост", callback_data="generate_post"))
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# Обработка нажатия кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "generate_post":
        post = generate_post()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Одобрить", callback_data="approve_post"))
        # Отправка сгенерированного поста с кнопкой одобрения
        bot.send_message(call.message.chat.id, post, reply_markup=markup)
    
    elif call.data == "approve_post":
        # Если пост одобрен, пересылаем его в канал (замените CHANNEL_ID на ID вашего канала)
        CHANNEL_ID = '@Monopolist_Survivor'
        bot.forward_message(CHANNEL_ID, call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Пост был отправлен в канал!")

# Запуск бота
bot.polling(none_stop=True)
