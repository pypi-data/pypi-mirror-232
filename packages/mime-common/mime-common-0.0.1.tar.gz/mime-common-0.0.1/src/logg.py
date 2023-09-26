# Logger
# ################
import logging
import sys, os
from logging.handlers import RotatingFileHandler
from console import Console

LOGG_LEVEL = logging.INFO
LOGG_FILE = 'pyscript.log'
LOGG_MAX_SIZE = 4000000
LOGG_BACKUP_COUNT = 5
SHOW_IN_CONSOLE = False
CONSOLE_COLORS = False

class Logg:
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    _instance = None
    def __new__(cls, filename=LOGG_FILE, level=LOGG_LEVEL, show_in_console=SHOW_IN_CONSOLE, console_colors=CONSOLE_COLORS):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.show_in_console = show_in_console
            cls._instance.console = Console(use_colors=console_colors)
            cls._instance.logger = logging.getLogger(__name__)
            cls._instance.logger.setLevel(level)
            formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler = RotatingFileHandler(filename, maxBytes=LOGG_MAX_SIZE, backupCount=LOGG_BACKUP_COUNT)
            file_handler.setFormatter(formatter)
            cls._instance.logger.addHandler(file_handler)
        return cls._instance

    def debug(self, message):
        if logging.DEBUG >= self.logger.level:
            self.logger.debug(message)
            if self.show_in_console: self.console.debug(message)

    def info(self, message):
        if logging.INFO >= self.logger.level:
            self.logger.info(message)
            if self.show_in_console: self.console.info(message)

    def warning(self, message):
        if logging.WARNING >= self.logger.level:
            self.logger.warning(message)
            if self.show_in_console: self.console.warning(message)

    def error(self, message):
        if logging.ERROR >= self.logger.level:
            self.logger.error(message)
            if self.show_in_console: self.console.error(message)

    def critical(self, message):
        if logging.CRITICAL >= self.logger.level:
            self.logger.critical(message)
            if self.show_in_console: self.console.critical(message)

    def exception_string(self, e:Exception):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return f"{exc_type} {exc_obj} in {fname} line {exc_tb.tb_lineno}"
    
    def str2level(self, level_string:str = "INFO") -> int:
        if level_string == None:
            level_string = "INFO"
        level_string = level_string.upper()
        if level_string == "DEBUG":
            return logging.DEBUG
        elif level_string == "WARNING":
            return logging.WARNING
        elif level_string == "ERROR":
            return logging.ERROR
        elif level_string == "CRITICAL":
            return logging.CRITICAL
        return logging.INFO
