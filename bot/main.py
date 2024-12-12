import os
import requests
import qrcode
from io import BytesIO
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputFile,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
import logging

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Backend URL для взаимодействия с API
BOT_BACKEND_URL = os.getenv("BOT_BACKEND_URL", "http://localhost:8500")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BOT_USERNAME = os.getenv("BOT_USERNAME", "bot_user")
BOT_PASSWORD = os.getenv("BOT_PASSWORD", "bot_password")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HEADERS = {'accept': 'application/json'}

# Глобальная переменная для хранения токена
AUTH_TOKEN = None

# Состояния для ConversationHandler
SELECT_EVENT, GET_SEATS, GET_PHONE, GET_PAYMENT_FILE = range(4)


def get_auth_token():
    """
    Получение токена авторизации.
    """
    global AUTH_TOKEN
    try:
        response = requests.post(
            f"{BOT_BACKEND_URL}/token",
            data={"username": BOT_USERNAME, "password": BOT_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        AUTH_TOKEN = response.json()["access_token"]
        logging.info("Токен авторизации успешно получен")
    except requests.RequestException as e:
        logging.error(f"Ошибка при получении токена авторизации: {e}")
        AUTH_TOKEN = None


def make_request(method, endpoint, **kwargs):
    """
    Выполнение запроса к бэкенду с авторизацией.
    """
    global AUTH_TOKEN
    if not AUTH_TOKEN:
        get_auth_token()

    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {AUTH_TOKEN}"

    try:
        response = requests.request(method, f"{BOT_BACKEND_URL}{endpoint}", headers=headers, **kwargs)
        if response.status_code == 401:  # Если токен недействителен
            logging.info("Токен недействителен. Обновление токена...")
            get_auth_token()
            headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
            response = requests.request(method, f"{BOT_BACKEND_URL}{endpoint}", headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Ошибка при выполнении запроса: {e}")
        return None


async def start(update: Update, context):
    """
    Обработчик команды /start.
    """
    events = make_request("GET", "/events")
    if not events:
        await update.message.reply_text("На данный момент нет доступных мероприятий.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton(event["name"], callback_data=event["guid"])]
        for event in events
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите мероприятие:", reply_markup=reply_markup)
    return SELECT_EVENT


async def select_event(update: Update, context):
    """
    Обработчик выбора мероприятия.
    """
    query = update.callback_query
    await query.answer()

    event_guid = query.data
    context.user_data["event_guid"] = event_guid

    event_data = make_request("GET", f"/events/{event_guid}")
    if not event_data:
        await query.edit_message_text("Произошла ошибка при получении информации о мероприятии.")
        return ConversationHandler.END

    context.user_data["event_price"] = event_data["price"]
    await query.edit_message_text(f"Вы выбрали: {event_data['name']}\n\n{event_data['text']}")
    await update.effective_message.reply_text("Введите количество мест:")
    return GET_SEATS


async def get_seats(update: Update, context):
    """
    Обработчик указания количества мест.
    """
    try:
        seats = int(update.message.text)
        if seats <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Введите корректное количество мест (число больше 0):")
        return GET_SEATS

    context.user_data["seats"] = seats
    context.user_data["total_cash"] = seats * context.user_data["event_price"]

    contact_button = KeyboardButton("Поделиться контактом", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Пожалуйста, отправьте ваш номер телефона:", reply_markup=reply_markup)
    return GET_PHONE


async def get_phone(update: Update, context):
    """
    Обработчик получения номера телефона.
    """
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text

    context.user_data["phone"] = phone
    user_nickname = update.effective_user.username
    context.user_data["user_nickname"] = user_nickname

    await update.message.reply_text(
        f"Отправьте файл (PDF, JPEG или PNG) с подтверждением перевода на сумму {context.user_data['total_cash']}."
    )
    return GET_PAYMENT_FILE


async def get_payment_file(update, context):
    """Обработчик получения файла подтверждения оплаты с авторизацией."""
    file = None

    # Получение документа или фотографии
    if update.message.document:
        file = update.message.document
    elif update.message.photo:
        file = update.message.photo[-1]  # Берём последнее изображение (высокое разрешение)

    if not file:
        await update.message.reply_text("Отправьте файл в формате PDF, JPEG или PNG.")
        return GET_PAYMENT_FILE

    # Проверка доступности мест
    event_guid = context.user_data["event_guid"]
    seats_requested = context.user_data["seats"]

    # Запрашиваем существующие бронирования для мероприятия
    bookings = make_request("GET", f"/bookings/", params={"event_guid": event_guid})

    # Проверяем, что запрос выполнен успешно
    if bookings is None:
        await update.message.reply_text("Произошла ошибка при проверке доступности мест.")
        return ConversationHandler.END

    # Если бронирования отсутствуют, считаем, что занятых мест нет
    total_booked = sum(booking["count_seats"] for booking in bookings) if bookings else 0

    # Запрашиваем данные о мероприятии
    event_data = make_request("GET", f"/events/{event_guid}")
    if not event_data:
        await update.message.reply_text("Произошла ошибка при получении информации о мероприятии.")
        return ConversationHandler.END

    max_seats = event_data["max_seats"]

    if total_booked + seats_requested > max_seats:
        await update.message.reply_text(
            f"Недостаточно свободных мест. Доступно: {max_seats - total_booked} мест."
        )
        return ConversationHandler.END

    # Шаг 1: Создание бронирования
    payload = {
        "event_guid": event_guid,
        "user_phone": context.user_data["phone"],
        "user_nickname": context.user_data.get("user_nickname"),
        "count_seats": seats_requested,
        "total_cash": context.user_data["total_cash"],
    }
    booking_data = make_request("POST", "/bookings", json=payload)

    if not booking_data:
        await update.message.reply_text(
            "Произошла ошибка при создании бронирования. Попробуйте ещё раз."
        )
        return ConversationHandler.END

    booking_guid = booking_data["guid"]
    context.user_data["booking_guid"] = booking_guid

    # Шаг 2: Загрузка файла оплаты
    file_id = file.file_id
    new_file = await context.bot.get_file(file_id)  # Используем context.bot
    file_data = requests.get(new_file.file_path).content

    files = {"file": (file.file_name if hasattr(file, "file_name") else "payment_confirmation.jpg", file_data)}
    upload_response = make_request(
        "POST",
        f"/bookings/{booking_guid}/upload-payment-file",
        files=files,
    )

    if not upload_response:
        await update.message.reply_text(
            "Произошла ошибка при загрузке файла. Попробуйте ещё раз."
        )
        return ConversationHandler.END

    # Шаг 3: Генерация QR-кода с фронтенд-ссылкой
    frontend_booking_url = f"{FRONTEND_URL}/booking/{booking_guid}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(frontend_booking_url)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    bio = BytesIO()
    bio.name = "qr_code.png"
    img.save(bio, "PNG")
    bio.seek(0)

    # Отправка QR-кода пользователю
    await update.message.reply_photo(photo=InputFile(bio), caption="Ваше бронирование успешно создано!")
    return ConversationHandler.END


async def cancel(update: Update, context):
    """
    Обработчик отмены процесса.
    """
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


def main():
    """
    Запуск Telegram-бота.
    """
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_EVENT: [CallbackQueryHandler(select_event)],
            GET_SEATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_seats)],
            GET_PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
            GET_PAYMENT_FILE: [
                MessageHandler(filters.Document.ALL | filters.PHOTO, get_payment_file)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
