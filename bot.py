from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Пользовательские данные (вместо базы данных)
user_data = {}

# Функция приветствия
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_data[user.id] = {"balance": 0, "completed": 0}

    welcome_message = (
        f"👋 Привет, {user.first_name}!\n\n"
        "🔥 Добро пожаловать в наш бот. Здесь вы сможете зарабатывать деньги, просматривая контент.\n\n"
        "📱 Нажмите кнопку ниже, чтобы начать!"
    )

    keyboard = [[InlineKeyboardButton("Начать 🔥", callback_data="start_action")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(welcome_message, reply_markup=reply_markup)

# Обработка кнопки "Начать 🔥"
def start_action(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    send_video(query, context)

# Функция для отправки видео
def send_video(query, context: CallbackContext) -> None:
    user_id = query.from_user.id
    user_info = user_data[user_id]

    # Путь к видео
    video_path = f"/Users/macbook/Desktop/telegram_bot/video{user_info['completed'] + 1}.mp4"
    print(f"Проверяем отправку видео: {video_path}")  # Отладка

    try:
        keyboard = [
            [InlineKeyboardButton("Нравится 👍 (10 руб)", callback_data="like"),
             InlineKeyboardButton("Не нравится 👎 (10 руб)", callback_data="dislike")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем видео
        context.bot.send_video(chat_id=user_id, video=open(video_path, "rb"), caption="Просмотрите видео и выберите реакцию:", reply_markup=reply_markup)
        print(f"Видео {video_path} успешно отправлено")
    except FileNotFoundError:
        print(f"Ошибка: Видео {video_path} не найдено")
        query.edit_message_text("Видео не найдено. Обратитесь к администратору.")
    except Exception as e:
        print(f"Ошибка при отправке видео: {e}")


# Обработка реакции "Нравится" или "Не нравится"
def handle_reaction(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    user_id = query.from_user.id
    user_info = user_data[user_id]

    # Обновление баланса
    user_info["balance"] += 10
    user_info["completed"] += 1

    # Сообщение о балансе
    balance_text = (
        f"Ваш баланс изменен с {user_info['balance'] - 10} до {user_info['balance']} руб\n\n"
        f"✅ Выполнено: {user_info['completed']} из 4\n"
        f"💰 Ваш баланс: {user_info['balance']} руб"
    )
    query.edit_message_text(balance_text)

    # Отправка следующего видео или завершение
    if user_info["completed"] < 4:
        send_video(query, context)
    else:
        query.edit_message_text("Вы выполнили все задания на сегодня. Возвращайтесь завтра!")

# Основная функция
def main():
    updater = Updater("7980145475:AAGP1_CfcLErdmK0aIsPOhTOiCAFCpJiqvU")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(start_action, pattern="^start_action$"))
    dispatcher.add_handler(CallbackQueryHandler(handle_reaction, pattern="^(like|dislike)$"))

    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
