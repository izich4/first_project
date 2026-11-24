import telebot
from datetime import datetime, date
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

# Преобразование строки ДД.ММ.ГГГГ в объект даты (или None при ошибке)
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return None

# Расчет оставшихся дней и выбор индикатора срочности
def get_deadline_status(due_date_str):
    due_date = parse_date(due_date_str)
    if due_date is None:
        return "⚪ Неизвестный формат даты"

    days_left = (due_date - date.today()).days

    if days_left < 0:
        return f"⚫ Просрочено на {abs(days_left)} дн."
    elif days_left == 0:
        return "🔴 Сдать СЕГОДНЯ!"
    elif days_left <= 2:
        return f"🔴 Осталось {days_left} дн."
    elif days_left <= 7:
        return f"🟡 Осталось {days_left} дн."
    else:
        return f"🟢 Осталось {days_left} дн."

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

# Финал диалога: проверка даты и сохранение дедлайна в SQLite
def process_date_step(message, subject, task):
    if not message.text:
        msg = bot.send_message(
            message.chat.id,
            "⚠️ Пожалуйста, отправь дату текстом в формате ДД.ММ.ГГГГ (или /cancel для отмены):"
        )
        bot.register_next_step_handler(msg, process_date_step, subject, task)
        return

    if check_cancel(message):
        return

    due_date = message.text.strip()
    if parse_date(due_date) is None:
        msg = bot.send_message(
            message.chat.id,
            "⚠️ Неверный формат даты! Введи дату строго в виде ДД.ММ.ГГГГ (например: 05.12.2026):"
        )
        bot.register_next_step_handler(msg, process_date_step, subject, task)
        return

    add_deadline(message.from_user.id, subject, task, due_date)

    success_text = (
        "✅ Дедлайн успешно сохранен в базу данных!\n\n"
        f"📚 Предмет: {subject}\n"
        f"📝 Задача: {task}\n"
        f"📅 Сдать до: {due_date}"
    )
    bot.send_message(message.chat.id, success_text, reply_markup=get_main_menu())

# Сортировка и формирование текста списка дедлайнов
def format_deadlines_list(user_id):
    deadlines = get_user_deadlines(user_id)
    if not deadlines:
        return None

    sorted_deadlines = sorted(
        deadlines,
        key=lambda item: parse_date(item[3]) or date.max
    )

    response = "📋 Твои учебные дедлайны:\n\n"
    for idx, item in enumerate(sorted_deadlines, start=1):
        task_id, subject, task, due_date = item
        status = get_deadline_status(due_date)
        response += f"{idx}. 📚 {subject} — {task}\n   📅 До {due_date} ({status})\n\n"

    return response


# Вывод всех задач пользователя из SQLite
@bot.message_handler(func=lambda message: message.text == "📋 Мои дедлайны")
def list_deadlines(message):
    text = format_deadlines_list(message.from_user.id)
    if not text:
        bot.send_message(
            message.chat.id,
            "📂 Список дедлайнов пуст. Нажми «➕ Добавить дедлайн», чтобы создать первую запись!"
        )
        return

    bot.send_message(message.chat.id, text)

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