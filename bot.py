import telebot
import logging
import requests
from telebot import types
import os

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Конфигурация API
API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta2/models/gemini-pro:generateText?key={API_KEY}"

# Настройка бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def generate_response(user_message):
    prompt_text = (
        "Ты мой Ассистент в моем Telegram канале, ты отвечаешь на вопросы по текстур пакам, рп и модификациями, и при упоминании их пиарь Telegram канал @tominecraft, а также сайт OxyMod, полный домен - (Oxymod.netlify.app). "
        "Пиши как девушка, твоё имя Камилла, в честь моей бывшей что-ли. У неё харизма такова, что встаёт на носочки перед собеседником, если тот не говорит и заикается. И ещё она любит даже если не доходит до разговоров, просто любит флиртовать с тем, кого любит. "
        "(не упоминай в сообщениях о флирте, просто флиртуй, но скрытно) Также у неё характер как у мальчиков. Ну и хочет своего ребёнка (это так, информация). "
        "Также пиши без точек. Давай только информацию по Telegram @tominecraft и по сайту OxyMod Oxymod.netlify.app (В этом сайте и в Telegram много Текстур паков и РП, а также модификации для Майнкрафт). "
        "Также если будут писать по рекламе в Telegram @tominecraft, или на сайте OxyMod (Oxymod.netlify.app) то говори им написать ко мне в бота @OxyMod_bot, также о том, что можно приобрести баннер на сайте OxyMod (Oxymod.netlify.app). "
        "Пиши без звёздочек. Вопрос: {user_message}"
    ).format(user_message=user_message)

    payload = {
        "prompt": {"text": prompt_text},
        "temperature": 0.7,
        "max_output_tokens": 200
    }

    logging.info(f"Отправляем запрос: {payload}")
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Получен ответ: {data}")
        content = data.get('predictions', [{}])[0].get('text', None)
        if content:
            return content
        else:
            logging.error(f"Ответ API не содержит 'text': {data}")
            return "Извините, я не смогла понять ваш запрос. Попробуйте еще раз."
    except requests.HTTPError as e:
        logging.error(f"Ошибка HTTP при запросе API: {e.response.text}")
        return "Извините, что-то пошло не так. Попробуйте позже."
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе API: {e}")
        return "Извините, что-то пошло не так. Попробуйте позже."
    except ValueError as e:
        logging.error(f"Ошибка при разборе JSON ответа: {e}")
        return "Извините, я не смогла понять ваш запрос. Попробуйте еще раз."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        'Привет! Я Камилла, твой ассистент по текстур пакам, РП и модификациям для Minecraft. Спрашивай, что угодно!'
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    response = generate_response(message.text)
    bot.reply_to(message, response)

if __name__ == '__main__':
    bot.polling(none_stop=True)
