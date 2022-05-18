from telegram import Update
from telegram.ext import Application, CallbackContext

from .LoggingModule import logger
from ..database.database import users


class Permissions:
    admin = "admin"
    sorter = "sorter"
    client = "client"
    all = "all"


class ControlModule:
    def __init__(self):
        self.admins = [
            516229295,  # Parzival
        ]

    @staticmethod
    def add_module(application: Application, module):
        handlers = module.get_handlers()
        application.add_handlers(handlers)

    def permission(self, permission_type: str = Permissions.all):
        def decorator(func):
            async def inner(other, update: Update, context: CallbackContext, *args, **kwargs):
                user = update.message.from_user
                match permission_type:
                    case Permissions.client:
                        if not users.is_client(user.id):
                            logger.error_by_user(user, "Permission `client` denied")
                            return await update.message.reply_text(
                                "Вы должны быть клиентом, чтобы использовать эту команду"
                            )
                    case Permissions.sorter:
                        if not users.is_sorter(user.id):
                            logger.error_by_user(user, "Permission `sorter` denied")
                            return await update.message.reply_text(
                                "Вы должны быть сортировщиком, чтобы использовать эту команду"
                            )
                    case Permissions.admin:
                        if user.id not in self.admins:
                            logger.error_by_user(user, "Permission `admin` denied")
                            return await update.message.reply_text(
                                "Вы должны быть администратором, чтобы использовать эту команду"
                            )
                await func(other, update, context)
            return inner
        return decorator


control = ControlModule()
