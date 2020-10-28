import logging
import datetime
from pathlib import Path

GAME_ROOT_DIR = Path(__file__).parent.absolute().resolve()

log_file_dir = GAME_ROOT_DIR / "log"
log_file = log_file_dir / "product{}.log".format(datetime.datetime.now())

log_file_dir.mkdir(exist_ok=True)
log_file.touch(exist_ok=True)

logging.basicConfig(
    filename=log_file,
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(lineno)d:%(message)s",
)


logger = logging.getLogger(__name__)

logger.info("Logger configured")
logger.debug("program root: %s", GAME_ROOT_DIR)
logger.debug("log file: %s", log_file)
