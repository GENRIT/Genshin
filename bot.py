import telebot
from telebot import types
from PIL import Image
from io import BytesIO

# Вставьте сюда ваш токен и ID
API_TOKEN = '6420216228:AAFgkx1SNpvvFek9ACHdMJ-h4IirruRqCTI'
USER_ID = 1420106372

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправьте мне PNG файл размером 128x128 для обработки.")

@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):
    if message.from_user.id != USER_ID:
        bot.reply_to(message, "Извините, вы не авторизованы для использования этого бота.")
        return

    try:
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

bot.infinity_polling()
