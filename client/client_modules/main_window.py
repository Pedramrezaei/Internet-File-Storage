import os
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QBrush, QColor
from .login import LoginScreen
from .main_menu import MainMenuScreen
from .file_manager import FileManagerScreen
from .chat import ChatScreen
import socket
from .constants import HOST, TCP_PORT, UDP_PORT


class CurvedDesign(QWidget):
    """Widget to draw the curved design."""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        brush = QBrush(QColor("#1d9bf0"))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(-100, 100, 600, 500)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.username = None
        self.setWindowTitle("Webeloper")
        self.setGeometry(200, 200, 1000, 600)

        # Load and apply the external stylesheet
        self.apply_stylesheet()

        # Central widget and layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # Top bar for greeting and logout button
        self.top_bar_layout = QHBoxLayout()
        self.top_bar_layout.setContentsMargins(10, 10, 10, 10)

        # Greeting label
        self.greeting_label = QLabel("")
        self.greeting_label.setObjectName("greeting_label")
        self.greeting_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.setObjectName("logout_button")
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setFixedSize(100, 30)
        self.logout_button.setVisible(False)

        self.top_bar_layout.addWidget(self.greeting_label)
        self.top_bar_layout.addWidget(self.logout_button)
        self.layout.addLayout(self.top_bar_layout)

        # Stacked widget for screen switching
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        self.setCentralWidget(self.central_widget)

        # Sockets
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, TCP_PORT))

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Screens
        self.login_screen = LoginScreen(self.client_socket)
        self.main_menu_screen = MainMenuScreen()
        self.file_manager_screen = FileManagerScreen(self.client_socket)
        self.file_manager_screen.switch_to_main_menu.connect(self.show_main_menu)  # Connect signal here
        self.chat_screen = ChatScreen(self.udp_socket, self.username)

        # Connect signals
        self.login_screen.switch_to_main.connect(self.show_main_menu)
        self.main_menu_screen.switch_to_file_manager.connect(self.show_file_manager)
        self.main_menu_screen.switch_to_chat.connect(self.show_chat_screen)
        self.chat_screen.switch_to_main_menu.connect(self.show_main_menu)

        # Add screens to stack
        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.main_menu_screen)
        self.stack.addWidget(self.file_manager_screen)
        self.stack.addWidget(self.chat_screen)
        self.stack.setCurrentWidget(self.login_screen)

    def show_main_menu(self):
        """Switch to the main menu screen."""
        self.username = self.login_screen.username_input.text()
        self.update_greeting()
        self.logout_button.setVisible(True)
        self.stack.setCurrentWidget(self.main_menu_screen)

    def show_file_manager(self):
        """Switch to the file manager screen."""
        self.update_greeting()
        self.logout_button.setVisible(True)
        self.stack.setCurrentWidget(self.file_manager_screen)

    def show_chat_screen(self):
        """Switch to the chat screen."""
        self.chat_screen.username = self.username
        self.chat_screen.send_username_to_server()
        self.update_greeting()
        self.logout_button.setVisible(True)
        self.stack.setCurrentWidget(self.chat_screen)

    def update_greeting(self):
        """Update the greeting label with the signed-in username."""
        if self.username:
            self.greeting_label.setText(f"Hi, {self.username}")
        else:
            self.greeting_label.clear()

    def logout(self):
        """Handle logout and return to the login screen."""
        self.username = None
        self.greeting_label.clear()
        self.logout_button.setVisible(False)
        self.stack.setCurrentWidget(self.login_screen)

    def closeEvent(self, event):
        """Handle cleanup on application close."""
        try:
            self.client_socket.send("CHAT_EXIT".encode())
            self.client_socket.close()
            self.udp_socket.close()
        except Exception as e:
            print(f"Error during client disconnect: {e}")
        super().closeEvent(event)

    def apply_stylesheet(self):
        """Load and apply external stylesheet."""
        stylesheet_path = os.path.join(os.path.dirname(__file__), "stylesheet.qss")
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, "r") as file:
                self.setStyleSheet(file.read())
