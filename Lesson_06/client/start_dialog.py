from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, qApp
# from PyQt5.QtCore import QEvent


# Стартовый диалог с выбором имени пользователя
class UserNameDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.ok_pressed = False

        self.setWindowTitle('Привет!')
        self.setFixedSize(220, 110)

        self.label = QLabel('Введите имя пользователя:', self)
        self.label.move(10, 15)
        self.label.setFixedSize(205, 15)

        # строка ввода
        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(195, 20)
        self.client_name.move(10, 40)

        self.btn_ok = QPushButton('Начать', self)
        self.btn_ok.move(25, 70)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.move(110, 70)
        self.btn_cancel.clicked.connect(qApp.exit)

        self.show()

    # Обработчик кнопки ОК, если поле ввода не пустое, ставим флаг и завершаем приложение.
    def click(self):
        if self.client_name.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = UserNameDialog()
    app.exec_()
