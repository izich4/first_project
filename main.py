import telebot
from telebot import types
from config import BOT_TOKEN

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

# Обработчик кнопки «➕ Добавить дедлайн» (заготовка для будущих недель)
@bot.message_handler(func=lambda message: message.text == "➕ Добавить дедлайн")
def add_deadline(message):
    bot.send_message(
        message.chat.id,
        "🛠 Функция добавления задач в базу данных SQLite скоро появится!"
    )

# Обработчик кнопки «📋 Мои дедлайны» (заготовка для будущих недель)
@bot.message_handler(func=lambda message: message.text == "📋 Мои дедлайны")
def list_deadline_stub(message):
    bot.send_message(
        message.chat.id,
        "📂 Твой список дедлайнов пока пуст. На следующей неделе мы подключим базу данных!"
    )

# Обработчик любого другого текста
@bot.message_handler(content_types=['text'])
def handle_unknown_text(message):
    bot.send_message(
        message.chat.id,
        "Пожалуйста, используй кнопки меню внизу экрана",
        reply_markup=get_main_menu()
    )

if __name__ == '__main__':
    print("Бот запущен! Тестируем кнопочное меню...")
    bot.infinity_polling()