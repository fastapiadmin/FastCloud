from app.config.path_conf import BANNER_FILE
from app.core.logger import log


def worship() -> None:
    """
    读取并打印启动 Banner（优先 `banner.txt`，并附带当前环境名）。

    参数:
    - None

    返回:
    - None
    """
    if BANNER_FILE.exists():
        banner = BANNER_FILE.read_text(encoding="utf-8")
        log.info(banner)
