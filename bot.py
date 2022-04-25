import logging
import os

import telegram
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackContext

from config import TELEGRAM_BOT_HTTP_API_TOKEN, FilterersPhotos
from json_database import *

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

default_reply_keyboard = [
    ["/nudes", "/aesthetics"],
    ["/nude_photo", "/aesthetic_photo"]
]
default_markup = ReplyKeyboardMarkup(default_reply_keyboard, resize_keyboard=True)


filter_replies = ["delete", "aesthetics", "nudes", "full_nudes"]
filter_reply_keyboard = [
    filter_replies,
    ["/exit"]
]
filter_markup = ReplyKeyboardMarkup(filter_reply_keyboard, resize_keyboard=True)

FILTERING = 0


def get_random_photo():
    vibe_path = random.choice(os.listdir("photos"))
    public_path = random.choice(os.listdir(f"photos/{vibe_path}"))
    photo_path = random.choice(os.listdir(f"photos/{vibe_path}/{public_path}"))

    return f"photos/{vibe_path}/{public_path}/{photo_path}"


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Hello",
        reply_markup=default_markup,
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("HELP!")


def send_aesthetics_command(update: Update, context: CallbackContext) -> None:
    photo_urls = get_five_photo_by_category(category="aesthetics", file=Files.photos)
    update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
    logger.info(f"SUCCESS: five aesthetics photos were sent to {update.message.from_user.name}")


def send_aesthetic_photo_command(update: Update, context: CallbackContext) -> None:
    photo_url = get_one_photo_url_by_category(category="aesthetics", file=Files.photos)
    update.message.reply_photo(photo_url)
    logger.info(f"SUCCESS: one aesthetic photo was sent to {update.message.from_user.name}")


def send_nudes_command(update: Update, context: CallbackContext) -> None:
    photo_urls = get_five_photo_by_category(category="nudes", file=Files.photos)
    update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
    logger.info(f"SUCCESS: five nudes photos were sent to {update.message.from_user.name}")


def send_nudes_photo_command(update: Update, context: CallbackContext) -> None:
    photo_url = get_one_photo_url_by_category(category="nudes", file=Files.photos)
    update.message.reply_photo(photo_url)
    logger.info(f"SUCCESS: one nude photo was sent to {update.message.from_user.name}")


def get_photos_number_command(update: Update, context: CallbackContext) -> None:
    total_unsorted_photos_number, unsorted_counter = get_number_of_photos(file=Files.unsorted_photos)
    unsorted_formatted_counter = '\n'.join([f'{category}: {number}' for category, number in unsorted_counter.items()])
    total_photos_number, counter = get_number_of_photos(file=Files.photos)
    formatted_counter = '\n'.join([f'{category}: {number}' for category, number in counter.items()])
    output = f"Общее количество всех фотографий: {total_unsorted_photos_number}\n" \
             f"Количество по категориям:\n{unsorted_formatted_counter}\n\n" \
             f"Общее количество сортированных фотографий: {total_photos_number}\n" \
             f"Количество по категориям:\n{formatted_counter}"
    logger.info(output)
    update.message.reply_text(output)
    logger.info(f"unsorted photos number: {total_unsorted_photos_number}, sorted photos number: {total_photos_number}")


def send_photo_filter(update: Update, context: CallbackContext):
    photo_url = get_one_photo_url_by_category("nudes")
    user_id = update.message.from_user.id
    update.message.reply_photo(photo=photo_url)
    set_current_url_filterer(user_id=user_id, photo_url=photo_url)
    logger.info(f"Set current_url = {photo_url}\n to user_id: {user_id}")
    return FILTERING


def start_filter(update: Update, context: CallbackContext) -> int:
    logger.info(f"{update.message.from_user.name} started filtering")
    user_id = update.message.from_user.id
    if new_filterer(user_id):
        text = """Спасибо, что согласились поучаствовать в проекте Boobster.
Ваша задача фильтровать фотографии для создания базы данных по категориям. 
Всего есть 4 типа: абсолютные нюдсы, полу нюдсы, эстетичные фотографии и ссаный шлак. Для каждой фотографии будет необходимо определить тип.
Для фотографии типа абсолютные нюдсы отправьте full_nudes, для нюдсов - nudes, для эстетичных - aesthetics, для мусора - delete.
Ниже можете ознакомиться с примерами типов."""
        update.message.reply_text(text)
        update.message.reply_text(
            "Full nudes - фотографии с частичной или полной оголенностью. Обязательно сиськи, попы, вагины вся хуйня."
        )
        update.message.reply_media_group(
            media=[telegram.InputMediaPhoto(photo_url) for photo_url in FilterersPhotos.full_nudes]
        )
        update.message.reply_text(
            "Nudes - фотографии, которые вроде и нюдсы, но не видно нихуя. Где одежды есть хотя бы"
        )
        update.message.reply_media_group(
            media=[telegram.InputMediaPhoto(photo_url) for photo_url in FilterersPhotos.nudes]
        )
        update.message.reply_text(
            "Aesthetics - фотографии, которые не подходят под первые две категории и не совсем шлак. Всякие милые"
            "девочки, машинки, закаты хуяты, эстетика в общем. Но там блять цитаты всякие, кофты их нахуй в мусор"
        )
        update.message.reply_media_group(
            media=[telegram.InputMediaPhoto(photo_url) for photo_url in FilterersPhotos.aesthetics])
        add_filterer(user_id)

    update.message.reply_text("Удачной сортировки!", reply_markup=filter_markup)
    send_photo_filter(update, context)

    return FILTERING


def filtering_filter(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_reply = update.message.text
    photo_url = get_current_url_filterer(user_id)
    if user_reply != "delete":
        add_photo_url(url=photo_url, categories=[user_reply], file=Files.photos)
        logger.info(f"Added {photo_url.split('/')[-1].split('?')[0]} to {Files.photos}")
    remove_photo_url(photo_url, file=Files.unsorted_photos)
    logger.info(f"Removed {photo_url.split('/')[-1].split('?')[0]} from {Files.unsorted_photos}")
    send_photo_filter(update, context)


def exit_filter(update: Update, context: CallbackContext) -> int:
    logger.info(f"{update.message.from_user.name} finished filtering")
    update.message.reply_text("Спасибо за работу", reply_markup=default_markup)
    return ConversationHandler.END


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

    filter_handler = ConversationHandler(
        entry_points=[CommandHandler("start_filter", start_filter)],
        states={
            FILTERING: [MessageHandler(Filters.regex(f"^({'|'.join(filter_replies)})$"), filtering_filter)]
        },
        fallbacks=[CommandHandler("exit", exit_filter)]
    )

    dispatcher.add_handler(filter_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
