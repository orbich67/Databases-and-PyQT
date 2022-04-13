import logging

# порт по умолчанию:
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента:
DEFAULT_IP_ADDRESS = '127.0.0.1'
# максимальная очередь подключений:
MAX_CONNECTIONS = 5
# Максимальная длина сообщения (байт):
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'
# Текущий уровень логирования
LOGGING_LEVEL = logging.DEBUG
# База данных для хранения данных сервера:
SERVER_DATABASE = 'sqlite:///server_base.db3'

# Протокол JIM (ключи)
ACTION = 'action'
TIME = 'time'
USER = 'user'
SENDER = 'from'
DESTINATION = 'to'
ACCOUNT_NAME= 'account_name'
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'

# Словари - ответы:
# 200
RESPONSE_200 = {RESPONSE: 200}
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
