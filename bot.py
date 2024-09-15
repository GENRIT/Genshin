import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import logging
from collections import defaultdict

API_KEY = '7441566490:AAEH1IMGBiIvisBjkH0DmLavDydsbd8T-24'
GEMINI_API_KEY = 'AIzaSyD5UcnXASfVpUa6UElDxYqZU6hxxwttj5M'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

bot = telebot.TeleBot(API_KEY, parse_mode="Markdown")
user_count = set()
user_request_count = defaultdict(int)
user_modes = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Пред-промт для генерации постов
POST_PROMPT = """Создай пост в стиле вдохновляющих и познавательных бизнес-заметок с краткими, но сильными тезисами. 
Тема постов должна быть связана с финансами, бизнесом, финансовой грамотностью и мотивацией. 
Стиль постов — простой и понятный, как будто человек делится личным опытом. 
Каждый пост должен заканчиваться фразой, подчеркивающей основную мысль, и содержать подпись "©️ Монополист" и хештеги, например, #Бизнес или #Финграм. 
Тон должен быть уверенным, но не высокомерным. Приводите примеры из реальной жизни или истории компаний. Оформляй посты с короткими абзацами для удобства восприятия.
"""

# Генерация постов с помощью API Gemini
def generate_post():
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "gemini-pro",
        "prompt": POST_PROMPT,
        "max_tokens": 500
    }
    response = requests.post(GEMINI_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result['text']
    else:
        return "Ошибка при генерации поста."

# Хэндлер для команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который помогает создавать бизнес-посты. Нажмите кнопку ниже для генерации поста.")
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Сгенерировать пост", callback_data="generate_post")
    markup.add(button)
    bot.send_message(message.chat.id, "Нажмите кнопку для создания поста:", reply_markup=markup)

# Обработка нажатия кнопки
@bot.callback_query_handler(func=lambda call: call.data == "generate_post")
def send_post(call):
    post = generate_post()
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Одобрить и отправить в канал", callback_data="approve_post")
    markup.add(button)
    bot.send_message(call.message.chat.id, post, reply_markup=markup)

# Обработка одобрения поста и отправка в канал
@bot.callback_query_handler(func=lambda call: call.data == "approve_post")
def approve_post(call):
    channel_id = '@Monopolist_Survivor'  # Замените на ваш канал
    bot.send_message(channel_id, call.message.text)
    bot.send_message(call.message.chat.id, "Пост был отправлен в канал.")

# Запуск бота
bot.polling(none_stop=True)
