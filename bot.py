import logging
import os
import telegram
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from database.database import (
    Photos,
    Users,
    URLAlreadyExistsError,
    URLBlocked,
    URLNotFoundError,
    CategoryNotFoundError,
    CollectionNotFoundError,
    IsNotSorterError,
    SorterAlreadyExistsError,
    IsNotClientError,
    ClientAlreadyExistsError
)
import config
from config import Colors as C

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

default_reply_keyboard = [
    ["/nudes", "/aesthetics"],
    ["/nude_photo", "/aesthetic_photo"],
]
default_markup = ReplyKeyboardMarkup(default_reply_keyboard, resize_keyboard=True)

sorting_replies = ["delete", "aesthetics", "nudes", "full_nudes"]
sorting_reply_keyboard = [sorting_replies, ["/exit"]]
sorting_markup = ReplyKeyboardMarkup(sorting_reply_keyboard, resize_keyboard=True)

SORTING = 0

photos = Photos()
users = Users()


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello", reply_markup=default_markup)


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("HELP!")


def send_aesthetics_command(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if not users.is_client(user.id):
        users.add_client(user)
    users.add_number_to_category_client(user, category="aesthetics", number=5)
    photo_urls = photos.get_five_photo_by_category(category="aesthetics")
    update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
    logger.info(f"{C.green}SUCCESS{C.white}: five aesthetics photos were sent to {C.blue}"
                f"{user.first_name}(id:{user.id}){C.white}")


def send_aesthetic_photo_command(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if not users.is_client(user.id):
        users.add_client(user)
    users.add_number_to_category_client(user, category="aesthetics", number=1)
    photo_url = photos.get_one_photo_url_by_category(category="aesthetics")
    update.message.reply_photo(photo_url)
    logger.info(f"{C.green}SUCCESS{C.white}: one aesthetic photo was sent to {C.blue}"
                f"{user.first_name}(id:{user.id}){C.white}")


def send_nudes_command(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if not users.is_client(user.id):
        users.add_client(user)
    users.add_number_to_category_client(user, category="nudes", number=5)
    photo_urls = photos.get_five_photo_by_category(category="nudes")
    update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
    logger.info(f"{C.green}SUCCESS{C.white}: five nudes photos were sent to {C.blue}"
                f"{user.first_name}(id:{user.id}){C.white}")


def send_nudes_photo_command(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if not users.is_client(user.id):
        users.add_client(user)
    users.add_number_to_category_client(user, category="nudes", number=1)
    photo_url = photos.get_one_photo_url_by_category(category="nudes")
    update.message.reply_photo(photo_url)
    logger.info(f"{C.green}SUCCESS{C.white}: one nude photo was sent to {C.blue}"
                f"{user.first_name}(id:{user.id}){C.white}")


def get_photo_stats_command(update: Update, context: CallbackContext) -> None:
    counters = photos.get_stats_of_photos()
    allowed_photos_formatted = "\n".join(
        f"{category}: {number}" for category, number in counters[config.Collections.allowed].items()
    )
    update.message.reply_text(
        f"Статистика по фотографиям:\n"
        f"{config.Collections.allowed}:\n{allowed_photos_formatted}\n\n"
        f"{config.Collections.unsorted}: {counters[config.Collections.unsorted]}\n"
        f"{config.Collections.blocked}: {counters[config.Collections.blocked]}"
    )
    logger.info(f"Statistics of photos (asked by {C.blue}{update.message.from_user.first_name} "
                f"(id: {update.message.from_user.id}){C.white}): {counters}")


def send_photo_sorting(update: Update, context: CallbackContext):
    photo_url = photos.get_photo_for_sorting()
    user = update.message.from_user
    while True:
        try:
            update.message.reply_photo(photo=photo_url)
            break
        except telegram.error.BadRequest:
            logger.error(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: "
                         f"{C.red}BadRequest{C.white}. Deleted and blocked photo")
            photos.delete_from_unsorted_photo_url(photo_url)
            try:
                photos.add_to_blocked_photo_url(photo_url)
            except URLAlreadyExistsError:
                pass
    users.set_current_url_sorter(user, photo_url)
    logger.info(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: Set photo_url for sorter ")
    return SORTING


def start_sorting(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f"{C.blue}{update.message.from_user.first_name} (id:{user.id}){C.white}: started sorting")
    if not users.is_sorter(user.id):
        text = """Спасибо, что согласились поучаствовать в проекте Boobster. Ваша задача сортировать фотографии для 
создания базы данных по категориям. Всего есть 4 типа: абсолютные нюдсы, полу нюдсы, эстетичные фотографии и 
ссаный шлак. Для каждой фотографии будет необходимо определить тип. Для фотографии типа абсолютные нюдсы 
отправьте full_nudes, для нюдсов - nudes, для эстетичных - aesthetics, для мусора - delete. Ниже можете 
ознакомиться с примерами типов. """
        update.message.reply_text(text)
        update.message.reply_text(
            "Full nudes - фотографии с частичной или полной оголенностью. Обязательно сиськи, попы, вагины вся хуйня."
        )
        update.message.reply_media_group(
            media=[
                telegram.InputMediaPhoto(photo_url)
                for photo_url in config.FilterersPhotos.full_nudes
            ]
        )
        update.message.reply_text(
            "Nudes - фотографии, которые вроде и нюдсы, но не видно нихуя. Где одежды есть хотя бы"
        )
        update.message.reply_media_group(
            media=[
                telegram.InputMediaPhoto(photo_url)
                for photo_url in config.FilterersPhotos.nudes
            ]
        )
        update.message.reply_text(
            "Aesthetics - фотографии, которые не подходят под первые две категории и не совсем шлак. Всякие милые"
            "девочки, машинки, закаты хуяты, эстетика в общем. Но там блять цитаты всякие, кофты их нахуй в мусор"
        )
        update.message.reply_media_group(
            media=[
                telegram.InputMediaPhoto(photo_url)
                for photo_url in config.FilterersPhotos.aesthetics
            ]
        )
        users.add_sorter(user)

    update.message.reply_text("Удачной сортировки!", reply_markup=sorting_markup)
    send_photo_sorting(update, context)

    return SORTING


def filtering_filter(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_reply = update.message.text
    photo_url = users.get_current_url_sorter(user)
    if user_reply != "delete":
        photos.add_to_allowed_photo_url(url=photo_url, categories=[user_reply])
        logger.info(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: "
                    f"{C.green}added{C.white} photo to the AllowedPhotosURLs")
    photos.delete_from_unsorted_photo_url(url=photo_url)
    logger.info(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: "
                f"{C.red}removed{C.white} photo from the UnsortedPhotosURLs")
    users.add_one_to_category_sorter(user, category=user_reply)
    send_photo_sorting(update, context)


def exit_sorting(update: Update, context: CallbackContext) -> int:
    logger.info(f"{C.blue}{update.message.from_user.first_name} (id:{update.message.from_user.id}){C.white}: "
                f"finished filtering")
    update.message.reply_text("Спасибо за работу", reply_markup=default_markup)
    return ConversationHandler.END


def get_sorter_stats_command(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if not users.is_sorter(user.id):
        update.message.reply_text(f"Вы не идентифицированы как сортировщик.")
        return
    counter = users.get_stats_of_sorter(user)
    formatted_output = "\n".join(f"{category}: {number}" for category, number in counter.items())
    logger.info(f"Statistics of sorter {C.blue}{user.first_name} (id: {user.id}){C.white}: {counter}")
    update.message.reply_text(f"Ваша статистика (как сортировщика):\n{formatted_output}")


def get_client_stats_command(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if not users.is_client(user.id):
        update.message.reply_text(f"Вы не идентифицированы как клиент.")
        return
    counter = users.get_stats_of_client(user)
    formatted_output = "\n".join(f"{category}: {number}" for category, number in counter.items())
    logger.info(f"Statistics of client {C.blue}{user.first_name} (id: {user.id}){C.white}: {counter}")
    update.message.reply_text(f"Ваша статистика (как клиента):\n{formatted_output}")


def main() -> None:
    updater = Updater(token=config.TELEGRAM_BOT_HTTP_API_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(CommandHandler("aesthetics", send_aesthetics_command))
    dispatcher.add_handler(CommandHandler("nudes", send_nudes_command))
    dispatcher.add_handler(CommandHandler("aesthetic_photo", send_aesthetic_photo_command))
    dispatcher.add_handler(CommandHandler("nude_photo", send_nudes_photo_command))

    dispatcher.add_handler(CommandHandler("photo_stats", get_photo_stats_command))
    dispatcher.add_handler(CommandHandler("sorter_stats", get_sorter_stats_command))
    dispatcher.add_handler(CommandHandler("client_stats", get_client_stats_command))

    filter_handler = ConversationHandler(
        entry_points=[CommandHandler("start_sorting", start_sorting)],
        states={
            SORTING: [
                MessageHandler(
                    Filters.regex(f"^({'|'.join(sorting_replies)})$"), filtering_filter
                )
            ]
        },
        fallbacks=[CommandHandler("exit", exit_sorting)],
    )

    dispatcher.add_handler(filter_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
