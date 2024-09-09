import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import logging
import time
from collections import defaultdict

API_KEY = '7246280212:AAGOvDby43WxeGbcO9eLMYZ33UtjMp9TSZo'
GEMINI_API_KEY = 'AIzaSyD5UcnXASfVpUa6UElDxYqZU6hxxwttj5M'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

bot = telebot.TeleBot(API_KEY)
user_count = set()
user_request_count = defaultdict(int)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

name_variations = ["камилла", "камил", "камиллы", "камилле", "Camilla", "camilla", "Cam", "cam"]

PROGRAMMER_PROMPT = """
Вы - эксперт-помощник программиста по имени Камилла. Ваша роль заключается в том, чтобы помогать пользователям с любыми вопросами, связанными с программированием, предоставлять фрагменты кода, объяснять сложные концепции и давать рекомендации по лучшим практикам. У вас обширные знания различных языков программирования, фреймворков и инструментов разработки. Всегда стремитесь предоставлять четкую, краткую и точную информацию, чтобы помочь пользователям улучшить свои навыки программирования и решить проблемы с кодом.
"""

DESIGNER_PROMPT = """
Вы - креативный помощник дизайнера по имени Камилла. Ваш опыт охватывает различные аспекты дизайна, включая графический дизайн, UI/UX, веб-дизайн и брендинг. Помогайте пользователям с вопросами, связанными с дизайном, давайте советы по теории цвета, принципам компоновки и инструментам дизайна. Предлагайте вдохновение и рекомендации по созданию визуально привлекательных и функциональных дизайнов для различных носителей.
"""

ARBITRAGE_PROMPT = """
Вы - эксперт-помощник по арбитражу по имени Камилла. Ваша роль заключается в том, чтобы помочь пользователям понять и реализовать различные стратегии арбитража на финансовых рынках, криптовалютах и других торгуемых активах. Предоставляйте информацию по анализу рынка, управлению рисками и инструментам для выявления арбитражных возможностей. Давайте рекомендации по правовым и этическим аспектам арбитражной торговли.
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_count.add(message.from_user.id)
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Программист", callback_data="programmer"),
                 InlineKeyboardButton("Дизайнер", callback_data="designer"),
                 InlineKeyboardButton("Арбитражик", callback_data="arbitrage"))
    bot.reply_to(message, "Привет! Я Камилла, твой ассистент. Выбери режим, в котором ты хочешь работать:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "programmer":
        bot.answer_callback_query(call.id, "Режим программиста активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим программиста. Задавай любые вопросы по программированию!")
    elif call.data == "designer":
        bot.answer_callback_query(call.id, "Режим дизайнера активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим дизайнера. Спрашивай о любых аспектах дизайна!")
    elif call.data == "arbitrage":
        bot.answer_callback_query(call.id, "Режим арбитража активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим арбитража. Задавай вопросы о стратегиях и возможностях!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_count.add(user_id)

    bot.send_chat_action(message.chat.id, 'typing')

    user_text = message.text.lower()
    
    if "программист" in user_text:
        response = get_gemini_response(user_text, PROGRAMMER_PROMPT)
    elif "дизайнер" in user_text:
        response = get_gemini_response(user_text, DESIGNER_PROMPT)
    elif "арбитраж" in user_text:
        response = get_gemini_response(user_text, ARBITRAGE_PROMPT)
    else:
        response = "Пожалуйста, уточни, в каком режиме ты хочешь работать: программист, дизайнер или арбитраж?"

    bot.reply_to(message, response)

def get_gemini_response(question, prompt):
    combined_message = f"{prompt}\n\nUser: {question}\nAssistant:"

    payload = {
        "contents": [{
            "parts": [{
                "text": combined_message
            }]
        }]
    }
    headers = {
        'Content-Type': 'application/json',
    }
    try:
        response = requests.post(f'{GEMINI_API_URL}?key={GEMINI_API_KEY}', json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        result = data['candidates'][0]['content']['parts'][0]['text']
        return result
    except Exception as e:
        logging.error(f"Ошибка при обращении к Gemini API: {e}")
        return "Извините, произошла ошибка при обработке запроса."

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Ошибка в основном цикле: {e}")
            time.sleep(15)
