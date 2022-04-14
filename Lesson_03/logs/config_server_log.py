"""Конфиг серверного логгера"""

import sys
import os
import logging
sys.path.append(os.path.join(os.getcwd(), '..'))
import logging.handlers
from common.variables import LOGGING_LEVEL
sys.path.append('../')

# определяем формат сообщений:
SERVER_FORMATTER = logging.Formatter('%(asctime)-24s %(levelname)-9s %(filename)-13s %(message)s')

# Подготовка имени файла логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

# создаём потоки вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D')
LOG_FILE.setFormatter(SERVER_FORMATTER)

# создаём регистратор и настраиваем его
LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)


# проверка работы серверного конфига логов
if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.warning('Предупреждения')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
