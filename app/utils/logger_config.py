import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = "app.log"

logging.basicConfig(
    level=logging.INFO, format=LOG_FORMAT, filename=LOG_FILE, filemode="a"
)

LOGGER = logging.getLogger("chat_app")
