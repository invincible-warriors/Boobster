import telegram
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from ..bot_modules.BotModule import BotModule
from ..config.config import (
    Colors as C
)
from ..database.database import (
    photos, users
)


class PhotosSenderModule(BotModule):
    async def send_aesthetics_command(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        users.add_number_to_category_client(user, category="aesthetics", number=5)
        photo_urls = photos.get_five_photo_by_category(category="aesthetics")
        await update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
        self.logger.info(f"{C.green}SUCCESS{C.white}: five aesthetics photos were sent to {C.blue}"
                         f"{user.first_name} (id:{user.id}){C.white}")

    async def send_aesthetic_photo_command(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        users.add_number_to_category_client(user, category="aesthetics", number=1)
        photo_url = photos.get_one_photo_url_by_category(category="aesthetics")
        await update.message.reply_photo(photo_url)
        self.logger.info(f"{C.green}SUCCESS{C.white}: one aesthetic photo was sent to {C.blue}"
                         f"{user.first_name} (id:{user.id}){C.white}")

    async def send_nudes_command(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        users.add_number_to_category_client(user, category="nudes", number=5)
        photo_urls = photos.get_five_photo_by_category(category="nudes")
        await update.message.reply_media_group(media=[telegram.InputMediaPhoto(photo_url) for photo_url in photo_urls])
        self.logger.info(f"{C.green}SUCCESS{C.white}: five nudes photos were sent to {C.blue}"
                         f"{user.first_name} (id:{user.id}){C.white}")

    async def send_nudes_photo_command(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        users.add_number_to_category_client(user, category="nudes", number=1)
        photo_url = photos.get_one_photo_url_by_category(category="nudes")
        await update.message.reply_photo(photo_url)
        self.logger.info(f"{C.green}SUCCESS{C.white}: one nude photo was sent to {C.blue}"
                         f"{user.first_name} (id:{user.id}){C.white}")

    def get_handlers(self) -> list[CommandHandler]:
        handlers = [
            CommandHandler("nudes", self.send_nudes_command),
            CommandHandler("nude_photo", self.send_nudes_photo_command),
            CommandHandler("aesthetics", self.send_aesthetics_command),
            CommandHandler("aesthetic_photo", self.send_aesthetic_photo_command),
        ]
        return handlers
