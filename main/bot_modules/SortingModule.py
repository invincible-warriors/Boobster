from typing import Any

import telegram
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler, filters

from ..bot_modules.BotModule import BotModule
from ..bot_modules.MarkupsModule import Markups
from ..config.config import (
    Colors as C,
    FilterersPhotos
)
from ..database.database import (
    photos, users,
    URLAlreadyExistsError
)


class SortingModule(BotModule):
    SORTING = 0

    async def send_photo_sorting(self, update: Update, context: CallbackContext.DEFAULT_TYPE):
        photo_url = photos.get_photo_for_sorting()
        user = update.message.from_user
        while True:
            try:
                await update.message.reply_photo(photo=photo_url)
                break
            except telegram.error.BadRequest:
                self.logger.error(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: "
                                  f"{C.red}BadRequest{C.white}. Deleted and blocked photo")
                photos.delete_from_unsorted_photo_url(photo_url)
                try:
                    photos.add_to_blocked_photo_url(photo_url, user="bot")
                except URLAlreadyExistsError:
                    pass
        users.set_current_url_sorter(user, photo_url)
        self.logger.info(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: Set photo_url for sorter ")
        return self.SORTING

    async def start_sorting(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        if not users.is_sorter(user.id):
            text = """Спасибо, что согласились поучаствовать в проекте Boobster. Ваша задача сортировать фотографии для 
    создания базы данных по категориям. Всего есть 4 типа: абсолютные нюдсы, полу нюдсы, эстетичные фотографии и 
    ссаный шлак. Для каждой фотографии будет необходимо определить тип. Для фотографии типа абсолютные нюдсы 
    отправьте full_nudes, для нюдсов - nudes, для эстетичных - aesthetics, для мусора - delete. Ниже можете 
    ознакомиться с примерами типов. """
            await update.message.reply_text(text)
            await update.message.reply_text(
                "Full nudes - фотографии с частичной или полной оголенностью. Обязательно сиськи, попы, вагины вся "
                "хуйня. "
            )
            await update.message.reply_media_group(
                media=[
                    telegram.InputMediaPhoto(photo_url)
                    for photo_url in FilterersPhotos.full_nudes
                ]
            )
            await update.message.reply_text(
                "Nudes - фотографии, которые вроде и нюдсы, но не видно нихуя. Где одежды есть хотя бы"
            )
            await update.message.reply_media_group(
                media=[
                    telegram.InputMediaPhoto(photo_url)
                    for photo_url in FilterersPhotos.nudes
                ]
            )
            await update.message.reply_text(
                "Aesthetics - фотографии, которые не подходят под первые две категории и не совсем шлак. Всякие милые"
                "девочки, машинки, закаты хуяты, эстетика в общем. Но там блять цитаты всякие, кофты их нахуй в мусор"
            )
            await update.message.reply_media_group(
                media=[
                    telegram.InputMediaPhoto(photo_url)
                    for photo_url in FilterersPhotos.aesthetics
                ]
            )
            users.add_sorter(user)

        await update.message.reply_text("Удачной сортировки!", reply_markup=Markups.sorting)
        self.logger.info(f"{C.blue}{update.message.from_user.first_name} (id:{user.id}){C.white}: started sorting")
        await self.send_photo_sorting(update, context)

        return self.SORTING

    async def filtering_filter(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        user_reply = update.message.text
        photo_url = users.get_current_url_sorter(user)
        if user_reply != "delete":
            try:
                photos.add_to_allowed_photo_url(url=photo_url, categories=[user_reply], user=user)
                self.logger.info(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: "
                                 f"{C.green}added{C.white} photo to the AllowedPhotosURLs")
            except URLAlreadyExistsError:
                self.logger.warn(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: "
                                 f"{C.yellow}some error was occurred{C.white} but handled")
        photos.delete_from_unsorted_photo_url(url=photo_url)
        self.logger.info(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: "
                         f"{C.red}removed{C.white} photo from the UnsortedPhotosURLs")
        users.add_one_to_category_sorter(user, category=user_reply)
        await self.send_photo_sorting(update, context)

    async def exit_sorting(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            "Спасибо за работу",
            reply_markup=Markups.default if update.message.from_user.id != 516229295 else Markups.admin_default
        )
        self.logger.info(f"{C.blue}{update.message.from_user.first_name} (id:{update.message.from_user.id}){C.white}: "
                         f"finished filtering")
        return ConversationHandler.END

    def get_handlers(self) -> list[ConversationHandler[CallbackContext | Any]]:
        handlers = [
            ConversationHandler(
                entry_points=[CommandHandler("start_sorting", self.start_sorting)],
                states={
                    self.SORTING: [
                        MessageHandler(
                            filters.Regex(f"^({'|'.join(Markups.keyboards.sorting[0])})$"), self.filtering_filter
                        )
                    ]
                },
                fallbacks=[CommandHandler("exit", self.exit_sorting)],
            )
        ]
        return handlers
