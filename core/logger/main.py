import logging

from core.meta.singleton import Singleton

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s]: %(message)s',
    datefmt='%H:%M:%S'
)


class Logger(metaclass=Singleton):
    def __init__(self):
        ...

    @staticmethod
    def queue_position(url: str, position: int):
        logging.info(f'Current queue position ({url}): {position}')

    @staticmethod
    def song_store(url: str, result: bool):
        if result is False:
            logging.info(f'Failed to store song {url}')
        logging.info(f'Stored {url}')

    @staticmethod
    def total(total_songs: int, ok_songs: int, failed_songs: int):
        logging.info(f'OK: {ok_songs}/{total_songs}. Failed: {failed_songs}/{total_songs}. Total: {ok_songs + failed_songs}/{total_songs}')

    @staticmethod
    def storing(url: str):
        logging.info(f'Storing {url}... ')

    @staticmethod
    def time(total_time: float):
        logging.info(f'Total time: {total_time:.2f}')