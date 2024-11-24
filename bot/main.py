import logging
import random
import string
import io
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from config import TELEGRAM_TOKEN_BOT, QR_CODE_URL_DOMAIN
from database import session
from models import User, Booking, Link
import qrcode
from sqlalchemy.exc import SQLAlchemyError

# Setting up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Constants for conversation states
CONTACT, SEATS, PAYMENT = range(3)

# Information about the current event
EVENT = {
    'name': 'Концерт группы XYZ',
    'date': '01.12.2023',
    'available_seats': 100,
    'price_per_seat': 1000,  # Price per seat
}


# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if EVENT:
        message = (
            f"Привет, {user.first_name}! "
            f"Ближайшее мероприятие: {EVENT['name']} {EVENT['date']}."
        )
        await update.message.reply_text(message)
        await request_phone_number(update, context)
        return CONTACT
    else:
        await update.message.reply_text("Сейчас нет запланированных мероприятий.")
        return ConversationHandler.END


# Request for phone number
async def request_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_button = KeyboardButton('Поделиться контактом', request_contact=True)
    reply_markup = ReplyKeyboardMarkup(
        [[contact_button]], one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text(
        'Пожалуйста, поделитесь своим номером телефона для продолжения.',
        reply_markup=reply_markup
    )


# Handle contact sharing
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user_id = contact.user_id
    phone_number = contact.phone_number

    # Convert phone number to format 7xxxxxxxx
    if phone_number.startswith('+'):
        phone_number = phone_number[1:]
    if phone_number.startswith('8'):
        phone_number = '7' + phone_number[1:]

    # Save user to the database
    user = User(user_id=user_id, phone_number=phone_number)
    try:
        session.merge(user)
        session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await update.message.reply_text("Произошла ошибка при сохранении данных. Попробуйте позже.")
        return ConversationHandler.END

    await update.message.reply_text(
        'Спасибо! Сколько мест вы хотите забронировать?',
        reply_markup=ReplyKeyboardRemove()
    )
    return SEATS


# Handle seat selection
async def handle_seats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        seats = int(update.message.text)
        if seats <= 0:
            raise ValueError

        # Check availability
        booked_seats = session.query(Booking).filter_by(event_name=EVENT['name']).count()
        if booked_seats + seats > EVENT['available_seats']:
            await update.message.reply_text(
                f"К сожалению, доступно только {EVENT['available_seats'] - booked_seats} мест(а)."
            )
            return SEATS

        user_id = update.effective_user.id

        # Save booking to the database
        booking = Booking(user_id=user_id, seats=seats, event_name=EVENT['name'])
        session.add(booking)
        session.commit()

        total_price = seats * EVENT['price_per_seat']

        payment_info = (
            f"Для бронирования {seats} мест переведите {total_price} руб. на счет XXXX-YYYY-ZZZZ."
        )
        await update.message.reply_text(payment_info)
        await update.message.reply_text('После оплаты отправьте файл с подтверждением (jpeg/png/pdf).')
        return PAYMENT
    except ValueError:
        await update.message.reply_text('Пожалуйста, введите корректное количество мест (число больше 0).')
        return SEATS
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await update.message.reply_text("Произошла ошибка при сохранении бронирования. Попробуйте позже.")
        return ConversationHandler.END


# Handle payment confirmation
async def handle_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    booking = session.query(Booking).filter_by(user_id=user_id, payment_confirmed=False).first()

    if booking:
        file = None
        if update.message.document:
            file = update.message.document
        elif update.message.photo:
            file = update.message.photo[-1]
        else:
            await update.message.reply_text('Пожалуйста, отправьте файл с подтверждением оплаты (jpeg/png/pdf).')
            return PAYMENT

        # Check file format
        if hasattr(file, 'mime_type') and file.mime_type not in ['image/jpeg', 'image/png', 'application/pdf']:
            await update.message.reply_text('Недопустимый формат файла. Пришлите jpeg, png или pdf.')
            return PAYMENT

        # Save file locally (optional)
        # You can implement file saving here if needed

        # Mark payment as confirmed
        booking.payment_confirmed = True
        try:
            session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await update.message.reply_text("Произошла ошибка при обработке оплаты. Попробуйте позже.")
            return ConversationHandler.END

        # Generate one-time link and QR code
        link_url = await generate_one_time_link(user_id)
        qr_image = generate_qr_code(link_url)

        await update.message.reply_photo(photo=qr_image)
        await update.message.reply_text(
            'Оплата подтверждена! Вот ваш QR-код с одноразовой ссылкой.'
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            'Вы еще не сделали бронирование или оплата уже подтверждена.'
        )
        return ConversationHandler.END


# Generate one-time link
async def generate_one_time_link(user_id):
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    link = Link(user_id=user_id, token=token, expired=False)
    try:
        session.add(link)
        session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
    # Replace 'yourdomain.com' with your actual domain or IP address
    return f"http://{QR_CODE_URL_DOMAIN}/confirm/{token}"


# Generate QR code
def generate_qr_code(link):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    bio = io.BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio


# Handle unexpected input in CONTACT state
async def handle_unexpected_contact_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Пожалуйста, поделитесь своим номером телефона, используя кнопку ниже.')
    await request_phone_number(update, context)
    return CONTACT


# Handle unexpected input in PAYMENT state
async def handle_unexpected_payment_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Пожалуйста, отправьте файл с подтверждением оплаты (jpeg/png/pdf).')
    return PAYMENT


# Command handler for /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Операция отменена.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# Main function
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    application = ApplicationBuilder().token(TELEGRAM_TOKEN_BOT).build()

    # Define ConversationHandler with states CONTACT, SEATS, PAYMENT
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONTACT: [
                MessageHandler(filters.CONTACT, handle_contact),
                MessageHandler(filters.ALL & ~filters.COMMAND, handle_unexpected_contact_input),
            ],
            SEATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_seats)],
            PAYMENT: [
                MessageHandler(
                    (filters.Document.ALL | filters.PHOTO) & ~filters.COMMAND,
                    handle_payment_confirmation
                ),
                MessageHandler(filters.ALL & ~filters.COMMAND, handle_unexpected_payment_input),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add ConversationHandler to the application
    application.add_handler(conv_handler)

    # Run the bot
    application.run_polling()


if __name__ == '__main__':
    main()
