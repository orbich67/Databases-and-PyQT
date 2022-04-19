"""Декораторы"""

import sys
import logging
import logs.config_client_log
import logs.config_server_log
import traceback


# определяем LOGGER для источника запуска
if sys.argv[0].find('client.py') == -1:
    LOGGER = logging.getLogger('server.py')
else:
    LOGGER = logging.getLogger('client.py')


def log(func_to_log):
    """Функция-декоратор"""
    def log_saver(*args, **kwargs):
        res = func_to_log(*args, **kwargs)
        #
        LOGGER.debug(f'Была вызвана функция: {func_to_log.__name__}, с параметрами: {args}, {kwargs}. '
                     f'Вызов из модуля: {func_to_log.__module__}. '
                     f'Вызов из функции: {traceback.format_stack()[0].strip().split()[-1]}')

        return res
    return log_saver
