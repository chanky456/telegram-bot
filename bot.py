from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Функция приветствия
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user  # Получаем информацию о пользователе
    first_name = user.first_name if user.first_name else "пользователь"
    
    welcome_message = (
        f"👋 Привет, {first_name}!\n\n"
        "🔥 Добро пожаловать в наш бот. Здесь вы сможете зарабатывать деньги, просматривая контент.\n\n"
        "📱 Нажмите кнопку ниже, чтобы начать!"
    )
    
    update.message.reply_text(welcome_message)

# Основная функция
def main():
    updater = Updater("7980145475:AAGP1_CfcLErdmK0aIsPOhTOiCAFCpJiqvU")  # Вставьте свой токен
    dispatcher = updater.dispatcher

    # Добавляем обработчик команды /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Запуск бота
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
