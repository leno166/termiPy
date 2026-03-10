from .helper import APP_DIR as APP_DIR, ROOT as ROOT
from _typeshed import Incomplete
from pathlib import Path

LOG_DIR_PATH: Incomplete
LOG_NAME: str
LOG_TIMESTAMP_FORMAT: str
LOG_TIMESTAMP_STR: Incomplete
LOG_FILE_PATH: Incomplete
logger: Incomplete
EXPIRATION_DATE_STR: str
EXPIRATION_DATE: Incomplete

def check_expiration() -> None: ...
def is_old(path: Path, days: int = 30) -> bool: ...
def cleanup_old_logs(days: int = 30) -> None: ...
def setup_logger(): ...
