import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import logging
import time
from collections import defaultdict

API_KEY = '7441566490:AAEH1IMGBiIvisBjkH0DmLavDydsbd8T-24'
GEMINI_API_KEY = 'AIzaSyD5UcnXASfVpUa6UElDxYqZU6hxxwttj5M'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
CHANNEL_ID = '@Monopolist_Survivor'  # Замените на ваш канал

bot = telebot.TeleBot(API_KEY, parse_mode="Markdown")
user_count = set()
user_request_count = defaultdict(int)
user_modes = {}
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PROMPT = """Создай пост в стиле вдохновляющих и познавательных бизнес-заметок с краткими, но сильными тезисами. 
Тема постов должна быть связана с финансами, бизнесом, финансовой грамотностью и мотивацией. 
Стиль постов — простой и понятный, как будто человек делится личным опытом. 
Каждый пост должен заканчиваться фразой, подчеркивающей основную мысль, и содержать подпись "©️ Монополист" и хештеги, например, #Бизнес или #Финграм. 
Тон должен быть уверенным, но не высокомерным. Приводите примеры из реальной жизни или истории компаний. 
Оформляй посты с короткими абзацами для удобства восприятия."""

# Функция для отправки запроса в API Gemini
def generate_post():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GEMINI_API_KEY}',
    }
    
    data = {
        'prompt': PROMPT,
        'model': 'gemini-pro',
        'temperature': 0.7
    }
    
    response = requests.post(GEMINI_API_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['text']
    else:
        logging.error(f"Ошибка генерации поста: {response.status_code}, {response.text}")
        return None

# Хендлер команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Этот бот помогает создавать бизнес-посты. Нажми кнопку ниже, чтобы сгенерировать пост.")

# Хендлер для генерации поста
@bot.message_handler(commands=['generate'])
def send_post(message):
    post = generate_post()
    
    if post:
        # Инлайн-кнопка для одобрения поста
        markup = InlineKeyboardMarkup()
        approve_button = InlineKeyboardButton("Одобрить", callback_data="approve_post")
        markup.add(approve_button)
        
        bot.send_message(message.chat.id, post, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при генерации поста. Попробуйте снова.")

# Callback для одобрения поста
@bot.callback_query_handler(func=lambda call: call.data == "approve_post")
def approve_post(call):
    post = call.message.text
    bot.send_message(call.message.chat.id, "Пост одобрен и отправлен в канал!")
    
    # Отправка поста в канал
    bot.send_message(CHANNEL_ID, post)

# Запуск бота
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            time.sleep(5)
