import telebot
from telebot import types
from PIL import Image
from io import BytesIO
import zipfile
import random

# Вставьте сюда ваш токен и ID
API_TOKEN = '6420216228:AAFgkx1SNpvvFek9ACHdMJ-h4IirruRqCTI'
USER_ID = 1420106372

bot = telebot.TeleBot(API_TOKEN)

unique_responses = {
    "topic1": [
        "Привет! Как твои дела?",
        "Что нового?",
        "Чем занимаешься в свободное время?",
        "Как ты провёл сегодняшний день?",
        "Какие у тебя планы на выходные?",
        "Отлично, спасибо! А у тебя?",
        "Ничего особенного, всё по-старому.",
        "Читаю книгу и отдыхаю.",
        "Сегодня был довольно продуктивный день.",
        "Думаю поехать за город."
    ],
    "topic2": [
        "Какую книгу ты недавно прочитал?",
        "Какие фильмы тебе нравятся?",
        "Есть ли у тебя любимый сериал?",
        "Что ты думаешь о современных книгах?",
        "Есть ли у тебя любимый жанр литературы?",
        "Недавно прочитал '1984' Джорджа Оруэлла.",
        "Люблю научную фантастику и драмы.",
        "Сейчас смотрю 'Игру престолов'.",
        "Современные книги часто затрагивают важные темы.",
        "Предпочитаю детективы и триллеры."
    ],
    "topic3": [
        "Какую музыку ты слушаешь?",
        "У тебя есть любимый исполнитель?",
        "Какие жанры музыки тебе нравятся?",
        "Слушаешь ли ты музыку во время работы?",
        "Какая песня тебе нравится больше всего?",
        "Слушаю рок и поп.",
        "Очень люблю музыку группы Queen.",
        "Чаще всего слушаю джаз и блюз.",
        "Да, музыка помогает мне сосредоточиться.",
        "Сейчас моя любимая песня - 'Bohemian Rhapsody'."
    ],
    "topic4": [
        "Как ты относишься к искусству?",
        "Есть ли у тебя любимый художник?",
        "Какую выставку ты бы хотел посетить?",
        "Что для тебя искусство?",
        "Какие виды искусства тебе нравятся?",
        "Искусство - это способ самовыражения.",
        "Мне нравится работа Ван Гога.",
        "Хотел бы посетить выставку в Лувре.",
        "Искусство помогает понять мир.",
        "Я люблю живопись и скульптуру."
    ],
    "topic5": [
        "Какой твой любимый спорт?",
        "За какую команду ты болеешь?",
        "Занимаешься ли ты каким-то спортом?",
        "Как ты относишься к активному отдыху?",
        "Есть ли у тебя спортивные достижения?",
        "Люблю футбол и теннис.",
        "Болею за команду Барселона.",
        "Иногда играю в баскетбол.",
        "Активный отдых - это отличная возможность отдохнуть.",
        "Участвовал в марафоне и занял призовое место."
    ],
    "topic6": [
        "Какие страны ты бы хотел посетить?",
        "Какое самое интересное место ты посетил?",
        "Есть ли у тебя мечта путешествовать по миру?",
        "Какой город тебе понравился больше всего?",
        "Что для тебя значит путешествие?",
        "Хотел бы побывать в Японии и Австралии.",
        "Мне очень понравилось в Париже.",
        "Да, мечтаю объездить весь мир.",
        "Очень понравился Лондон.",
        "Путешествие - это возможность увидеть что-то новое."
    ],
    "topic7": [
        "Как ты проводишь выходные?",
        "Что ты обычно делаешь по вечерам?",
        "Какой у тебя хобби?",
        "Как ты отдыхаешь после работы?",
        "Есть ли у тебя традиции на выходные?",
        "Чаще всего встречаюсь с друзьями.",
        "Смотрю фильмы или читаю книги.",
        "Люблю фотографировать.",
        "После работы люблю заниматься спортом.",
        "Каждые выходные хожу в парк."
    ],
    "topic8": [
        "Веришь ли ты в судьбу?",
        "Считаешь ли ты, что у каждого есть своя цель в жизни?",
        "Как ты думаешь, что такое счастье?",
        "Что для тебя важно в жизни?",
        "Как ты относишься к философии?",
        "Да, я верю в судьбу.",
        "Уверен, что у каждого есть свое предназначение.",
        "Счастье - это состояние внутреннего мира.",
        "Для меня важны семья и друзья.",
        "Философия помогает понять смысл жизни."
    ],
    "topic9": [
        "Как ты относишься к науке?",
        "Какую научную теорию ты считаешь самой интересной?",
        "Кто твой любимый ученый?",
        "Какие научные открытия тебя впечатляют?",
        "Как ты думаешь, будущее науки?",
        "Наука - это ключ к прогрессу.",
        "Очень интересна теория относительности.",
        "Мой любимый ученый - Альберт Эйнштейн.",
        "Меня впечатляет квантовая физика.",
        "Думаю, наука изменит наш мир к лучшему."
    ],
    "topic10": [
        "Как ты видишь будущее технологий?",
        "Какие технологии тебя впечатляют?",
        "Как ты думаешь, что нас ждет через 50 лет?",
        "Что ты думаешь о роботах?",
        "Какие технологии ты бы хотел увидеть?",
        "Будущее технологий обещает быть захватывающим.",
        "Меня впечатляют искусственный интеллект и VR.",
        "Через 50 лет мы будем жить в совершенно новом мире.",
        "Роботы могут значительно облегчить нашу жизнь.",
        "Хотел бы увидеть технологию телепортации."
    ]
}

philosophical_responses = [
    "Уважение - это дорога с двусторонним движением.",
    "Иногда лучше молчать и показаться мудрым, чем говорить и развеять все сомнения.",
    "Грубость - это слабость, переодетая в силу.",
    "Терпение и мудрость всегда побеждают гнев.",
    "Ты должен быть тем изменением, которое хочешь видеть в мире."
]

def get_unique_response(topic):
    responses = unique_responses.get(topic, ["Извините, я не знаю, как ответить на эту тему."])
    return random.choice(responses)

def is_rude(message):
    rude_words = ["дурак", "идиот", "тупой", "глупый", "болван"]
    return any(word in message.text.lower() for word in rude_words)

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
        if "рустам" in message.text.lower():
            bot.send_chat_action(message.chat.id, 'typing')  # Отображение "печатает..."
            if is_rude(message):
                response = random.choice(philosophical_responses)
            else:
                topic = "topic" + str(random.randint(1, 10))
                response = get_unique_response(topic)
            bot.send_message(message.chat.id, response)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "process_image":
        bot.answer_callback_query(call.id, "Отправьте PNG файл размером 128x128 для обработки.")
        bot.register_next_step_handler(call.message, handle_image_processing)
    elif call.data == "rename_zip":
        bot.answer_callback_query(call.id, "Отправьте изображение для переименования и архивации.")
        bot.register_next_step_handler(call.message, handle_image_renaming_and_zipping)

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

bot.infinity_polling()
