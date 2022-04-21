"""Конфиг клиентского логгера"""

import sys
import os
import logging
sys.path.append('../')
# sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import LOGGING_LEVEL



# определяем формат сообщений:
CLIENT_FORMATTER = logging.Formatter('%(asctime)-24s %(levelname)-9s %(filename)-15s %(message)s')

# подготовка имени файла логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

# создаём потоки вывода логов
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.INFO)
LOG_FILE = logging.FileHandler(PATH, encoding='utf8')
LOG_FILE.setFormatter(CLIENT_FORMATTER)

# создаём регистратор и настраиваем его
LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)


# проверка работы клиентского конфига логов
if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.warning('Предупреждения')
    LOGGER.info('Информационное сообщение')
    LOGGER.debug('Отладочная информация')
