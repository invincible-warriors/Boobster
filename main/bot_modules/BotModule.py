from abc import abstractmethod
from telegram.ext import Handler


class BotModule:
    @abstractmethod
    def get_handlers(self) -> list[Handler]:
        pass
