import datetime
import sys

sys.path.append('../')
from common.variables import *
from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import os


# Класс - база данных сервера.
class ClientDatabase:
    # Класс - отображение таблицы известных пользователей.
    class KnownUsers:
        def __init__(self, user):
            self.id = None
            self.username = user

    # Класс - отображение таблицы истории сообщений
    class MessageStat:
        def __init__(self, contact, direction, message):
            self.id = None
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = datetime.datetime.now()

    # Класс - отображение списка контактов
    class Contacts:
        def __init__(self, contact):
            self.id = None
            self.name = contact

    # Конструктор класса:
    def __init__(self, name):
        # Создаём движок базы данных, поскольку разрешено несколько клиентов одновременно,
        # каждый должен иметь свою БД.
        # Поскольку клиент мультипоточный, то необходимо отключить проверки на подключения
        # с разных потоков, иначе sqlite3. ProgrammingError
        # connect_args={'check_same_thread': False} разрешить запись от одного пользователя с разных потоков
        path = os.path.dirname(os.path.realpath(__file__))
        base_client_dir = 'client_database'
        filename = f'client_{name}.db3'
        self.database_engine = create_engine(f'sqlite:///{os.path.join(path, base_client_dir, filename)}',
                                             echo=False,
                                             pool_recycle=7200,
                                             connect_args={'check_same_thread': False})

        # Создаём объект MetaData
        self.metadata = MetaData()

        # Создаём таблицу известных пользователей
        users = Table('known_users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String)
                      )

        # Создаём таблицу истории сообщений
        history = Table('message_history', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('contact', String),
                        Column('direction', String),
                        Column('message', Text),
                        Column('date', DateTime)
                        )

        # Создаём таблицу контактов
        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, unique=True)
                         )

        # Создаём таблицы
        self.metadata.create_all(self.database_engine)

        # Создаём отображения
        mapper(self.KnownUsers, users)
        mapper(self.MessageStat, history)
        mapper(self.Contacts, contacts)

        # Создаём сессию
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # Необходимо очистить таблицу контактов, т.к. при запуске они подгружаются с сервера.
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        """ Функция добавления контактов """
        if not self.session.query(self.Contacts).filter_by(name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def del_contact(self, contact):
        """ Функция удаления контакта """
        self.session.query(self.Contacts).filter_by(name=contact).delete()
        self.session.commit()

    def contacts_clear(self):
        """ Метод, очищающий таблицу со списком контактов. """
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_users(self, users_list):
        """ Функция добавления известных пользователей. """
        # Пользователи получаются только с сервера, поэтому таблица очищается.
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, contact, direction, message):
        """ Функция сохраняет сообщения """
        message_row = self.MessageStat(contact, direction, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        """ Функция возвращает контакты """
        return [contact[0] for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self):
        """ Функция возвращает список известных пользователей """
        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, user):
        """ Функция проверяет наличие пользователя в таблице Известных Пользователей """
        if self.session.query(self.KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        """ Функция проверяет наличие пользователя в таблице Контактов """
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact):
        """ Функция возвращает историю переписки """
        query = self.session.query(self.MessageStat).filter_by(contact=contact)
        return [(history_row.contact, history_row.direction,
                 history_row.message, history_row.date)
                for history_row in query.all()]


# отладка
if __name__ == '__main__':
    test_db = ClientDatabase('base_test')
    for i in ['User3', 'User4', 'User5']:
        test_db.add_contact(i)
    test_db.add_contact('User4')
    test_db.add_users(['User1', 'User2', 'User3', 'User4', 'User5'])
    test_db.save_message('User1', 'User2',
                         f'Привет! я тестовое сообщение от {datetime.datetime.now()}!')
    test_db.save_message('User2', 'User1',
                         f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!')
    print('get_contacts', test_db.get_contacts())
    print('get_users', test_db.get_users())
    print('check_user', test_db.check_user('User1'))
    print('check_user', test_db.check_user('User10'))
    print('check_contact', test_db.check_contact('User10'))
    print(test_db.get_history('User2'))
    print(sorted(test_db.get_history('User2') , key=lambda item: item[3]))
    print(test_db.get_history('User2'))
    test_db.del_contact('User1')
    test_db.del_contact('User2')
    test_db.del_contact('User3')
    test_db.del_contact('User4')
    test_db.del_contact('User5')
    print(test_db.get_contacts())
