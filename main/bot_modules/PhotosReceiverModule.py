from enum import Enum, auto

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Handler, ConversationHandler, MessageHandler, filters

from .BotModule import BotModule
from .ControlModule import Permissions, control
from .LoggingModule import logger
from ..database.database import photos


class States:
    GETTING_PHOTOS = 1


class PhotosReceiverModule(BotModule):
    def __init__(self):
        self.nicknames = {}

    @control.permission(Permissions.sorter)
    async def start_receiving(self, update: Update, context: CallbackContext) -> int:
        print(1)
        user = update.message.from_user
        await update.message.reply_text("Для помощи введите /help")
        logger.info_by_user(user, "Started sending photos")
        nicknames = photos.get_nicknames()
        formatted_nicknames = "\n".join(f"{i + 1}. {nickname}" for i, nickname in enumerate(nicknames))
        if nicknames:
            await update.message.reply_text(
                f"Если никнейм есть в этом списке, пожалуйста напишите его точно так же во избежании ошибок"
                f":\n{formatted_nicknames}"
            )
        await update.message.reply_text("Задайте никнейм командой /name")
        return States.GETTING_PHOTOS

    @staticmethod
    async def help_receiving(update: Update, context: CallbackContext) -> None:
        await update.message.reply_text("1. Используйте команду /name {ник модели}"
                                        "2. Начинайте присылать фотографии модели."
                                        "3. По завершении нажмите /end")

    async def set_nickname(self, update: Update, context: CallbackContext) -> int:
        print(2)
        user = update.message.from_user
        nickname = " ".join(update.message.text.split()[1:])
        logger.info_by_user(user, f"Set nickname to `{nickname}`")
        self.nicknames[user.id] = {
            "nickname": nickname,
            "photo_counter": 0
        }
        await update.message.reply_text("Отлично! Теперь можете присылать фотографии модели")
        return States.GETTING_PHOTOS

    @staticmethod
    async def receiving(update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        print(3)
        user = update.message.from_user
        photo = update.message.photo[-1].file_id
        hash_ = await photos.add_to_unsorted_photos(photo, context)
        logger.info_by_user(user, f"Added telegram photo ({hash_})")
        return States.GETTING_PHOTOS

    async def stop_receiving(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> ConversationHandler:
        print(4)
        data = self.nicknames.pop(update.message.from_user)
        await update.message.reply_text(
            f"Спасибо за работу. Вы добавили {data['photo_counter']} фото {data['nickname']}"
        )
        logger.info("Finished sending photos")
        return ConversationHandler.END

    def get_handlers(self) -> list[Handler]:
        handlers = [
            ConversationHandler(
                entry_points=[CommandHandler("start_receiving", self.start_receiving)],
                states={
                    States.GETTING_PHOTOS: [
                        # MessageHandler(filters.PHOTO, self.receiving),
                        CommandHandler("name", self.set_nickname)
                    ]
                },
                fallbacks=[CommandHandler("end", self.stop_receiving)],
            )
        ]
        return handlers
