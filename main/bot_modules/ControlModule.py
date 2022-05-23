from enum import Enum, auto

from telegram import Update, User
from telegram.ext import Application, CallbackContext

from .LoggingModule import logger
from ..database.database import users


class Permissions(Enum):
    admin = auto()
    sorter = auto()
    client = auto()
    all = auto()


class ControlModule:
    def __init__(self):
        self.admins = [
            516229295,  # Parzival
        ]

    @staticmethod
    def add_module(application: Application, module):
        handlers = module.get_handlers()
        application.add_handlers(handlers)

    @staticmethod
    async def raise_warn(update: Update, permission: Permissions, user: User):
        logger.error_by_user(user, f"Permission `{permission.name}` denied")
        return await update.message.reply_html(
            f"Вы должны иметь уровень доступа <b>{permission.name}</b>, чтобы использовать эту команду"
        )

    def permission(self, permission_type: Permissions = Permissions.all):
        def decorator(func):
            async def inner(other, update: Update, context: CallbackContext, *args, **kwargs):
                user = update.message.from_user
                match permission_type:
                    case Permissions.client:
                        if not users.is_client(user.id):
                            return await self.raise_warn(update, permission_type, user)
                    case Permissions.sorter:
                        if not users.is_sorter(user.id):
                            return await self.raise_warn(update, permission_type, user)
                    case Permissions.admin:
                        if user.id not in self.admins:
                            return await self.raise_warn(update, permission_type, user)
                await func(other, update, context)
            return inner
        return decorator


control = ControlModule()
