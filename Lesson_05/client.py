"""Программа-клиент"""

import logging
import logs.config_client_log
import argparse
import sys
from PyQt5.QtWidgets import QApplication

from common.variables import *
from errors import ServerError
from decos import log
from client.database import ClientDatabase
from client.transport import ClientTransport
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog


# Инициализация клиентского логгера
CLIENT_LOGGER = logging.getLogger('client')


@log
def arg_parser():
    """ Парсер аргументов командной строки,
    читает и возвращает 3 параметра (server_address, server_port, client_mode) """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'В качестве порта может быть указано число в диапазоне от 1024 до 65535')
        exit(1)
    return server_address, server_port, client_name


if __name__ == '__main__':
    # Загружаем параметры командной строки
    server_address, server_port, client_name = arg_parser()

    # Создаём клиентское приложение
    client_app = QApplication(sys.argv)

    # Запрашиваем имя пользователя, если оно не было задано.
    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()
        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и удаляем объект.
        # Иначе - выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    CLIENT_LOGGER.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address} , '
        f'порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация базы данных
    database = ClientDatabase(client_name)

    # Создаём объект - транспорт и запускаем транспортный поток
    try:
        transport = ClientTransport(server_port, server_address, database, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    # Создаём GUI
    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    # Раз графическая оболочка закрылась, закрываем транспорт
    transport.transport_shutdown()
    transport.join()
