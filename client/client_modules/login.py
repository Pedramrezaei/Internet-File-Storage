import socket

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import pyqtSignal

class LoginScreen(QWidget):
    switch_to_main = pyqtSignal()

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Password")
        self.layout.addWidget(self.password_input)

        # Status label for feedback
        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            self.status_label.setText("Username and password cannot be empty.")
            return

        try:
            # Clear any leftover data in the socket buffer
            self.client_socket.settimeout(1)
            try:
                while self.client_socket.recv(1024):
                    pass
            except socket.timeout:
                pass
            finally:
                self.client_socket.settimeout(None)

            # Send login request
            self.client_socket.sendall("LOGIN".encode("utf-8"))
            self.client_socket.sendall(f"{username}:{password}".encode("utf-8"))

            # Receive response
            response = self.client_socket.recv(1024).decode("utf-8")
            if response == "LOGIN_SUCCESS":
                self.switch_to_main.emit()
            else:
                self.status_label.setText(response)
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def register(self):
        """Handle user registration."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.status_label.setText("Username and password cannot be empty.")
            return

        try:
            # Send register request to server
            self.client_socket.sendall("REGISTER".encode())
            self.client_socket.sendall(f"{username}:{password}".encode())

            # Receive server response
            response = self.client_socket.recv(1024).decode()
            QMessageBox.information(self, "Registration Status", response)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
