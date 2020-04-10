import logging
from src.utils.configurer import config


class Logger:
    def __init__(self, filename: str) -> None:
        logging.basicConfig(
            filename=filename,
            filemode='a',
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%d-%b-%y %H:%M:%S',
        )
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler())
        self.level_int_mapping = {
            "critical": 50,
            "error": 40,
            "warning": 30,
            "info": 20,
            "debug": 10
        }

    def log(self, level: str, message: str) -> bool:
        logging.log(self.level_int_mapping[level.lower()], message)
        return True


logger = Logger(config.get_configuration("log_filename", "SYSTEM"))
