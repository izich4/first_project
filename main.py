import telebot
from config import BOT_TOKEN

# Подключение бота с помощью токена
bot = telebot.TeleBot(BOT_TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Привет, {user_name}! \n\n"
        "Я бот для контроля учебных дедлайнов.\n"
        "Я помогу тебе не забыть о сдаче лабораторных и курсовых работ.\n\n"
        "Напиши /help, чтобы узнать, что я умею."
    )
    bot.send_message(message.chat.id, welcome_text)

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "Доступные команды:\n"
        "/start — перезапустить бота\n"
        "/help — показать эту справку\n\n"
        "В следующих обновлениях здесь появится меню для добавления задач!"
    )
    bot.send_message(message.chat.id, help_text)

# Обработчик любого другого текста
@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_message(
        message.chat.id,
        "Я пока понимаю только команды /start и /help"
    )

# Запуск бесконечного цикла работы бота
if __name__ == '__main__':
    print("Бот успешно запущен и ждет сообщений...")
    bot.infinity_polling()