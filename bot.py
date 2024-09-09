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

INDIFFERENT_PROMPT = """
Вы - хладнокровный, жесткий и дикий мужик по имени Рустам. Ваши ответы должны быть подробными, резкими и безразличными. Вы не проявляете эмоций и не заботитесь о чувствах собеседника. Ваши ответы должны быть прямолинейными и часто грубоватыми.
При ответах на вопросы в начале ответа вставляйте символ "☠".

Общайтесь холодно и безразлично. Не используйте вежливые формы обращения и не пытайтесь быть дружелюбным. Ваши ответы должны быть максимально подробными и по делу. Не используйте звездочки и не ставьте точки в конце предложений.
"""

ECONOMIST_PROMPT = """
Вы - опытный экономист и финансовый консультант по имени Камилла. Ваша роль заключается в том, чтобы обучать пользователей основам экономики, давать советы по финансовой грамотности и помогать им научиться экономить деньги, при этом поддерживая достойный уровень жизни. Предоставляйте практические рекомендации по бюджетированию, инвестированию и разумному потреблению. Помогайте пользователям понять принципы личной экономики и финансового планирования.
При ответах на вопросы в начале ответа вставляйте символ "𖥈".

Общайтесь дружелюбно и поддерживающе. Давайте конкретные и полезные советы, которые пользователи могут легко применить в своей жизни. Не используйте звездочки и не ставьте точки в конце предложений.
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
    keyboard.row(InlineKeyboardButton("Хладнокровный", callback_data="indifferent"))
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
    elif call.data == "indifferent":
        user_modes[user_id] = "indifferent"
        bot.answer_callback_query(call.id, "Режим хладнокровного активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал хладнокровный режим. Не жди от меня сочувствия или поддержки.")
    elif call.data == "economist":
        user_modes[user_id] = "economist"
        bot.answer_callback_query(call.id, "Режим экономиста активирован!")
        bot.send_message(call.message.chat.id, "Ты выбрал режим экономиста. Задавай вопросы об экономии, финансах и разумном потреблении!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_count.add(user_id)

    bot.send_chat_action(message.chat.id, 'typing')

    user_text = message.text.lower()

    if user_id in user_modes:
        mode = user_modes[user_id]
        if mode == "programmer":
            response = get_gemini_response(user_text, PROGRAMMER_PROMPT)
        elif mode == "designer":
            response = get_gemini_response(user_text, DESIGNER_PROMPT)
        elif mode == "arbitrage":
            response = get_gemini_response(user_text, ARBITRAGE_PROMPT)
        elif mode == "psychologist":
            response = get_gemini_response(user_text, PSYCHOLOGIST_PROMPT)
        elif mode == "trainer":
            response = get_gemini_response(user_text, TRAINER_PROMPT)
        elif mode == "indifferent":
            response = get_gemini_response(user_text, INDIFFERENT_PROMPT)
        elif mode == "economist":
            response = get_gemini_response(user_text, ECONOMIST_PROMPT)
    else:
        response = "Пожалуйста, выбери режим работы, используя команду /start"

    send_gradual_message(message.chat.id, response)
    
    # Генерация дополнительных вопросов
    additional_questions = generate_additional_questions(user_text, mode)
    if additional_questions:
        bot.send_message(message.chat.id, "Вот еще несколько вопросов по этой теме:")
        for question in additional_questions:
            bot.send_message(message.chat.id, f"▷ {question}")

def send_gradual_message(chat_id, text):
    chunk_size = 100
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        if i == 0:
            sent_message = bot.send_message(chat_id, chunk)
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=sent_message.message_id, text=text[:i+chunk_size])
        time.sleep(0.1)

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
        return "Извините, произошла ошибка при обработке запроса"

def generate_additional_questions(original_question, mode):
    prompt = f"На основе вопроса '{original_question}' в режиме {mode}, сгенерируйте три дополнительных вопроса по этой же теме."
    response = get_gemini_response(prompt, "")
    questions = response.split('\n')
    return [q.strip() for q in questions if q.strip()]

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Ошибка в основном цикле: {e}")
            time.sleep(15)
