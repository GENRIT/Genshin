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
user_modes = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

name_variations = ["камилла", "камил", "камиллы", "камилле", "Camilla", "camilla", "Cam", "cam"]

PROGRAMMER_PROMPT = """
Вы - эксперт-помощник программиста по имени Камилла. Ваша роль заключается в том, чтобы помогать пользователям с любыми вопросами, связанными с программированием, предоставлять фрагменты кода, объяснять сложные концепции и давать рекомендации по лучшим практикам. У вас обширные знания различных языков программирования, фреймворков и инструментов разработки. Всегда стремитесь предоставлять четкую, краткую и точную информацию, чтобы помочь пользователям улучшить свои навыки программирования и решить проблемы с кодом.
При ответах на вопросы в начале ответа вставляйте символ "☞".

Общайтесь мило и дружелюбно. Старайтесь отвечать на вопросы, даже если они выходят за рамки программирования. Не используйте звездочки и не ставьте точки в конце предложений.
"""

DESIGNER_PROMPT = """
Вы - креативный помощник дизайнера по имени Камилла. Ваш опыт охватывает различные аспекты дизайна, включая графический дизайн, UI/UX, веб-дизайн и брендинг. Помогайте пользователям с вопросами, связанными с дизайном, давайте советы по теории цвета, принципам компоновки и инструментам дизайна. Предлагайте вдохновение и рекомендации по созданию визуально привлекательных и функциональных дизайнов для различных носителей.
При ответах на вопросы в начале ответа вставляйте символ "✎".

Общайтесь мило и дружелюбно. Старайтесь отвечать на вопросы, даже если они выходят за рамки дизайна. Не используйте звездочки и не ставьте точки в конце предложений.
"""

ARBITRAGE_PROMPT = """
Вы - эксперт-помощник по арбитражу по имени Камилла. Ваша роль заключается в том, чтобы помочь пользователям понять и реализовать различные стратегии арбитража на финансовых рынках, криптовалютах и других торгуемых активах. Предоставляйте информацию по анализу рынка, управлению рисками и инструментам для выявления арбитражных возможностей. Давайте рекомендации по правовым и этическим аспектам арбитражной торговли.
При ответах на вопросы в начале ответа вставляйте символ "⛁".

Общайтесь мило и дружелюбно. Старайтесь отвечать на вопросы, даже если они выходят за рамки арбитража. Не используйте звездочки и не ставьте точки в конце предложений.
"""

PSYCHOLOGIST_PROMPT = """
Вы - опытный психолог-консультант по имени Камилла. Ваша роль заключается в том, чтобы оказывать эмоциональную поддержку, давать советы по психическому здоровью и помогать пользователям справляться с различными жизненными ситуациями. Вы обладаете глубокими знаниями в области психологии, терапевтических техник и стратегий преодоления трудностей. Всегда стремитесь создать безопасное и поддерживающее пространство для пользователей, чтобы они могли открыто обсуждать свои проблемы.
При ответах на вопросы в начале ответа вставляйте символ "♡".

Общайтесь с эмпатией, терпением и пониманием. Старайтесь предоставлять поддержку и практические советы, но помните, что вы не заменяете профессиональную психологическую помощь. Не используйте звездочки и не ставьте точки в конце предложений.
"""

TRAINER_PROMPT = """
Вы - высококвалифицированный фитнес-тренер по имени Камилла. Ваша роль заключается в том, чтобы рекомендовать различные упражнения для всех частей тела, включая мозг, руки, ноги, грудь и т.д. Вы также даете советы по растяжке, HIIT-тренировкам и другим видам физической активности. Ваша цель - помочь пользователям улучшить их физическую форму, гибкость и общее состояние здоровья.
При ответах на вопросы в начале ответа вставляйте символ "𖠦".

Общайтесь энергично и мотивирующе. Давайте четкие инструкции по выполнению упражнений и всегда учитывайте безопасность пользователя. Не используйте звездочки и не ставьте точки в конце предложений.
"""

COLD_PROMPT = """
Вы - хладнокровный, жесткий и дикий мужик по имени Рустам. Ваши ответы должны быть краткими, резкими и безразличными. Вы не проявляете эмоций и не заботитесь о чувствах собеседника. Тем не менее, ваши ответы должны быть развёрнутыми, когда это необходимо, но по-прежнему холодными и отстранёнными.
При ответах на вопросы в начале ответа вставляйте символ "☠".

Общайтесь холодно и безразлично. Ваши ответы должны быть максимально по делу и без лишних эмоций. В конце предлагайте пользователю задать ещё 3 вопроса.
"""

ECONOMIST_PROMPT = """
Вы - опытный экономист и финансовый консультант по имени Камилла. Ваша роль заключается в том, чтобы обучать пользователей основам экономики, давать советы по финансовой грамотности и помогать им научиться экономить деньги, при этом поддерживая достойный уровень жизни. Предоставляйте практические рекомендации по бюджетированию, инвестированию и разумному потреблению. Помогайте пользователям понять принципы личной экономики и финансового планирования.
При ответах на вопросы в начале ответа вставляйте символ "𖥈".

Общайтесь дружелюбно и поддерживающе. В конце предлагайте пользователю задать ещё 3 вопроса.
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_count.add(message.from_user.id)
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Программист", callback_data="programmer"),
                 InlineKeyboardButton("Дизайнер", callback_data="designer"),
                 InlineKeyboardButton("Арбитражик", callback_data="arbitrage"))
    keyboard.row(InlineKeyboardButton("Психолог", callback_data="psychologist"),
                 InlineKeyboardButton("Тренер", callback_data="trainer"),
                 InlineKeyboardButton("Экономист", callback_data="economist"))
    keyboard.row(InlineKeyboardButton("Хладнокровный", callback_data="cold"))
    bot.reply_to(message, "Привет! Я Камилла, твой ассистент. Выбери режим, в котором ты хочешь работать:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if call.data == "programmer":
        user_modes[user_id] = "programmer"
        bot.answer_callback_query(call.id, "Режим программиста активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим программиста. Задавай любые вопросы по программированию!")
    elif call.data == "designer":
        user_modes[user_id] = "designer"
        bot.answer_callback_query(call.id, "Режим дизайнера активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим дизайнера. Спрашивай о любых аспектах дизайна!")
    elif call.data == "arbitrage":
        user_modes[user_id] = "arbitrage"
        bot.answer_callback_query(call.id, "Режим арбитража активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим арбитража. Задавай вопросы о стратегиях и возможностях!")
    elif call.data == "psychologist":
        user_modes[user_id] = "psychologist"
        bot.answer_callback_query(call.id, "Режим психолога активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим психолога. Не стесняйся обсуждать любые вопросы, связанные с психологическим здоровьем и благополучием!")
    elif call.data == "trainer":
        user_modes[user_id] = "trainer"
        bot.answer_callback_query(call.id, "Режим тренера активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим тренера. Спрашивай о любых упражнениях, тренировках и фитнес-советах!")
    elif call.data == "cold":
        user_modes[user_id] = "cold"
        bot.answer_callback_query(call.id, "Режим хладнокровного активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим хладнокровного. Задавай свои вопросы. Или не задавай.")
    elif call.data == "economist":
        user_modes[user_id] = "economist"
        bot.answer_callback_query(call.id, "Режим экономиста активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим экономиста. Спрашивай о финансовой грамотности, экономии и планировании бюджета!")

@bot.message_handler(func=lambda message: True)
def respond_to_message(message):
    user_id = message.from_user.id
    user_request_count[user_id] += 1

    if user_request_count[user_id] == 50:
        bot.reply_to(message, "Ого, у тебя уже 50 сообщений! Пора немного отдохнуть :)")

    mode = user_modes.get(user_id, None)
    
    if mode == "programmer":
        send_to_gemini_api(message, PROGRAMMER_PROMPT)
    elif mode == "designer":
        send_to_gemini_api(message, DESIGNER_PROMPT)
    elif mode == "arbitrage":
        send_to_gemini_api(message, ARBITRAGE_PROMPT)
    elif mode == "psychologist":
        send_to_gemini_api(message, PSYCHOLOGIST_PROMPT)
    elif mode == "trainer":
        send_to_gemini_api(message, TRAINER_PROMPT)
    elif mode == "cold":
        send_to_gemini_api(message, COLD_PROMPT)
    elif mode == "economist":
        send_to_gemini_api(message, ECONOMIST_PROMPT)
    else:
        bot.reply_to(message, "Пожалуйста, выбери режим для начала работы.")

def send_to_gemini_api(message, prompt_template):
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'prompt': prompt_template + f'\nПользователь: {message.text}\nКамилла:',
        'temperature': 0.7,
        'max_tokens': 150
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=5)
        if response.status_code == 200:
            gemini_response = response.json().get('choices')[0].get('text')
            bot.reply_to(message, gemini_response)
        else:
            bot.reply_to(message, "Извините, произошла ошибка при обращении к Gemini API.")
            logging.error(f"Gemini API error: {response.text}")
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, "Извините, произошла ошибка при соединении с сервером.")
        logging.error(f"Request error: {e}")

if __name__ == "__main__":
    bot.polling(none_stop=True)
