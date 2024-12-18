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
                    "\u2705 Нажмите «Готово», чтобы начать зарабатывать деньги.")

    keyboard = [[InlineKeyboardButton("Начать", callback_data="ready")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Функция для обработки кнопки "Готово"
def ready(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    ready_text = ("\u2705 Отлично! Вы готовы к работе с платформой.\n\n"
                  "\u2757 Вы можете прекратить просмотр видео в любой момент. Заработанные средства будут автоматически зачислены на ваш баланс.\n\n"
                  "\u2757 Не пытайтесь нажать кнопку «Просмотр» несколько раз подряд. Вы сможете нажать её только после того, как ваш просмотр будет учтен.")

    query.edit_message_text(ready_text)
    send_video(query, context)

# Функция для отправки видео
def send_video(query, context: CallbackContext) -> None:
    user_id = query.from_user.id
    user_info = user_data[user_id]

    # Проверка на бонус
    if user_info["completed"] == 4 and not user_info["bonus_given"]:
        send_bonus_message(query, context)
        return

    # Замена на путь к вашему видео
    video_path = f"video{user_info['completed'] + 1}.mp4"

    try:
        keyboard = [
            [InlineKeyboardButton("Мне понравилось (10 руб)", callback_data="like"),
             InlineKeyboardButton("Не понравилось (10 руб)", callback_data="dislike")],
            [InlineKeyboardButton("Закончить просмотр", callback_data="finish")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_video(chat_id=user_id, video=open(video_path, "rb"), caption="Просмотрите видео и выберите реакцию.", reply_markup=reply_markup)
    except FileNotFoundError:
        query.edit_message_text("Видео не найдено. Обратитесь к администратору.")

# Функция для отправки бонусного сообщения
def send_bonus_message(query, context: CallbackContext) -> None:
    user_id = query.from_user.id
    user_data[user_id]["bonus_given"] = True

    bonus_text = ("\U0001F381 Бонус: вы получили счастливый бонус от спонсора!\n\n"
                  "- 1000 рублей\n\n"
                  "Чтобы забрать бонус, нажмите кнопку '\U0001F381 забрать 1000 рублей.'\n\u2193")

    keyboard = [[InlineKeyboardButton("Получить 1000 рублей", callback_data="claim_bonus")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(bonus_text, reply_markup=reply_markup)

# Обработка бонусной кнопки
def claim_bonus(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    bonus_claim_text = ("Хорошая работа! Чтобы получить 1000 рублей:\n\n"
                        "- Подпишитесь на канал: здесь будет ссылка на наш канал\n"
                        "- Лайкните 5 последних постов \u2764\n"
                        "- Свяжитесь с владельцем канала и получите свой бонус 1000 рублей \U0001F381\n")

    keyboard = [[InlineKeyboardButton("Подписаться на канал", url="https://t.me/+aWcjTRzCSoU1Mzhi")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(bonus_claim_text, reply_markup=reply_markup)

# Обработка кнопок под видео
def handle_reaction(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    if user_id not in user_data:
        user_data[user_id] = {"balance": 0, "completed": 0, "bonus_given": False}

    user_info = user_data[user_id]

    # Обновление баланса и выполненных заданий
    if query.data in ["like", "dislike"]:
        user_info["balance"] += 10
        user_info["completed"] += 1

        balance_text = (f"Ваш баланс изменен с {user_info['balance'] - 10} до {user_info['balance']} руб\n\n"
                        f"📱 Ставка за просмотр: 10 руб\n\n"
                        f"✅ Выполнено: {user_info['completed']} из 20\n"
                        f"💰 Ваш баланс: {user_info['balance']} руб")

        query.edit_message_text(balance_text)

        if user_info["completed"] < 20:
            send_video(query, context)
        else:
            query.edit_message_text("Вы выполнили все задания на сегодня. Возвращайтесь завтра!")

    elif query.data == "finish":
        query.edit_message_text("Вы закончили просмотр видео. Спасибо за участие!")

# Основная функция
def main():
    updater = Updater("7980145475:AAGP1_CfcLErdmK0aIsPOhTOiCAFCpJiqvU")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(ready, pattern="^ready$"))
    dispatcher.add_handler(CallbackQueryHandler(handle_reaction, pattern="^(like|dislike|finish)$"))
    dispatcher.add_handler(CallbackQueryHandler(claim_bonus, pattern="^claim_bonus$"))

    updater.start_polling(timeout=5)
    updater.idle()

if __name__ == "__main__":
    main()
