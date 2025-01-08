from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem
import socket
import os

class FileManagerScreen(QWidget):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.layout = QVBoxLayout()

        # Table for file listing
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(7)
        self.file_table.setHorizontalHeaderLabels(["Name","Description", "Date Uploaded", "Type", "Size", "Preview", "Download"])
        self.layout.addWidget(self.file_table)

        # Buttons
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_button)

        self.refresh_button = QPushButton("Refresh File List")
        self.refresh_button.clicked.connect(self.refresh_file_list)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)
        self.refresh_file_list()

    def refresh_file_list(self):
        """Fetch the list of files from the server and update the table."""
        try:
            self.client_socket.send("LIST_FILES".encode())
            response = self.client_socket.recv(1024 * 1024).decode()
            files = eval(response)  # Convert string to list of dictionaries

            self.file_table.setRowCount(len(files))
            for row, file in enumerate(files):
                self.file_table.setItem(row, 0, QTableWidgetItem(file["name"]))
                self.file_table.setItem(row, 1, QTableWidgetItem(file["description"]))
                self.file_table.setItem(row, 2, QTableWidgetItem(file["date_uploaded"]))
                self.file_table.setItem(row, 3, QTableWidgetItem(file["type"]))
                self.file_table.setItem(row, 4, QTableWidgetItem(file["size"]))

                # Preview button
                preview_button = QPushButton("Preview")
                preview_button.clicked.connect(lambda _, f=file["name"]: self.preview_file(f))
                self.file_table.setCellWidget(row, 5, preview_button)

                # Download button
                download_button = QPushButton("Download")
                download_button.clicked.connect(lambda _, f=file["name"]: self.download_file(f))
                self.file_table.setCellWidget(row, 6, download_button)
        except Exception as e:
            print(f"Error refreshing file list: {e}")

    def upload_file(self):
        """Upload a file to the server."""
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)", options=options)
            if file_path:
                description, ok = QFileDialog.getText(self, "File Description", "Enter a description for the file:")
                if not ok or not description.strip():
                    return

                file_name = os.path.basename(file_path)
                with open(file_path, "rb") as file:
                    file_data = file.read()

                self.client_socket.send(f"UPLOAD_FILE:{file_name}|{description}".encode())
                self.client_socket.send(file_data)
                response = self.client_socket.recv(1024).decode()
                print(response)
                self.refresh_file_list()
        except Exception as e:
            print(f"Error uploading file: {e}")

    def preview_file(self, filename):
        """Request a file preview from the server."""
        try:
            self.client_socket.send(f"PREVIEW_FILE:{filename}".encode())
            preview = self.client_socket.recv(1024).decode()
            print(f"Preview of {filename}:\n{preview}")
        except Exception as e:
            print(f"Error previewing file: {e}")

    def download_file(self, filename):
        """Download a file from the server."""
        try:
            self.client_socket.send(f"DOWNLOAD_FILE:{filename}".encode())
            file_data = self.client_socket.recv(1024 * 1024)  # Read the file data
            if file_data.startswith(b"File not found"):
                print(file_data.decode())
            else:
                with open(filename, "wb") as file:
                    file.write(file_data)
                print(f"File '{filename}' downloaded successfully.")
        except Exception as e:
            print(f"Error downloading file: {e}")
