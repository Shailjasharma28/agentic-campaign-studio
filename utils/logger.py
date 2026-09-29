import logging
from pathlib import Path

#--------------------------
# LOG DIRECTORY
#--------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

#--------------------------
#LOGGER 
#--------------------------

logger = logging.getLogger("agentic_campaign_studio")
logger.setLevel(logging.INFO)


if not logger.handlers:

    file_handler = logging.FileHandler(
        LOG_FILE, encoding="utf-8"
    )

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
       " %(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)