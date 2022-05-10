import logging
import telegram
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    LabeledPrice,
    ShippingOption
)
from telegram.ext import (
    ApplicationBuilder,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ShippingQueryHandler,
    PreCheckoutQueryHandler,
    CallbackContext,
    filters
)

import config
from config import Colors as C
from database.database import (
    Photos,
    Users,
    URLAlreadyExistsError
)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

default_reply_keyboard = [
    ["/nudes", "/aesthetics"],
    ["/nude_photo", "/aesthetic_photo"],
]
default_markup = ReplyKeyboardMarkup(default_reply_keyboard, resize_keyboard=True)

admin_default_reply_keyboard = default_reply_keyboard + [
    ["/client_stats", "/sorter_stats"],
    ["/clients_stats", "/sorters_stats"],
    ["/start_sorting"]
]
admin_default_markup = ReplyKeyboardMarkup(admin_default_reply_keyboard, resize_keyboard=True)

sorting_replies = ["delete", "aesthetics", "nudes", "full_nudes"]
sorting_reply_keyboard = [sorting_replies, ["/exit"]]
sorting_markup = ReplyKeyboardMarkup(sorting_reply_keyboard, resize_keyboard=True)

SORTING = 0

photos = Photos()
users = Users()


async def start(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello",
        reply_markup=default_markup if update.message.from_user.id != 516229295 else admin_default_markup
    )


async def send_aesthetics_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    users.add_number_to_category_client(user, category="aesthetics", number=5)
    photo_urls = photos.get_five_photo_by_category(category="aesthetics")
    await update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
    logger.info(f"{C.green}SUCCESS{C.white}: five aesthetics photos were sent to {C.blue}"
                f"{user.first_name} (id:{user.id}){C.white}")


async def send_aesthetic_photo_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    users.add_number_to_category_client(user, category="aesthetics", number=1)
    photo_url = photos.get_one_photo_url_by_category(category="aesthetics")
    await update.message.reply_photo(photo_url)
    logger.info(f"{C.green}SUCCESS{C.white}: one aesthetic photo was sent to {C.blue}"
                f"{user.first_name} (id:{user.id}){C.white}")


async def send_nudes_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    users.add_number_to_category_client(user, category="nudes", number=5)
    photo_urls = photos.get_five_photo_by_category(category="nudes")
    await update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
    logger.info(f"{C.green}SUCCESS{C.white}: five nudes photos were sent to {C.blue}"
                f"{user.first_name} (id:{user.id}){C.white}")


async def send_nudes_photo_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    users.add_number_to_category_client(user, category="nudes", number=1)
    photo_url = photos.get_one_photo_url_by_category(category="nudes")
    await update.message.reply_photo(photo_url)
    logger.info(f"{C.green}SUCCESS{C.white}: one nude photo was sent to {C.blue}"
                f"{user.first_name} (id:{user.id}){C.white}")


async def get_photo_stats_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    counters = photos.get_stats_of_photos()
    allowed_photos_formatted = "\n".join(
        f"{category}: {number}" for category, number in counters[config.Collections.allowed].items()
    )
    await update.message.reply_text(
        f"Статистика по фотографиям:\n"
        f"{config.Collections.allowed}:\n{allowed_photos_formatted}\n\n"
        f"{config.Collections.unsorted}: {counters[config.Collections.unsorted]}\n"
        f"{config.Collections.blocked}: {counters[config.Collections.blocked]}"
    )
    logger.info(f"Statistics of photos (asked by {C.blue}{update.message.from_user.first_name} "
                f"(id: {update.message.from_user.id}){C.white}): {counters}")


async def send_photo_sorting(update: Update, context: CallbackContext.DEFAULT_TYPE):
    photo_url = photos.get_photo_for_sorting()
    user = update.message.from_user
    while True:
        try:
            await update.message.reply_photo(photo=photo_url)
            break
        except telegram.error.BadRequest:
            logger.error(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: "
                         f"{C.red}BadRequest{C.white}. Deleted and blocked photo")
            photos.delete_from_unsorted_photo_url(photo_url)
            try:
                photos.add_to_blocked_photo_url(photo_url, user="bot")
            except URLAlreadyExistsError:
                pass
    users.set_current_url_sorter(user, photo_url)
    logger.info(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: Set photo_url for sorter ")
    return SORTING


async def start_sorting(update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    if not users.is_sorter(user.id):
        text = """Спасибо, что согласились поучаствовать в проекте Boobster. Ваша задача сортировать фотографии для 
создания базы данных по категориям. Всего есть 4 типа: абсолютные нюдсы, полу нюдсы, эстетичные фотографии и 
ссаный шлак. Для каждой фотографии будет необходимо определить тип. Для фотографии типа абсолютные нюдсы 
отправьте full_nudes, для нюдсов - nudes, для эстетичных - aesthetics, для мусора - delete. Ниже можете 
ознакомиться с примерами типов. """
        await update.message.reply_text(text)
        await update.message.reply_text(
            "Full nudes - фотографии с частичной или полной оголенностью. Обязательно сиськи, попы, вагины вся хуйня."
        )
        await update.message.reply_media_group(
            media=[
                telegram.InputMediaPhoto(photo_url)
                for photo_url in config.FilterersPhotos.full_nudes
            ]
        )
        await update.message.reply_text(
            "Nudes - фотографии, которые вроде и нюдсы, но не видно нихуя. Где одежды есть хотя бы"
        )
        await update.message.reply_media_group(
            media=[
                telegram.InputMediaPhoto(photo_url)
                for photo_url in config.FilterersPhotos.nudes
            ]
        )
        await update.message.reply_text(
            "Aesthetics - фотографии, которые не подходят под первые две категории и не совсем шлак. Всякие милые"
            "девочки, машинки, закаты хуяты, эстетика в общем. Но там блять цитаты всякие, кофты их нахуй в мусор"
        )
        await update.message.reply_media_group(
            media=[
                telegram.InputMediaPhoto(photo_url)
                for photo_url in config.FilterersPhotos.aesthetics
            ]
        )
        users.add_sorter(user)

    await update.message.reply_text("Удачной сортировки!", reply_markup=sorting_markup)
    logger.info(f"{C.blue}{update.message.from_user.first_name} (id:{user.id}){C.white}: started sorting")
    await send_photo_sorting(update, context)

    return SORTING


async def filtering_filter(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_reply = update.message.text
    photo_url = users.get_current_url_sorter(user)
    if user_reply != "delete":
        photos.add_to_allowed_photo_url(url=photo_url, categories=[user_reply], user=user)
        logger.info(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: "
                    f"{C.green}added{C.white} photo to the AllowedPhotosURLs")
    photos.delete_from_unsorted_photo_url(url=photo_url)
    logger.info(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: "
                f"{C.red}removed{C.white} photo from the UnsortedPhotosURLs")
    users.add_one_to_category_sorter(user, category=user_reply)
    await send_photo_sorting(update, context)


async def exit_sorting(update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Спасибо за работу",
        reply_markup=default_markup if update.message.from_user.id != 516229295 else admin_default_markup
    )
    logger.info(f"{C.blue}{update.message.from_user.first_name} (id:{update.message.from_user.id}){C.white}: "
                f"finished filtering")
    return ConversationHandler.END


def formatted_statistics(stats_data):
    users_data = []
    hyphen_counter = 64
    for user_data in stats_data:
        user_tag = f"@{user_data['user']['username']}"
        user_name = user_data["user"]["first_name"]
        added_at = user_data['added_at'].strftime("%A %d.%m.%Y, %H:%M:%S")
        last_seen = user_data.get("last_seen", user_data["added_at"]).strftime("%A %d.%m.%Y, %H:%M:%S")
        formatted_categories = "\n".join(
            f"<b>{category}</b>: {number}" for category, number in user_data['photos_counter'].items()
        )
        users_data.append(
            f"{user_tag} - <b>{user_name}</b>\n"
            f"<b>Added at</b>: {added_at}\n"
            f"<b>Last seen</b>: {last_seen}\n"
            f"\n"
            f"{formatted_categories}"
        )
    formatted_output = f"\n{'-' * hyphen_counter}\n".join(users_data)
    return formatted_output


async def get_sorter_stats_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if not users.is_sorter(user.id):
        await update.message.reply_text(f"Вы не идентифицированы как сортировщик.")
        return
    counter = users.get_stats_of_sorter(user)
    formatted_output = "\n".join(f"{category}: {number}" for category, number in counter.items())
    logger.info(f"Statistics of sorter {C.blue}{user.first_name} (id:{user.id}){C.white}: {counter}")
    await update.message.reply_text(f"Ваша статистика (как сортировщика):\n{formatted_output}")


async def get_sorters_stats_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id != 516229295:
        await update.message.reply_text("У вас нет доступа к этой команде")
        return
    clients_stats = users.get_stats_of_all_sorters(sorting="ASC")
    formatted_output = formatted_statistics(clients_stats)
    await update.message.reply_html(f"Статистика всех сортировщиков:\n{formatted_output}")
    logger.info(f"Statistics of sorters were asked by {C.blue}{user.first_name} (id:{user.id}){C.white}")


async def get_client_stats_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if not users.is_client(user.id):
        await update.message.reply_text(f"Вы не идентифицированы как клиент.")
        return
    counter = users.get_stats_of_client(user)
    formatted_output = "\n".join(f"{category}: {number}" for category, number in counter.items())
    logger.info(f"Statistics of client {C.blue}{user.first_name} (id:{user.id}){C.white}: {counter}")
    await update.message.reply_text(f"Ваша статистика (как клиента):\n{formatted_output}")


async def get_clients_stats_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user.id != 516229295:
        await update.message.reply_text("У вас нет доступа к этой команде")
        return
    clients_stats = users.get_stats_of_all_clients()
    formatted_output = formatted_statistics(clients_stats)
    await update.message.reply_html(f"Статистика всех клиентов:\n{formatted_output}")
    logger.info(f"Statistics of clients were asked by {C.blue}{user.first_name} (id:{user.id}){C.white}")


# async def start_with_shipping_callback(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
#     chat_id = update.message.chat_id
#     title = "Payment Example"
#     description = "Payment Example description"
#     payload = "Custom-Payload"
#     currency = "RUB"
#     price = 100
#     prices = [LabeledPrice("Test", price * 100)]
#     await update.message.reply_invoice(
#         title, description, payload, config.TELEGRAM_PAYMENT_PROVIDER_TOKEN, currency, prices,
#         need_name=True, need_email=True, need_shipping_address=True, is_flexible=True
#     )
#
#
# async def start_without_shipping_callback(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
#     chat_id = update.message.chat_id
#     title = "Payment Example"
#     description = "Payment Example description"
#     payload = "Custom-Payload"
#     currency = "RUB"
#     price = 100
#     prices = [LabeledPrice("Test", price * 100)]
#     await update.message.reply_invoice(
#         title, description, payload, config.TELEGRAM_PAYMENT_PROVIDER_TOKEN, currency, prices,
#         suggested_tip_amounts=[100 * 100, 500 * 100, 1000 * 100], max_tip_amount=1000 * 100
#     )
#
#
# async def shipping_callback(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
#     query = update.shipping_query
#     if query.invoice_payload != "Custom-Payload":
#         await query.answer(ok=False, error_message="Something went wrong...")
#         return
#     options = [ShippingOption("1", "Shipping Option A", [LabeledPrice("A", 100 * 100)])]
#     price_list = [LabeledPrice("B1", 150), LabeledPrice("B2", 200)]
#     options.append(ShippingOption("2", "Shipping Option B", price_list))
#     await query.answer(ok=True, shipping_options=options)
#
#
# async def precheckout_callback(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
#     query = update.pre_checkout_query
#     if query.invoice_payload != "Custom-Payload":
#         await query.answer(ok=False, error_message="Something went wrong...")
#     else:
#         await query.answer(ok=True)
#
#
# async def successful_payment_callback(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
#     await update.message.reply_text("Thank you for your payment!")


def main() -> None:
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_HTTP_API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("aesthetics", send_aesthetics_command))
    application.add_handler(CommandHandler("nudes", send_nudes_command))
    application.add_handler(CommandHandler("aesthetic_photo", send_aesthetic_photo_command))
    application.add_handler(CommandHandler("nude_photo", send_nudes_photo_command))

    application.add_handler(CommandHandler("photo_stats", get_photo_stats_command))
    application.add_handler(CommandHandler("sorter_stats", get_sorter_stats_command))
    application.add_handler(CommandHandler("sorters_stats", get_sorters_stats_command))
    application.add_handler(CommandHandler("client_stats", get_client_stats_command))
    application.add_handler(CommandHandler("clients_stats", get_clients_stats_command))

    filter_handler = ConversationHandler(
        entry_points=[CommandHandler("start_sorting", start_sorting)],
        states={
            SORTING: [
                MessageHandler(
                    filters.Regex(f"^({'|'.join(sorting_replies)})$"), filtering_filter
                )
            ]
        },
        fallbacks=[CommandHandler("exit", exit_sorting)],
    )

    application.add_handler(filter_handler)

    # application.add_handler(CommandHandler("shipping", start_with_shipping_callback))
    # application.add_handler(CommandHandler("noshipping", start_without_shipping_callback))
    # application.add_handler(ShippingQueryHandler(shipping_callback))
    # application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    # application.add_handler(
    #     MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    # )

    application.run_polling()


if __name__ == "__main__":
    main()
