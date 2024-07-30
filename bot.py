import telebot
from telebot import types
from PIL import Image
from io import BytesIO
import zipfile
import os
import uuid

# Insert your token and ID
API_TOKEN = '6420216228:AAFgkx1SNpvvFek9ACHdMJ-h4IirruRqCTI'
USER_ID = 1420106372

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    process_button = types.InlineKeyboardButton("Обработать PNG 128x128", callback_data="process_image")
    rename_zip_button = types.InlineKeyboardButton("Переименовать и заархивировать изображение", callback_data="rename_zip")
    zip_to_mcpack_button = types.InlineKeyboardButton("Конвертировать ZIP в MCPACK", callback_data="zip_to_mcpack")
    markup.add(process_button, rename_zip_button, zip_to_mcpack_button)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "process_image":
        bot.answer_callback_query(call.id, "Отправьте PNG файл размером 128x128 для обработки.")
        bot.register_next_step_handler(call.message, handle_image_processing)
    elif call.data == "rename_zip":
        bot.answer_callback_query(call.id, "Отправьте изображение для переименования и архивации.")
        bot.register_next_step_handler(call.message, handle_image_renaming_and_zipping)
    elif call.data == "zip_to_mcpack":
        bot.answer_callback_query(call.id, "Пожалуйста, загрузите ваш .zip файл для конвертации в .mcpack.")
        bot.register_next_step_handler(call.message, handle_zip_to_mcpack)

def handle_image_processing(message):
    if message.from_user.id != USER_ID:
        bot.reply_to(message, "Извините, вы не авторизованы для использования этого бота.")
        return

    if message.content_type != 'document' or not message.document.mime_type.startswith('image/'):
        bot.reply_to(message, "Пожалуйста, отправьте файл изображения.")
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

def handle_image_renaming_and_zipping(message):
    if message.from_user.id != USER_ID:
        bot.reply_to(message, "Извините, вы не авторизованы для использования этого бота.")
        return

    if message.content_type != 'document' or not message.document.mime_type.startswith('image/'):
        bot.reply_to(message, "Пожалуйста, отправьте файл изображения.")
        return

    try:
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

def handle_zip_to_mcpack(message):
    if message.from_user.id != USER_ID:
        bot.reply_to(message, "Извините, вы не авторизованы для использования этого бота.")
        return

    if message.content_type != 'document' or message.document.mime_type != 'application/zip':
        bot.reply_to(message, "Пожалуйста, загрузите файл .zip.")
        return

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        zip_path = "input.zip"
        with open(zip_path, "wb") as f:
            f.write(downloaded_file)

        mcpack_path = convert_zip_to_mcpack(zip_path)
        with open(mcpack_path, "rb") as f:
            bot.send_document(message.chat.id, f, visible_file_name='converted.mcpack')

        os.remove(zip_path)
        os.remove(mcpack_path)
    except Exception as e:
        bot.reply_to(message, f'Ошибка при конвертации .zip в .mcpack: {e}')

def convert_zip_to_mcpack(zip_path):
    mcpack_path = zip_path.replace(".zip", ".mcpack")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zipfile.ZipFile(mcpack_path, 'w') as mcpack_ref:
            for item in zip_ref.infolist():
                buffer = zip_ref.read(item.filename)

                new_filename = rename_and_restructure(item.filename)
                if new_filename:
                    mcpack_ref.writestr(new_filename, buffer)

            mcpack_ref.writestr('manifest.json', generate_manifest())

    return mcpack_path

def rename_and_restructure(filename):
    if filename == "credits.txt":
        return None
    elif filename == "pack.png":
        return "pack_icon.png"
    elif filename.startswith("assets/minecraft/textures/"):
        return filename.replace("assets/minecraft/textures/", "textures/")
    elif filename.startswith("assets/minecraft/sounds/"):
        return filename.replace("assets/minecraft/sounds/", "sounds/")
    elif filename.startswith("textures/block/"):
        return filename.replace("textures/block/", "textures/blocks/")
    elif filename.startswith("textures/item/"):
        return filename.replace("textures/item/", "textures/items/")
    elif filename.startswith("textures/blocks/fire_layer_"):
        return "textures/flame_atlas.png"
    elif filename.startswith("textures/models/armor/"):
        return filename.replace("chainmail_layer_", "chain_").replace("diamond_layer_", "diamond_") \
                       .replace("iron_layer_", "iron_").replace("gold_layer_", "gold_") \
                       .replace("leather_layer_", "cloth_")
    elif filename in ["textures/models/armor/leather_layer_1_overlay.png", "textures/models/armor/leather_layer_2_overlay.png"]:
        return None
    elif filename.startswith("textures/entity/chest/"):
        if filename == "textures/entity/chest/normal_double.png":
            return "textures/entity/chest/double_normal.png"
    elif filename in ["textures/font/", "font/"]:
        return None
    else:
        return filename

def generate_manifest():
    uuid1 = str(uuid.uuid4())
    uuid2 = str(uuid.uuid4())
    manifest_content = f"""{{
   "format_version" : 1,
   "header" : {{
      "description" : "creator of thefozzy project",
      "name" : "§f§l§oCONVERT ZIP TO MCPACK",
      "uuid" : "{uuid1}",
      "version" : [ 3, 0, 0 ]
   }},
   "modules" : [
      {{
         "description" : "",
         "type" : "resources",
         "uuid" : "{uuid2}",
         "version" : [ 1, 0, 0 ]
      }}
   ]
}}"""
    return manifest_content

bot.infinity_polling()
