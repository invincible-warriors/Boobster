import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

from main.bot_modules.ControlModule import ControlModule
from main.bot_modules.MarkupsModule import Markups
from main.bot_modules.PhotosSenderModule import PhotosSenderModule
from main.bot_modules.SortingModule import SortingModule
from main.bot_modules.StatisticsModule import StatisticsModule
from main.bot_modules.LoggingModule import logger
from main.config import config


async def start(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello",
        reply_markup=Markups.default if update.message.from_user.id != 516229295 else Markups.admin_default
    )


def main() -> None:
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_HTTP_API_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    ControlModule.add_module(application, StatisticsModule())
    ControlModule.add_module(application, SortingModule())
    ControlModule.add_module(application, PhotosSenderModule())

    application.run_polling()


if __name__ == "__main__":
    main()
