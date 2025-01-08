from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

class MainMenuScreen(QWidget):
    switch_to_chat = pyqtSignal()
    switch_to_file_manager = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        chat_button = QPushButton("Join Chatroom")
        chat_button.clicked.connect(self.switch_to_chat)
        layout.addWidget(chat_button)

        file_manager_button = QPushButton("File Manager")
        file_manager_button.clicked.connect(self.switch_to_file_manager)
        layout.addWidget(file_manager_button)

        self.setLayout(layout)

