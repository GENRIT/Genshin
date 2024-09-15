import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import logging
import time
from collections import defaultdict

API_KEY = '7441566490:AAEH1IMGBiIvisBjkH0DmLavDydsbd8T-24'
GEMINI_API_KEY = 'AIzaSyD5UcnXASfVpUa6UElDxYqZU6hxxwttj5M'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
CHANNEL_ID = '@Monopolist_Survivor'  # ID или @юзернейм вашего канала

bot = telebot.TeleBot(API_KEY, parse_mode="Markdown")
user_count = set()
user_request_count = defaultdict(int)
user_modes = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

POST_PROMPT = """Создай пост в стиле вдохновляющих и познавательных бизнес-заметок с краткими, но сильными тезисами. 
Тема постов должна быть связана с финансами, бизнесом, финансовой грамотностью и мотивацией. 
Стиль постов — простой и понятный, как будто человек делится личным опытом. 
Каждый пост должен заканчиваться фразой, подчеркивающей основную мысль, и содержать подпись "©️ Монополист" и хештеги, например, #Бизнес или #Финграм. 
Тон должен быть уверенным, но не высокомерным. Приводите примеры из реальной жизни или истории компаний. 
Оформляй посты с короткими абзацами для удобства восприятия."""

# Начальное приветствие
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_count.add(message.from_user.id)
    bot.reply_to(message, "Привет! Я бот, который поможет создавать бизнес-посты. Напиши /generate, чтобы создать пост.")

# Генерация поста
@bot.message_handler(commands=['generate'])
def generate_post(message):
    user_id = message.from_user.id
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Генерация поста с помощью Gemini
    generated_post = get_gemini_response(POST_PROMPT)
    
    # Отправка пользователю для одобрения
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Одобрить", callback_data=f"approve_{user_id}"))
    
    bot.send_message(message.chat.id, generated_post, reply_markup=markup)

# Обработка инлайн-кнопок
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_post(call):
    user_id = call.data.split('_')[1]
    if call.from_user.id == int(user_id):
        # Отправка поста в канал
        bot.send_message(CHANNEL_ID, call.message.text)
        bot.answer_callback_query(call.id, "Пост отправлен в канал!")
    else:
        bot.answer_callback_query(call.id, "У вас нет прав для одобрения этого поста.")

# Функция для обращения к Gemini API
def get_gemini_response(prompt, max_retries=3, retry_delay=5):
    payload = {
        "prompt": prompt,
        "model": "gemini-pro",
        "temperature": 0.7,
        "maxOutputTokens": 500
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GEMINI_API_KEY}'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            result = data['candidates'][0]['content']
            return result
        except Exception as e:
            logging.error(f"Ошибка при обращении к Gemini API (попытка {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return "Извините, произошла ошибка при генерации поста."

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Ошибка в основном цикле: {e}")
            time.sleep(15)
