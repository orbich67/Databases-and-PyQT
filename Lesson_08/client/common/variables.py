import logging

# порт по умолчанию:
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента:
DEFAULT_IP_ADDRESS = '127.0.0.1'
# максимальная очередь подключений:
MAX_CONNECTIONS = 5
# Максимальная длина сообщения (байт):
MAX_PACKAGE_LENGTH = 10240
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
ACCOUNT_NAME= 'account_name'
SENDER = 'from'
DESTINATION = 'to'
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
DEL_CONTACT = 'del'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'
DATA = 'bin'
PUBLIC_KEY = 'pubkey'
PUBLIC_KEY_REQUEST = 'pubkey_need'

# Словари - ответы:
# 200
RESPONSE_200 = {RESPONSE: 200}
# 202
RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO: None
                }
# 205
RESPONSE_205 = {RESPONSE: 205}
# 400
RESPONSE_400 = {RESPONSE: 400,
                ERROR: None
                }
# 511
RESPONSE_511 = {RESPONSE: 511,
                DATA: None
                }
