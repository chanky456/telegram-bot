from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Функция приветствия
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user  # Получаем информацию о пользователе
    first_name = user.first_name if user.first_name else "пользователь"
    
    welcome_message = (
        f"👋 Привет, {first_name}!\n\n"
        "🔥 Добро пожаловать в наш бот. Здесь вы сможете зарабатывать деньги, просматривая контент.\n\n"
        "📱 Нажмите кнопку ниже, чтобы начать!"
    )
    
    # Создаем кнопку
    keyboard = [[InlineKeyboardButton("Начать 🔥", callback_data="start_action")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с кнопкой
    update.message.reply_text(welcome_message, reply_markup=reply_markup)

# Обработка нажатия кнопки "Начать 🔥"
def start_action(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()  # Подтверждаем, что запрос получен
    query.edit_message_text("🚀 Отлично! Вы начали работать с ботом. Давайте приступим!")

# Основная функция
def main():
    updater = Updater("ВАШ_ТОКЕН_БОТА")  # Вставьте токен вашего бота
    dispatcher = updater.dispatcher

    # Добавляем обработчики
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(start_action, pattern="^start_action$"))

    # Запуск бота
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
