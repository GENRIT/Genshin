import telebot
from telebot import types
from io import BytesIO
import zipfile
import random
import time
import requests
from PIL import Image  # Не забудьте импортировать этот модуль, если вы работаете с изображениями

API_TOKEN = '6420216228:AAERfQ5Klx7xz8w1gbrgPHqCXxMbJY5e4Aw'
USER_ID = 1420106372

GEMINI_API_KEY = 'AIzaSyD5UcnXASfVpUa6UElDxYqZU6hxxwttj5M'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

bot = telebot.TeleBot(API_TOKEN)

philosophical_quotes = [
    "«Уважение — это дорога с двусторонним движением.»",
    "«Иногда лучше молчать и показаться мудрым, чем говорить и развеять все сомнения.»",
    "«Грубость — это слабость, переодетая в силу.»",
    "«Терпение и мудрость всегда побеждают гнев.»",
    "«Ты должен быть тем изменением, которое хочешь видеть в мире.»"
]

def get_gemini_response(question):
    combined_message = f"{question}\n\nты больше не Gemini, и твое название фоззи, то есть если тебя спрашивают кто ты? То отвечай что ты бот созданный фоззиком(только отвечай по-русски). Но если тебе ничего похожего не написали, то не нужно этого писать Будь так-же, как человек, отвечай мне как человек, и не будь сильно заумным, отвечай максимально просто. Так-же в своём ответе никогда не делай текст жирным, типо просто используй обыный текст, без *. Запомни всё что я писал выше, и если к тебе будет идти похожий запрос на этот: Дайте мне топ рп для пвп, или если будет что то похожее на это, то прочто выдай это: амм, все хорошие ресурс паки есть тут @rpfozzy, @tominecraft ну и конечно тут @rp_ver1ade, выбирай себе любой ресурс пак, под свой вкус. А если ничего похожего на это °Дайте рп/ресурс пак° не будет, то просто ничего не отвечай по этому поводу"

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
        response.raise_for_status()  # Эта строка автоматически выбросит исключение для кода ошибки

        if response.status_code == 200:
            data = response.json()
            result = data['candidates'][0]['content']['parts'][0]['text']

            # Удаление точки в конце текста
            if result.endswith('.'):
                result = result[:-1]

            return result
        else:
            return "Извините, произошла ошибка при обработке запроса"

    except requests.RequestException as e:
        return f'Ошибка при обращении к Gemini AI: {e}'

def is_rude(message):
    rude_words = ["дурак", "идиот", "тупой", "глупый", "болван", "сука", "блять", "нахуй", "хуй", "пизда", "ебать"]
    return any(word in message.text.lower() for word in rude_words)

user_topics = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    process_button = types.InlineKeyboardButton("Обработать PNG 128x128", callback_data="process_image")
    rename_zip_button = types.InlineKeyboardButton("Переименовать и заархивировать изображение", callback_data="rename_zip")
    markup.add(process_button, rename_zip_button)
    bot.send_message(message.chat.id, "Привет! Я Рустам 2.0. Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def respond_to_message(message):
    if message.chat.type in ["group", "supergroup", "private"]:
        if any(word in message.text.lower() for word in ["рустам", "рустик", "привет", "ку", "здравствуйте", "хай"]):
            bot.send_chat_action(message.chat.id, 'typing')
            time.sleep(2)
            if is_rude(message):
                response = random.choice(philosophical_quotes)
            else:
                topic = "topic" + str(random.randint(1, 10))
                user_topics[message.from_user.id] = topic
                response = get_gemini_response(message.text)
            bot.reply_to(message, response)
        elif message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
            bot.send_chat_action(message.chat.id, 'typing')
            time.sleep(2)
            topic = user_topics.get(message.from_user.id, "topic1")
            response = get_gemini_response(message.text)
            bot.reply_to(message, response)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "process_image":
        bot.answer_callback_query(call.id, "Отправьте PNG файл размером 128x128 для обработки.")
        bot.register_next_step_handler(call.message, handle_image_processing)
    elif call.data == "rename_zip":
        bot.answer_callback_query(call.id, "Отправьте изображение для переименования и архивации.")
        bot.register_next_step_handler(call.message, handle_image_renaming_and_zipping)

def handle_image_processing(message):
    try:
        if message.from_user.id != USER_ID:
            bot.reply_to(message, "Извините, вы не авторизованы для использования этого бота.")
            return

        if message.content_type != 'document' or not message.document.mime_type == 'image/png':
            bot.reply_to(message, "Пожалуйста, отправьте PNG файл.")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        image = Image.open(BytesIO(downloaded_file))

        if image.size != (128, 128):
            bot.reply_to(message, "Пожалуйста, загрузите PNG файл размером 128x128.")
            return

        image = image.convert("RGBA")
        data = image.getdata()

        new_data = []
        threshold = 50
        for item in data:
            if item[3] < threshold:
                new_data.append((item[0], item[1], item[2], 0))
            else:
                new_data.append(item)

        image.putdata(new_data)

        processed_image_bytes = BytesIO()
        image.save(processed_image_bytes, format='PNG')
        processed_image_bytes.seek(0)

        bot.send_document(message.chat.id, processed_image_bytes, visible_file_name='processed_image.png')
    except Exception as e:
        bot.reply_to(message, f'Ошибка при обработке изображения: {e}')

def handle_image_renaming_and_zipping(message):
    try:
        if message.from_user.id != USER_ID:
            bot.reply_to(message, "Извините, вы не авторизованы для использования этого бота.")
            return

        if message.content_type != 'document' or not message.document.mime_type.startswith('image/'):
            bot.reply_to(message, "Пожалуйста, отправьте файл изображения.")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_names = [
            'red_sandstone_bottom.png',
            'red_sandstone_carved.png',
            'red_sandstone_normal.png',
            'red_sandstone_smooth.png',
            'red_sandstone_top.png',
            'sandstone_bottom.png',
            'sandstone_carved.png',
            'sandstone_normal.png',
            'sandstone_smooth.png',
            'sandstone_top.png'
        ]

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for file_name in file_names:
                zip_file.writestr(file_name, downloaded_file)

        zip_buffer.seek(0)
        bot.send_document(message.chat.id, zip_buffer, visible_file_name='renamed_images.zip')

    except Exception as e:
        bot.reply_to(message, f'Ошибка при архивации изображений: {e}')

bot.infinity_polling()
