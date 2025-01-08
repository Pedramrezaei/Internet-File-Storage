from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt
from .login import LoginScreen
from .main_menu import MainMenuScreen
from .chat import ChatScreen
from .file_manager import FileManagerScreen
import socket
from .constants import HOST, TCP_PORT, UDP_PORT


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.username = None
        self.setWindowTitle("Chat Client")
        self.setGeometry(200, 200, 600, 400)

        # Central widget and layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # Top bar for the greeting
        self.top_bar_layout = QHBoxLayout()
        self.greeting_label = QLabel("")
        self.greeting_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.top_bar_layout.addWidget(self.greeting_label)
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
        self.chat_screen = None  # Initialize chat screen dynamically
        self.file_manager_screen = FileManagerScreen(self.client_socket)  # File manager screen

        # Connect signals
        self.login_screen.switch_to_main.connect(self.show_main_menu)
        self.main_menu_screen.switch_to_chat.connect(self.show_chat)
        self.main_menu_screen.switch_to_file_manager.connect(self.show_file_manager)  # Connect file manager

        # Add screens to stack
        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.main_menu_screen)
        self.stack.addWidget(self.file_manager_screen)
        self.stack.setCurrentWidget(self.login_screen)

    def show_main_menu(self):
        """Switch to the main menu screen."""
        self.username = self.login_screen.username_input.text()
        self.update_greeting()
        self.stack.setCurrentWidget(self.main_menu_screen)

    def show_chat(self):
        """Switch to the chat screen."""
        if self.chat_screen is None:  # Create the chat screen only once
            self.chat_screen = ChatScreen(self.udp_socket, self.username)
            self.chat_screen.switch_to_main_menu.connect(self.show_main_menu)
            self.stack.addWidget(self.chat_screen)

        self.chat_screen.username = self.username
        self.chat_screen.send_username_to_server()
        self.stack.setCurrentWidget(self.chat_screen)

    def show_file_manager(self):
        """Switch to the file manager screen."""
        self.stack.setCurrentWidget(self.file_manager_screen)

    def update_greeting(self):
        """Update the greeting label with the signed-in username."""
        if self.username:
            self.greeting_label.setText(f"Hi, {self.username}")
        else:
            self.greeting_label.clear()

    def closeEvent(self, event):
        """Handle cleanup on application close."""
        try:
            self.client_socket.send("CHAT_EXIT".encode())
            self.client_socket.close()
            self.udp_socket.close()
        except Exception as e:
            print(f"Error during client disconnect: {e}")
        super().closeEvent(event)
