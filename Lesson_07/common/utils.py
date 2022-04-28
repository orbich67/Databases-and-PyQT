"""Утилиты"""

import json
import sys

sys.path.append('../')
from common.variables import *
from common.decos import log


@log
def get_message(client):
    """Утилита приема и декодирования сообщения
    принимает байты, выдает словарь, если принято что-то другое - отдаёт ошибку значения.
    :param client: сокет для передачи данных.
    :return: словарь - сообщение.
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock, message):
    """Утилита кодирования и отправки сообщения
    принимает словарь и отправляет его.
    :param sock: сокет для передачи.
    :param message: словарь для передачи.
    :return: ничего не возвращает.
    """
    if not isinstance(message, dict):
        raise TypeError
    js_message = json.dumps(message)
    sock.send(js_message.encode(ENCODING))
