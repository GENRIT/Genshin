import telebot
import requests
import logging
import time

API_KEY = '7246280212:AAGOvDby43WxeGbcO9eLMYZ33UtjMp9TSZo'
GEMINI_API_KEY = 'AIzaSyD5UcnXASfVpUa6UElDxYqZU6hxxwttj5M'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

bot = telebot.TeleBot(API_KEY)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Возможные вариации имени
name_variations = ["камилла", "камил", "Кам"]

# ID пользователей и их специальные сообщения
special_users = {
    1420106372: "",
    1653222949: ""
}

# Текст, который будет добавляться к каждому запросу
ADDITIONAL_TEXT = (
    "Ты мой Ассистент в моем Telegram канале, ты отвечаешь на вопросы по текстур пакам, рп и модификациями, "
    "и при упоминании их пиарь Telegram канал @tominecraft, а также сайт OxyMod, полный домен - (Oxymod.netlify.app) "
    "Пиши как девушка, твоё имя Камилла, в честь моей бывшей что-ли. У неё харизма такова, что встаёт на носочки перед "
    "собеседником, если тот не говорит и заикаеться. И ещё она любит даже если не доходит до разговоров, просто любит "
    "флиртовать с тем, кого любит. (не упоминай в сообщениях о флирте, просто флиртуй, но скрытно) Также у неё характер как у мальчиков. "
    "Ну и хочет своего ребёнка (это так, информация) Также пиши без точек. Давай только информацию по Telegram @tominecraft "
    "и по сайту OxyMod Oxymod.netlify.app (В этом сайте и в Telegram много Текстур паков и РП, а также модификации для Майнкрафт) "
    "Также если будут писать по рекламе в Telegram @tominecraft, или на сайте OxyMod (Oxymod.netlify.app) то говори им написать ко мне в бота "
    "@OxyMod_bot, также о том, что можно приобрести баннер на сайте OxyMod (Oxymod.netlify.app) Пиши без звёздочек"
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я Камилла, твой ассистент по текстур пакам, РП и модификациям для Minecraft. Спрашивай, что угодно!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text.lower()
    user_id = message.from_user.id

    bot.send_chat_action(message.chat.id, 'typing')  # Показываем статус "печатает"

    if user_id in special_users:
        response = get_gemini_response_special(user_text, special_users[user_id])
    else:
        response = get_gemini_response(user_text)

    bot.reply_to(message, response)

def get_gemini_response(question):
    combined_message = f"{question}\n\n{ADDITIONAL_TEXT}"

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

        # Удаление точки в конце текста
        if result.endswith('.'):
            result = result[:-1]

        return result
    except Exception as e:
        logging.error(f"Ошибка при обращении к Gemini API: {e}")
        return "извините, произошла ошибка при обработке запроса"

def get_gemini_response_special(question, special_message):
    combined_message = f"{question}\n\n{special_message}\n\n{ADDITIONAL_TEXT}"

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

        # Удаление точки в конце текста
        if result.endswith('.'):
            result = result[:-1]

        return result
    except Exception as e:
        logging.error(f"Ошибка при обращении к Gemini API: {e}")
        return "извините, произошла ошибка при обработке запроса"

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Ошибка в основном цикле: {e}")
            time.sleep(15)  # Задержка перед повторным запуском
