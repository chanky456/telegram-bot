from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Пользовательские данные (вместо базы данных)
user_data = {}

# Функция для команды /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_data[user.id] = {"balance": 0, "completed": 0, "bonus_given": False}

    welcome_text = (f"\U0001F44B {user.first_name}\n\n"
                    "\U0001F525 Мы соединяем авторов контента TikTok и наших пользователей. "
                    "За просмотр видео вы будете получать деньги.\n\n"
                    "\U0001F440 Мы платим 10 рублей за каждый просмотр.\n\n"
                    "✅ Нажмите «Готово», чтобы начать зарабатывать деньги.")

    keyboard = [
        [InlineKeyboardButton("Готово", callback_data="ready")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Функция для обработки кнопки "Готово"
def ready(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    ready_text = ("✅ Отлично! Вы готовы к работе с платформой.\n\n"
                  "❗ Вы можете прекратить просмотр видео в любой момент. Заработанные средства будут автоматически зачислены на ваш баланс.\n\n"
                  "❗ Не пытайтесь нажать кнопку «Просмотр» несколько раз подряд. Вы сможете нажать её только после того, как ваш просмотр будет учтен.")

    query.edit_message_text(ready_text)
    send_video(query, context)

# Функция для отправки видео
def send_video(query, context: CallbackContext) -> None:
    user_id = query.from_user.id
    user_info = user_data[user_id]

    video_path = f"video{user_info['completed'] + 1}.mp4"
    print(f"Отправляем видео: {video_path}")

    try:
        keyboard = [
            [InlineKeyboardButton("Мне понравилось (10 руб)", callback_data="like"),
             InlineKeyboardButton("Не понравилось (10 руб)", callback_data="dislike")],
            [InlineKeyboardButton("Закончить просмотр", callback_data="finish")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_video(chat_id=user_id, video=open(video_path, "rb"), caption="Просмотрите видео и выберите реакцию.", reply_markup=reply_markup)
        print(f"Видео {video_path} успешно отправлено")
    except FileNotFoundError:
        print(f"Ошибка: Видео {video_path} не найдено")
        query.edit_message_text("Видео не найдено. Обратитесь к администратору.")
    except Exception as e:
        print(f"Ошибка при отправке видео: {e}")

# Функция для обработки реакции
def handle_reaction(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        print(f"Получен callback_data: {query.data}")
        query.answer()

        user_id = query.from_user.id
        if user_id not in user_data:
            user_data[user_id] = {"balance": 0, "completed": 0, "bonus_given": False}

        user_info = user_data[user_id]

        if query.data in ["like", "dislike"]:
            user_info["balance"] += 10
            user_info["completed"] += 1

            balance_text = (f"Ваш баланс изменен с {user_info['balance'] - 10} до {user_info['balance']} руб\n\n"
                            f"📱 Ставка за просмотр: 10 руб\n\n"
                            f"✅ Выполнено: {user_info['completed']} из 4\n"
                            f"💰 Ваш баланс: {user_info['balance']} руб")

            query.edit_message_text(balance_text)

            if user_info["completed"] < 4:
                send_video(query, context)
            else:
                query.edit_message_text("Вы выполнили все задания на сегодня. Возвращайтесь завтра!")

        elif query.data == "finish":
            query.edit_message_text("Вы закончили просмотр видео. Спасибо за участие!")
    except Exception as e:
        print(f"Ошибка в handle_reaction: {e}")

# Основная функция
def main():
    updater = Updater("7980145475:AAGP1_CfcLErdmK0aIsPOhTOiCAFCpJiqvU")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(ready, pattern="^ready$"))
    dispatcher.add_handler(CallbackQueryHandler(handle_reaction, pattern="^(like|dislike|finish)$"))

    print("Бот запущен и готов к работе")
    updater.start_polling(timeout=5)
    updater.idle()

if __name__ == "__main__":
    main()
