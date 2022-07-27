import logging
import os
from configparser import ConfigParser


class Config:
    KEY_SEPARATOR = "."

    def __init__(self, settings_path="test.txt") -> None:
        logging.getLogger(__name__)
        logging.warning(f'Current settings path {settings_path} - current execution path {os.path.realpath(__file__)}')
        self._file_path = os.environ.get("SETTINGS_PATH", settings_path)
        self._config = self._parse_file(self._file_path)

    @staticmethod
    def _parse_file(file_path):
        config_parser = ConfigParser()
        config_parser.read(file_path)
        return config_parser

    def __call__(self, key, default=None, cast=None):
        section, option = self._parse_key(key)
        if cast is bool:
            get = self._config.getboolean
        elif cast is int:
            get = self._config.getint
        elif cast is None:
            get = self._config.get
        else:
            cast_str = cast.__name__ if isinstance(cast, type) else repr(cast)
            raise ValueError("Unsupported cast: {}".format(cast_str))
        return get(section, option, fallback=default)

    @classmethod
    def _parse_key(cls, key):
        if cls.KEY_SEPARATOR not in key:
            return "DEFAULT", key
        return key.split(cls.KEY_SEPARATOR)


config = Config()

EVENT_STORE_PATH = config("EVENT_STORE_PATH")
CORS_ALLOW_ORIGINS = config("CORS.CORS_ALLOW_ORIGINS").split(",")
DATABASE_URL = os.environ.get("DATABASE_URL", config("DATABASE.DATABASE_URL"))
