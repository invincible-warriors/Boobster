import telegram
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from .BotModule import BotModule
from .LoggingModule import logger
from ..config.config import (
    Colors as C
)
from ..database.database import (
    photos, users
)


class PhotosSenderModule(BotModule):
    @staticmethod
    async def send_aesthetics_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        users.add_number_to_category_client(user, category="aesthetics", number=5)
        photo_urls = photos.get_five_photo_by_category(category="aesthetics")
        await update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
        logger.info_by_user(user, f"{C.green}SUCCESS{C.white} - got five aesthetics photos")

    @staticmethod
    async def send_aesthetic_photo_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        users.add_number_to_category_client(user, category="aesthetics", number=1)
        photo_url = photos.get_one_photo_by_category(category="aesthetics")
        await update.message.reply_photo(photo_url)
        logger.info_by_user(user, f"{C.green}SUCCESS{C.white} - got one aesthetic photo")

    @staticmethod
    async def send_nudes_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        users.add_number_to_category_client(user, category="nudes", number=5)
        photo_urls = photos.get_five_photo_by_category(category="nudes")
        await update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
        logger.info_by_user(user, f"{C.green}SUCCESS{C.white} - got five nude photos")

    @staticmethod
    async def send_nudes_photo_command(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        users.add_number_to_category_client(user, category="nudes", number=1)
        photo_url = photos.get_one_photo_by_category(category="nudes")
        await update.message.reply_photo(photo_url)
        logger.info_by_user(user, f"{C.green}SUCCESS{C.white} - got one nude photo")

    def get_handlers(self) -> list[CommandHandler]:
        handlers = [
            CommandHandler("nudes", self.send_nudes_command),
            CommandHandler("nude_photo", self.send_nudes_photo_command),
            CommandHandler("aesthetics", self.send_aesthetics_command),
            CommandHandler("aesthetic_photo", self.send_aesthetic_photo_command),
        ]
        return handlers
