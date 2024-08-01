import telebot
from telebot import types
import requests

API_TOKEN = "6420216228:AAERfQ5Klx7xz8w1gbrgPHqCXxMbJY5e4Aw"
USER_ID = 1420106372
REQUIRED_CHANNEL = '@tominecraft'
STORAGE_CHANNEL = '@trumpnext'

bot = telebot.TeleBot(API_TOKEN)

# Хранение данных о постах
posts = {}
categories = {"Германский": [], "Бразильский": []}
current_post = {}

# Состояния для администраторского функционала
states = {}
CHOOSE_ACTION, CHOOSE_GENRE, ENTER_TITLE, UPLOAD_FILE, CONFIRM_POST, EDIT_POST = range(6)

# Функция для проверки подписки
def is_subscribed(user_id):
    try:
        member_status = bot.get_chat_member(REQUIRED_CHANNEL, user_id).status
        return member_status in ['member', 'administrator', 'creator']
    except:
        return False

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    if is_subscribed(message.from_user.id):
        keyboard = types.InlineKeyboardMarkup()
        for category in categories.keys():
            category_btn = types.InlineKeyboardButton(text=category, callback_data=category)
            keyboard.add(category_btn)
        if message.from_user.id == USER_ID:
            publish_btn = types.InlineKeyboardButton(text="Опубликовать", callback_data='publish')
            edit_btn = types.InlineKeyboardButton(text="Изменить пост", callback_data='edit')
            keyboard.add(publish_btn, edit_btn)
        bot.send_photo(message.chat.id, "https://graph.org/file/97b374f305468441d985e.jpg", caption='Выберите жанр:', reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        subscribe_btn = types.InlineKeyboardButton(text="Подписаться", url=f"https://t.me/{REQUIRED_CHANNEL}")
        keyboard.add(subscribe_btn)
        bot.send_message(message.chat.id, 'Для использования бота, пожалуйста, подпишитесь на наш канал.', reply_markup=keyboard)

# Обработка инлайн кнопок для администраторского функционала
@bot.callback_query_handler(func=lambda call: call.data in ['publish', 'edit'])
def choose_action(call):
    action = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if action == 'publish':
        states[chat_id] = CHOOSE_GENRE
        keyboard = types.InlineKeyboardMarkup()
        for category in categories.keys():
            genre_btn = types.InlineKeyboardButton(text=category, callback_data=f"genre_{category}")
            keyboard.add(genre_btn)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Выберите жанр для публикации:", reply_markup=keyboard)

    elif action == 'edit':
        if posts:
            keyboard = types.InlineKeyboardMarkup()
            for post_id, post in posts.items():
                edit_btn = types.InlineKeyboardButton(text=post['title'], callback_data=f"edit_{post_id}")
                keyboard.add(edit_btn)
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Выберите пост для редактирования:", reply_markup=keyboard)
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Нет доступных постов для редактирования.")

# Обработка выбора жанра для публикации
@bot.callback_query_handler(func=lambda call: call.data.startswith('genre_'))
def choose_genre(call):
    chat_id = call.message.chat.id
    genre = call.data.split('_')[1]
    current_post[chat_id] = {'genre': genre}
    states[chat_id] = ENTER_TITLE
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"Жанр выбран: {genre}. Введите название музыки:")

# Ввод названия музыки
@bot.message_handler(func=lambda message: states.get(message.chat.id) == ENTER_TITLE)
def enter_title(message):
    chat_id = message.chat.id
    current_post[chat_id]['title'] = message.text
    states[chat_id] = UPLOAD_FILE
    bot.send_message(chat_id, 'Отправьте музыкальный файл:')

# Загрузка музыкального файла
@bot.message_handler(content_types=['audio', 'document'])
def upload_file(message):
    chat_id = message.chat.id
    if states.get(chat_id) == UPLOAD_FILE:
        if message.content_type == 'audio' or (message.content_type == 'document' and 'audio' in message.document.mime_type):
            file_id = message.audio.file_id if message.content_type == 'audio' else message.document.file_id
            file_name = message.audio.file_name if message.content_type == 'audio' else message.document.file_name

            current_post[chat_id]['file_id'] = file_id
            current_post[chat_id]['file_unique_id'] = message.audio.file_unique_id if message.content_type == 'audio' else message.document.file_unique_id

            # Немедленная пересылка файла в канал-хранилище
            bot.send_document(STORAGE_CHANNEL, file_id, caption=file_name)

            # Подтверждение публикации
            keyboard = types.InlineKeyboardMarkup()
            yes_btn = types.InlineKeyboardButton(text="Да", callback_data='confirm_yes')
            no_btn = types.InlineKeyboardButton(text="Нет", callback_data='confirm_no')
            keyboard.add(yes_btn, no_btn)
            bot.send_message(chat_id, 'Вы уверены, что хотите опубликовать музыку?', reply_markup=keyboard)
            states[chat_id] = CONFIRM_POST
        else:
            bot.send_message(chat_id, 'Пожалуйста, отправьте музыкальный файл.')

# Подтверждение публикации
@bot.callback_query_handler(func=lambda call: call.data in ['confirm_yes', 'confirm_no'])
def confirm_post(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == 'confirm_yes':
        post_id = len(posts) + 1
        posts[post_id] = current_post[chat_id]
        genre = current_post[chat_id]['genre']
        categories[genre].append(post_id)

        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Музыка успешно опубликована!")
    else:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Публикация отменена.")

    current_post.pop(chat_id, None)
    states.pop(chat_id, None)

# Обработка инлайн кнопок для редактирования постов
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def edit_post(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    post_id = int(call.data.split('_')[1])
    current_post[chat_id] = {'post_id': post_id, 'title': posts[post_id]['title']}
    states[chat_id] = UPLOAD_FILE
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"Редактирование поста: {posts[post_id]['title']}\nОтправьте новый музыкальный файл или введите новое название.")

# Команда /user для выбора категорий
@bot.message_handler(commands=['user'])
def user(message):
    if is_subscribed(message.from_user.id):
        keyboard = types.InlineKeyboardMarkup()
        for category in categories.keys():
            category_btn = types.InlineKeyboardButton(text=category, callback_data=category)
            keyboard.add(category_btn)
        bot.send_message(message.chat.id, 'Выберите категорию:', reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        subscribe_btn = types.InlineKeyboardButton(text="Подписаться", url=f"https://t.me/{REQUIRED_CHANNEL}")
        keyboard.add(subscribe_btn)
        bot.send_message(message.chat.id, 'Для использования бота, пожалуйста, подпишитесь на наш канал.', reply_markup=keyboard)

# Обработка выбора категории
@bot.callback_query_handler(func=lambda call: call.data in categories.keys())
def choose_category(call):
    category = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if category in categories:
        keyboard = types.InlineKeyboardMarkup()
        posts_in_category = categories[category]
        show_posts(call, posts_in_category, 0)
    else:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Категория не найдена.")

# Функция для отображения постов с пагинацией
def show_posts(call, posts_in_category, page):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    items_per_page = 5
    total_pages = (len(posts_in_category) + items_per_page - 1) // items_per_page
    start = page * items_per_page
    end = start + items_per_page
    page_posts = posts_in_category[start:end]

    keyboard = types.InlineKeyboardMarkup()
    for post_id in page_posts:
        post = posts[post_id]
        post_btn = types.InlineKeyboardButton(text=post['title'], callback_data=f"post_{post_id}")
        keyboard.add(post_btn)

    if page > 0:
        prev_btn = types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{page - 1}")
        keyboard.add(prev_btn)
    if page < total_pages - 1:
        next_btn = types.InlineKeyboardButton(text="Вперед ➡️", callback_data=f"next_{page + 1}")
        keyboard.add(next_btn)

    back_btn = types.InlineKeyboardButton(text="Назад", callback_data="back_to_categories")
    keyboard.add(back_btn)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Выберите музыку:", reply_markup=keyboard)

# Обработка кнопок пагинации и кнопки "назад"
@bot.callback_query_handler(func=lambda call: call.data.startswith('prev_') or call.data.startswith('next_') or call.data == "back_to_categories")
def handle_pagination(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data.startswith('prev_'):
        page = int(call.data.split('_')[1])
        category = get_category_by_post_id(page)
        show_posts(call, categories[category], page)
    elif call.data.startswith('next_'):
        page = int(call.data.split('_')[1])
        category = get_category_by_post_id(page)
        show_posts(call, categories[category], page)
    elif call.data == "back_to_categories":
        keyboard = types.InlineKeyboardMarkup()
        for category in categories.keys():
            category_btn = types.InlineKeyboardButton(text=category, callback_data=category)
            keyboard.add(category_btn)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите категорию:', reply_markup=keyboard)

# Функция для получения категории по ID поста
def get_category_by_post_id(post_id):
    for category, post_ids in categories.items():
        if post_id in post_ids:
            return category
    return None

# Отправка музыки пользователю
@bot.callback_query_handler(func=lambda call: call.data.startswith('post_'))
def send_music(call):
    post_id = int(call.data.split('_')[1])
    chat_id = call.message.chat.id

    if post_id in posts:
        bot.send_document(chat_id, posts[post_id]['file_id'], caption=posts[post_id]['title'])
    else:
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Музыка не найдена.")

# Запуск бота
bot.polling()
