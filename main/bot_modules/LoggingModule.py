import logging
import telegram
from ..config.config import Colors as C

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class Logger(logging.getLoggerClass()):
    def info_by_user(self, user: telegram.User, message: str):
        self.info(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: {message}")

    def error_by_user(self, user: telegram.User, message: str):
        self.error(f"{C.blue}{user.first_name} (id:{user.id}){C.white}: {message}")


logging.setLoggerClass(Logger)
logger = logging.getLogger(__name__)
