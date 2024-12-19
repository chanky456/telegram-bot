import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Пользовательские данные (вместо базы данных)
user_data = {}

# Функция приветствия
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_data[user.id] = {"balance": 0, "completed": 0}

    welcome_message = (
        f"👋 Привет, {user.first_name}!\n"
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

    video_path = f"video{user_info['completed'] + 1}.mp4"
    print(f"Проверяем путь к видео: {video_path}")  # Отладка

    if not os.path.exists(video_path):
        print(f"Ошибка: Видео {video_path} не найдено")
        query.edit_message_text("Видео не найдено. Обратитесь к администратору.")
        return

    try:
        with open(video_path, "rb") as video_file:
            keyboard = [
                [InlineKeyboardButton("Нравится 👍 (10 руб)", callback_data="like"),
                 InlineKeyboardButton("Не нравится 👎 (10 руб)", callback_data="dislike")],
                [InlineKeyboardButton("Закончить просмотр", callback_data="finish")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            context.bot.send_video(chat_id=user_id, video=video_file, caption="Просмотрите видео и выберите реакцию:", reply_markup=reply_markup)
            print(f"Видео {video_path} успешно отправлено")
    except Exception as e:
        print(f"Ошибка при отправке видео: {e}")

# Обработка реакции "Нравится" или "Не нравится"
def handle_reaction(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        print(f"Получен callback_data: {query.data}")  # Лог для отладки
        query.answer()

        user_id = query.from_user.id
        user_info = user_data.get(user_id, {"balance": 0, "completed": 0})

        if query.data in ["like", "dislike"]:
            user_info["balance"] += 10
            user_info["completed"] += 1
            user_data[user_id] = user_info  # Сохраняем обновленные данные

            # Формируем текст для обновления
            balance_text = (f"Ваш баланс изменен с {user_info['balance'] - 10} до {user_info['balance']} руб\n\n"
                            f"✅ Выполнено: {user_info['completed']} из 4\n"
                            f"💰 Ваш баланс: {user_info['balance']} руб")
            
            # Отправляем новое сообщение вместо редактирования
            query.message.reply_text(balance_text)

            # Проверяем, нужно ли отправить следующее видео
            if user_info["completed"] < 4:
                send_video(query, context)
            else:
                query.message.reply_text("Вы выполнили все задания на сегодня. Возвращайтесь завтра!")
        elif query.data == "finish":
            query.message.reply_text("Вы закончили просмотр видео. Спасибо за участие!")
    except Exception as e:
        print(f"Ошибка в handle_reaction: {e}")

# Основная функция
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

def main():
    # Получение токена из переменной окружения
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    updater = Updater(token)

    # Установка диспетчера команд
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(start_action, pattern="^start_action$"))
    dispatcher.add_handler(CallbackQueryHandler(handle_reaction, pattern="^(like|dislike|finish)$"))

    # Настройка порта и вебхуков
    port = int(os.environ.get('PORT', 8443))  # Порт по умолчанию 8443
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"

    updater.start_webhook(
        listen="0.0.0.0",  # Слушает все входящие подключения
        port=port,
        url_path="webhook"  # Вебхук будет доступен по пути /webhook
    )
    updater.bot.set_webhook(webhook_url)

    print(f"Бот запущен и использует вебхуки: {webhook_url}")
    updater.idle()

