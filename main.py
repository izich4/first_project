import telebot
from telebot import types
from config import BOT_TOKEN
from database import init_db, get_user_deadlines, add_deadline

# Подключаем бота с помощью токена
bot = telebot.TeleBot(BOT_TOKEN)

# Функция для создания кнопочного меню внизу экрана
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_add = types.KeyboardButton("➕ Добавить дедлайн")
    btn_list = types.KeyboardButton("📋 Мои дедлайны")
    btn_help = types.KeyboardButton("ℹ️ Помощь")

    # В первом ряду будут две кнопки, во втором — одна
    markup.add(btn_add, btn_list)
    markup.add(btn_help)
    return markup

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Привет, {user_name}! 👋\n\n"
        "Я бот для контроля учебных дедлайнов.\n"
        "Используй кнопки меню внизу экрана для управления задачами."
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=get_main_menu()
    )

# Обработчик команды /help и кнопки «ℹ️ Помощь»
@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
def send_help(message):
    help_text = (
        "📋 Как пользоваться ботом:\n\n"
        "• Нажми «➕ Добавить дедлайн», чтобы записать новую задачу.\n"
        "• Нажми «📋 Мои дедлайны», чтобы посмотреть список долгов.\n"
        "• Нажми /start, если меню случайно скрылось."
    )
    bot.send_message(message.chat.id, help_text)

# Проверка команды отмены ввода
def check_cancel(message):
    if message.text == '/cancel':
        bot.send_message(
            message.chat.id,
            "❌ Добавление дедлайна отменено.",
            reply_markup=get_main_menu()
        )
        return True
    return False

# Шаг 1: Начало диалога и запрос названия предмета
@bot.message_handler(func=lambda message: message.text == "➕ Добавить дедлайн")
def start_add_deadline(message):
    msg = bot.send_message(
        message.chat.id,
        "📚 Шаг 1 из 3. Введи название предмета (или /cancel для отмены):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, process_subject_step)

# Шаг 2: Получение предмета и запрос описания задачи
def process_subject_step(message):
    if check_cancel(message):
        return

    subject = message.text.strip()
    msg = bot.send_message(
        message.chat.id,
        f"📝 Шаг 2 из 3. Что именно нужно сдать по предмету «{subject}»?\n"
        "(например: Лабораторная работа №3)"
    )
    bot.register_next_step_handler(msg, process_task_step, subject)


# Шаг 3: Получение описания задачи и запрос даты сдачи
def process_task_step(message, subject):
    if check_cancel(message):
        return

    task = message.text.strip()
    msg = bot.send_message(
        message.chat.id,
        "📅 Шаг 3 из 3. Введи дату сдачи в формате ДД.ММ.ГГГГ\n"
        "(например: 25.11.2026):"
    )
    bot.register_next_step_handler(msg, process_date_step, subject, task)

# Обработчик кнопки «📋 Мои дедлайны» (заготовка для будущих недель)
@bot.message_handler(func=lambda message: message.text == "📋 Мои дедлайны")
def list_deadlines(message):
    deadlines = get_user_deadlines(message.from_user.id)

    if not deadlines:
        bot.send_message(
            message.chat.id,
            "📂 В базе данных пока нет активных дедлайнов. Скоро мы научимся их добавлять!"
        )
        return

    response = "📋 Твои учебные дедлайны:\n\n"
    for idx, item in enumerate(deadlines, start=1):
        task_id, subject, task, due_date = item
        response += f"{idx}. 📚 {subject} — {task} (до {due_date})\n"

    bot.send_message(message.chat.id, response)

# Обработчик любого другого текста
@bot.message_handler(content_types=['text'])
def handle_unknown_text(message):
    bot.send_message(
        message.chat.id,
        "Пожалуйста, используй кнопки меню внизу экрана",
        reply_markup=get_main_menu()
    )

if __name__ == '__main__':
    init_db()
    print("База данных SQLite проверена. Бот запущен!")
    bot.infinity_polling()