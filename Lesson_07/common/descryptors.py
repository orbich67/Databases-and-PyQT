import logging


SERVER_LOGGER = logging.getLogger('server')


# Дескриптор для описания порта:
class Port:
    """Класс - дескриптор для номера порта.
    Позволяет использовать только порты с 1023 по 65536
    """
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            SERVER_LOGGER.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {value}. '
                f'В качестве порта должно быть указано число в диапазоне от 1024 до 65535.')
            exit(1)
        # Если порт прошёл проверку, добавляем его в список атрибутов экземпляра
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
