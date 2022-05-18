from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from .BotModule import BotModule
from .ControlModule import Permissions, control
from .LoggingModule import logger
from ..config.config import Collections
from ..config.config import Colors as C
from ..database.database import photos, users


class StatisticsModule(BotModule):
    @staticmethod
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

    async def get_photo_stats_command(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        counters = photos.get_stats_of_photos()
        allowed_photos_formatted = "\n".join(
            f"{category}: {number}" for category, number in counters[Collections.allowed].items()
        )
        await update.message.reply_text(
            f"Статистика по фотографиям:\n"
            f"{Collections.allowed}:\n{allowed_photos_formatted}\n\n"
            f"{Collections.unsorted}: {counters[Collections.unsorted]}\n"
            f"{Collections.blocked}: {counters[Collections.blocked]}"
        )
        user = update.message.from_user
        logger.info_by_user(user, f"Got statistics of {C.purple}photos{C.white}")

    @control.permission(Permissions.sorter)
    async def get_sorter_stats_command(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        counter = users.get_stats_of_sorter(user)
        formatted_output = "\n".join(f"{category}: {number}" for category, number in counter.items())
        await update.message.reply_text(f"Ваша статистика (как сортировщика):\n{formatted_output}")
        logger.info_by_user(user, f"Got statistics of {C.purple}sorter{C.white}")

    @control.permission(Permissions.admin)
    async def get_sorters_stats_command(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        clients_stats = users.get_stats_of_all_sorters(sorting="ASC")
        formatted_output = self.formatted_statistics(clients_stats)
        await update.message.reply_html(f"Статистика всех сортировщиков:\n{formatted_output}")
        logger.info_by_user(user, f"Got statistics of {C.purple}sorters{C.white}")

    @control.permission(Permissions.client)
    async def get_client_stats_command(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        counter = users.get_stats_of_client(user)
        formatted_output = "\n".join(f"{category}: {number}" for category, number in counter.items())
        await update.message.reply_text(f"Ваша статистика (как клиента):\n{formatted_output}")
        logger.info_by_user(user, f"Got statistics of {C.purple}client{C.white}")

    @control.permission(Permissions.admin)
    async def get_clients_stats_command(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        clients_stats = users.get_stats_of_all_clients()
        formatted_output = self.formatted_statistics(clients_stats)
        await update.message.reply_html(f"Статистика всех клиентов:\n{formatted_output}")
        logger.info_by_user(user, f"Got statistics of {C.purple}clients{C.white}")

    def get_handlers(self) -> list[CommandHandler]:
        handlers = [
            CommandHandler("photo_stats", self.get_photo_stats_command),
            CommandHandler("sorter_stats", self.get_sorter_stats_command),
            CommandHandler("sorters_stats", self.get_sorters_stats_command),
            CommandHandler("client_stats", self.get_client_stats_command),
            CommandHandler("clients_stats", self.get_clients_stats_command)
        ]
        return handlers
