"""Декораторы"""

import sys
import logging
sys.path.append('../')
import logs.config_client_log
import logs.config_server_log

# определяем LOGGER для источника запуска
if sys.argv[0].find('client.py') == -1:
    LOGGER = logging.getLogger('server.py')
else:
    LOGGER = logging.getLogger('client.py')


def log(func_to_log):
    """Функция-декоратор, выполняющий логирование вызовов функций"""
    def log_saver(*args, **kwargs):
        LOGGER.debug(
            f'Была вызвана функция {func_to_log.__name__} c параметрами {args} , {kwargs}. '
            f'Вызов из модуля {func_to_log.__module__}')
        ret = func_to_log(*args, **kwargs)
        return ret

    return log_saver

