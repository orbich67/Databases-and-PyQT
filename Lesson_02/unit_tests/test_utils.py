"""Unit-тесты утилит"""

import sys
import os
import unittest
import json
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from common.utils import get_message, send_message


class TestSocket:
    """
    Тестовый класс для тестирования отправки и получения,
    при создании требует словарь, который будет прогоняться
    через тестовую функцию
    """
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        """
        Тестовая функция отправки, корректно кодирует сообщение,
        так же сохраняет то, что должно быть отправлено в сокет.
        message_to_send - то, что отправляем в сокет.
        :param message_to_send:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        # кодируем сообщение
        self.encoded_message = json_test_message.encode(ENCODING)
        # сохраняем то, что должно быть отправлено в сокет
        self.received_message = message_to_send

    def recv(self, max_len):
        """
        Получаем данные из сокета
        :param max_len:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 12.12,
        USER: {
            ACCOUNT_NAME: 'Guest'
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_send_message_ok(self):
        """
        Тест работы функции отправки,
        создаем тестовый сокет и проверяем корректность отправки словаря.
        :return:
        """
        # экземпляр тестового словаря
        test_socket = TestSocket(self.test_dict_send)
        # вызов тестируемой функции, результаты сохранятся в тестовом сокете
        send_message(test_socket, self.test_dict_send)
        # проверка корректности кодирования словаря
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)

    def test_send_message_err(self):
        """
        Тест исключения TypeError в функции отправки.
        :return:
        """
        # экземпляр тестового словаря
        test_socket = TestSocket(self.test_dict_send)
        # вызов тестируемой функции, результаты сохранятся в тестовом сокете
        send_message(test_socket, self.test_dict_send)
        # проверка исключения, если на входе передается не словарь
        self.assertRaises(TypeError, send_message, test_socket, 'wrong_dictionary')

    def test_get_message_ok(self):
        """
        Тест функции приема сообщения с корректным словарем.
        :return:
        """
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        # тест корректной расшифровки корректного словаря
        self.assertEqual(get_message(test_sock_ok), self.test_dict_recv_ok)

    def test_get_message_err(self):
        """
        Тест функции приема сообщения с ошибочным словарем.
        :return:
        """
        test_sock_err = TestSocket(self.test_dict_recv_err)
        # тест корректной расшифровки ошибочного словаря
        self.assertEqual(get_message(test_sock_err), self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()
