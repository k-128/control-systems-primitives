import os
import re
import logging
from logging import handlers
from pathlib import Path


def init_logger(
    logger_name: str       = "",
    log_level: int         = logging.INFO,
    date_fmt: str          = "%Y-%m-%d %H:%M:%S",
    date_fmt_show_ms: bool = True,
    file_name: str         = "_",
    logs_path: Path        = Path().cwd() / "bin/logs",
    raise_exceptions: bool = True
)-> logging.Logger:
    '''Initiate and get a logger that outputs to sys.stderr and daily files

    ```
    Params
    - logger_name: str          = ""
    - log_level: int            = logging.INFO
    - date_fmt: str             = "%Y-%m-%d %H:%M:%S"
    - file_name: str            = "_"
    - logs_path: Path           = Path().cwd() / "bin/logs"
    - raise_exceptions: bool    = True

    Resources
    - https://docs.python.org/3/library/logging.html
    ```
    '''
    os.makedirs(logs_path, exist_ok=True)

    # Set logger
    logger    = logging.getLogger(logger_name)
    show_ms   = ".%(msecs)03d" if date_fmt_show_ms else ""
    formatter = logging.Formatter(
        f"%(levelname)s\t[%(asctime)s{show_ms}] %(name)s - %(message)s",
        date_fmt
    )
    logger.setLevel(log_level)
    logging.raiseExceptions = raise_exceptions

    # Set stream to sys.stderr
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Set stream to daily files
    hdlr = handlers.TimedRotatingFileHandler(
        filename=f"{logs_path}/{file_name}",
        when="midnight",
        interval=1,
        encoding="utf-8",
        utc=True,
    )
    # Override conditional properties to append '.log' to the filename
    if "suffix" in hdlr.__dict__:
        hdlr.__dict__["suffix"] = "-%Y_%m_%d.log"
        extMatch = r"^-\d{4}_\d{2}_\d{2}(\.\w+)?.log$"
        hdlr.__dict__["extMatch"] = re.compile(extMatch, re.ASCII)
    #hdlr.rotation_filename = lambda default_name: f"{default_name}.log"
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)

    return logger


if __name__ == "__main__":
    log = init_logger()
    log.info("hello world")
