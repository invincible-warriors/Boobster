import logging
import os
import random

import telegram
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from config import TELEGRAM_BOT_HTTP_API_TOKEN
from json_database import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

reply_keyboard = [
    ["/nudes", "/aesthetics"],
    ["/nude_photo", "/aesthetic_photo"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


def get_random_photo():
    vibe_path = random.choice(os.listdir("photos"))
    public_path = random.choice(os.listdir(f"photos/{vibe_path}"))
    photo_path = random.choice(os.listdir(f"photos/{vibe_path}/{public_path}"))

    return f"photos/{vibe_path}/{public_path}/{photo_path}"


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Hello",
        reply_markup=markup,
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("HELP!")


def send_aesthetics_command(update: Update, context: CallbackContext) -> None:
    photo_urls = get_five_photo_by_category(category="aesthetics")
    update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
    logger.info(f"SUCCESS: five aesthetics photos were sent to {update.message.from_user.name}")


def send_aesthetic_photo_command(update: Update, context: CallbackContext) -> None:
    photo_url = get_one_photo_url_by_category(category="aesthetics")
    update.message.reply_photo(photo_url)
    logger.info(f"SUCCESS: one aesthetic photo was sent to {update.message.from_user.name}")


def send_nudes_command(update: Update, context: CallbackContext) -> None:
    photo_urls = get_five_photo_by_category(category="nudes")
    update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
    logger.info(f"SUCCESS: five nudes photos were sent to {update.message.from_user.name}")


def send_nudes_photo_command(update: Update, context: CallbackContext) -> None:
    photo_url = get_one_photo_url_by_category(category="nudes")
    update.message.reply_photo(photo_url)
    logger.info(f"SUCCESS: one nude photo was sent to {update.message.from_user.name}")


def get_photos_number_command(update: Update, context: CallbackContext) -> None:
    total_photos_number, counter = get_number_of_photos()
    formatted_counter = '\n'.join([f'*{category}*: {number}' for category, number in counter.items()])
    update.message.reply_markdown_v2(f"Общее количество фотографий: {total_photos_number}\n\n"
                                     f"Количество по категориям:\n{formatted_counter}")
    logger.info(f"photos_number: {total_photos_number}")


def echo(update: Update, context: CallbackContext) -> None:
    logger.info(f"Text message by {update.message.from_user.name}: {update.message.text}")


def main() -> None:
    updater = Updater(token=TELEGRAM_BOT_HTTP_API_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("aesthetics", send_aesthetics_command))
    dispatcher.add_handler(CommandHandler("nudes", send_nudes_command))
    dispatcher.add_handler(CommandHandler("aesthetic_photo", send_aesthetic_photo_command))
    dispatcher.add_handler(CommandHandler("nude_photo", send_nudes_photo_command))
    dispatcher.add_handler(CommandHandler("number", get_photos_number_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
