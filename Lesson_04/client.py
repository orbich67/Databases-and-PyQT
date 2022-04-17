"""Программа-клиент"""

import sys
import socket
import time
import argparse
import logging
import threading
import logs.config_client_log
from common.utils import *
from common.variables import *
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from decos import log
from metaclasses import ClientMaker
from client_database import ClientDatabase


# Инициализация клиентского логгера
CLIENT_LOGGER = logging.getLogger('client')

# Объект блокировки сокета и работы с базой данных
sock_lock = threading.Lock()
database_lock = threading.Lock()


# Класс формировки и отправки сообщений на сервер и взаимодействия с пользователем.
class ClientSender(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    def create_exit_message(self):
        """ Функция создаёт словарь с сообщением о выходе """
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def create_message(self):
        """ Функция запрашивает сообщение и кому отправить сообщение,
        и отправляет полученные данные на сервер """
        to = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')

        # Проверка существования получателя сообщения
        with database_lock:
            if not self.database.check_user(to):
                CLIENT_LOGGER.error(f'Попытка отправить сообщение '
                             f'незарегистрированному получателю: {to}')
                return

        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')

        # Сохраняем сообщения в истории
        with database_lock:
            self.database.save_message(self.account_name, to, message)

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with sock_lock:
            try:
                send_message(self.sock, message_dict)
                CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to}')
            except OSError as err:
                if err.errno:
                    CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
                    exit(1)
                else:
                    CLIENT_LOGGER.error('Не удалось передать сообщение. Таймаут соединения')

    def run(self):
        """ Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения """
        self.print_help()
        while True:
            command = input('Введите команду: ')
            # Если 'message' - вызываем метод отправки сообщений
            if command == 'message':
                self.create_message()
            # Если 'help' - выводим список команд
            elif command == 'help':
                self.print_help()
            # Если 'exit' - отправляем сообщение серверу о выходе и завершаем соединение.
            elif command == 'exit':
                with sock_lock:
                    try:
                        send_message(self.sock, self.create_exit_message())
                    except Exception as e:
                        print(e)
                        pass
                    print('Завершение соединения.')
                    CLIENT_LOGGER.info(f'Завершение работы по команде пользователя {self.account_name}.')
                    # Задержка необходима, чтобы успело уйти сообщение о выходе
                    time.sleep(0.5)
                    break
            # Если 'contacts' - выводим список контактов пользователя
            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contacts()
                if not contacts_list:
                    print('Список контактов пуст...')
                for contact in contacts_list:
                    print(contact)
            # Если 'edit' - редактирование контактов
            elif command == 'edit':
                self.edit_contacts()
            # Если 'history' - история сообщений.
            elif command == 'history':
                self.print_history()
            else:
                print('Команда не распознана, попробуйте снова. help - вывести поддерживаемые команды.')

    def print_help(self):
        """Функция, выводящая справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('history - история сообщений')
        print('contacts - список контактов')
        print('edit - редактирование списка контактов')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def print_history(self):
        """ Функция вывода истории сообщений """
        ask = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with database_lock:
            if ask == 'in':
                history_list = self.database.get_history(to_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} '
                          f'от {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(from_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} '
                          f'от {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]},'
                          f' пользователю {message[1]} '
                          f'от {message[3]}\n{message[2]}')

    def edit_contacts(self):
        """ Функция редактирования контактов """
        ans = input('Для удаления введите "del", для добавления "add": ')
        if ans == 'del':
            edit = input('Введите имя контакта для удаления: ')
            if self.database.check_contact(edit):
                with database_lock:
                    self.database.del_contact(edit)
                with sock_lock:
                    try:
                        del_contact(self.sock, self.account_name, edit)
                    except:
                        pass
            else:
                CLIENT_LOGGER.error('Попытка удаления несуществующего контакта.')
        elif ans == 'add':
            edit = input('Введите имя создаваемого контакта: ')
            # Проверка на существование контакта в базе данных
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with sock_lock:
                    try:
                        add_contact(self.sock, self.account_name, edit)
                    except ServerError:
                        CLIENT_LOGGER.error('Не удалось отправить информацию на сервер.')


# Класс-приёмник сообщений с сервера. Принимает сообщения, выводит в консоль.
class ClientReader(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    def run(self):
        """ Основной цикл приёмника сообщений, принимает сообщения, выводит в консоль.
            Завершается при потере соединения."""
        while True:
            # Задержка на 1-ну секунду перед попыткой захвата сокета.
            # Если не сделать - второй поток может долго ждать освобождения сокета.
            time.sleep(1)
            with sock_lock:
                try:
                    message = get_message(self.sock)

                except IncorrectDataRecivedError:
                    CLIENT_LOGGER.error(f'Не удалось декодировать полученное сообщение.')
                    # Вышел таймаут соединения если error = None, иначе обрыв соединения.
                except OSError as err:
                    if err.errno:
                        CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                        break
                    # Проблемы с соединением
                except (ConnectionError,
                        ConnectionAbortedError,
                        ConnectionResetError,
                        json.JSONDecodeError):
                    CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                    break
                    # Если пакет корректно получен выводим в консоль и записываем в базу.
                else:
                    if ACTION in message and message[ACTION] == MESSAGE \
                            and SENDER in message \
                            and DESTINATION in message \
                            and MESSAGE_TEXT in message \
                            and message[DESTINATION] == self.account_name:
                        print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                        # Захватываем работу с базой данных и сохраняем в неё сообщение
                        with database_lock:
                            try:
                                self.database.save_message(message[SENDER],
                                                           self.account_name,
                                                           message[MESSAGE_TEXT])
                            except Exception as e:
                                print(e)
                                CLIENT_LOGGER.error('Ошибка взаимодействия с базой данных!')
                        CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}: {message[MESSAGE_TEXT]}')
                    else:
                        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')



@log
def create_presence(account_name):
    """ Функция генерирует запрос о присутствии клиента """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def process_response_ans(message):
    """ Функция разбирает ответ сервера """
    CLIENT_LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


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


def add_contact(sock, username, contact):
    """ Функция добавления пользователя в контакт лист """
    CLIENT_LOGGER.debug(f'Создание контакта {contact}')
    req = {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        print(f'Контакт {contact} успешно добавлен!')
        pass
    else:
        raise ServerError('Ошибка добавления контакта!')


def del_contact(sock, username, contact):
    """Функция удаления пользователя из списка контактов"""
    CLIENT_LOGGER.debug(f'Удаление контакта {contact}')
    req = {
        ACTION: DEL_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        print(f'Контакт {contact} успешно удален!')
        pass
    else:
        raise ServerError(f'Ошибка удаления контакта {contact}!')


def contacts_list_request(sock, name):
    """Функция запроса листа с контактами"""
    CLIENT_LOGGER.debug(f'Запрос контакт листа для пользователя {name}')
    req = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER: name
    }
    CLIENT_LOGGER.debug(f'Сформирован запрос {req}')
    send_message(sock, req)
    ans = get_message(sock)
    CLIENT_LOGGER.debug(f'Получен ответ {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    raise ServerError


def user_list_request(sock, username):
    """Функция запроса списка известных пользователей"""
    CLIENT_LOGGER.debug(f'Запрос списка известных пользователей {username}')
    req = {
        ACTION: USERS_REQUEST,
        TIME: time.time(),
        ACCOUNT_NAME: username
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    raise ServerError


def database_load(sock, database, username):
    """ Функция инициализатор базы данных.
        Запускается при запуске, загружает данные в базу с сервера.
        Загружаем список известных пользователей """
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        CLIENT_LOGGER.error('Ошибка запроса списка известных пользователей.')
    else:
        database.add_users(users_list)
    # Загружаем список контактов
    try:
        contacts_list = contacts_list_request(sock, username)
    except ServerError:
        CLIENT_LOGGER.error('Ошибка запроса списка контактов.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


def main():
    # Загружаем параметры командной строки
    server_address, server_port, client_name = arg_parser()

    # Сообщение о запуске
    print(f'Консольный мессенджер. Клиентский модуль. Имя пользователя: {client_name}')

    # Запрашиваем имя пользователя, если оно не было задано.
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    CLIENT_LOGGER.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address} , '
        f'порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Таймаут 1-на секунда, необходим для освобождения сокета.
        transport.settimeout(1)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_response_ans(get_message(transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Принят ответ: {answer}')
        print(f'Соединение с сервером установлено.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        exit(1)
    else:
        # Инициализация базы данных
        database = ClientDatabase(client_name)
        database_load(transport, database, client_name)

        # если соединение с сервером установлено корректно, запускаем процесс приема сообщений клиентом
        module_reciver = ClientReader(client_name, transport, database)
        module_reciver.daemon = True
        module_reciver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        module_sender = ClientSender(client_name, transport, database)
        module_sender.daemon = True
        module_sender.start()
        CLIENT_LOGGER.debug('Запущены процессы.')

        # Основной цикл, если один из потоков завершён, то значит или потеряно соединение, или пользователь
        # ввёл exit. Поскольку все события обрабатываются в потоках, достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if module_reciver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
