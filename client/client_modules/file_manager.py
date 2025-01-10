import time

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QFileDialog,
    QInputDialog,
    QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal
import os


class FileManagerScreen(QWidget):
    switch_to_main_menu = pyqtSignal()

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

        # Layout
        self.layout = QVBoxLayout()

        # File Table
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(7)
        self.file_table.setHorizontalHeaderLabels(
            ["Name", "Description", "Date Uploaded", "Type", "Size", "Preview", "Download"]
        )
        self.layout.addWidget(self.file_table)

        # Upload Button
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_button)

        # Batch Download Button
        self.batch_download_button = QPushButton("Batch Download Files")
        self.batch_download_button.clicked.connect(self.batch_download)
        self.layout.addWidget(self.batch_download_button)

        # Buttons Layout
        self.buttons_layout = QHBoxLayout()

        # Refresh Button
        self.refresh_button = QPushButton("Refresh File List")
        self.refresh_button.clicked.connect(self.refresh_file_list)
        self.buttons_layout.addWidget(self.refresh_button)

        # Back Button
        self.back_button = QPushButton("Back to Main Menu")
        self.back_button.clicked.connect(self.switch_to_main_menu.emit)
        self.buttons_layout.addWidget(self.back_button)

        self.layout.addLayout(self.buttons_layout)
        self.setLayout(self.layout)
        self.refresh_file_list()

    def upload_file(self):
        """Upload a file to the server."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_path:
            description, ok = QInputDialog.getText(self, "File Description", "Enter a description for the file:")
            if not ok or not description.strip():
                return

            self.upload_thread = FileUploadThread(self.client_socket, file_path, description)
            self.upload_thread.file_uploaded.connect(self.append_to_table)
            self.upload_thread.start()

    def refresh_file_list(self):
        """Fetch the list of files from the server and update the table."""
        self.file_table.clearContents()  # Clear table content before refreshing
        self.refresh_thread = FileListRefreshThread(self.client_socket)
        self.refresh_thread.files_refreshed.connect(self.update_table)
        self.refresh_thread.start()

    def update_table(self, files):
        """Update the file table with the given files."""
        self.file_table.setRowCount(len(files))
        for row, file in enumerate(files):
            self.file_table.setItem(row, 0, QTableWidgetItem(file["name"]))
            self.file_table.setItem(row, 1, QTableWidgetItem(file["description"]))
            self.file_table.setItem(row, 2, QTableWidgetItem(file["date_uploaded"]))
            self.file_table.setItem(row, 3, QTableWidgetItem(file["type"]))
            self.file_table.setItem(row, 4, QTableWidgetItem(file["size"]))

            # Preview Button
            preview_button = QPushButton("Preview")
            preview_button.setStyleSheet("QPushButton { padding: 0px; font-size: 10px; }")  # Smaller font size and padding
            preview_button.clicked.connect(lambda _, f=file["name"]: self.preview_file(f))
            self.file_table.setCellWidget(row, 5, preview_button)

            # Download Button
            download_button = QPushButton("Download")
            download_button.setStyleSheet("QPushButton { padding: 0px; font-size: 10px; }")  # Smaller font size and padding
            download_button.clicked.connect(lambda _, f=file["name"]: self.download_file(f))
            self.file_table.setCellWidget(row, 6, download_button)

    def append_to_table(self, file_metadata):
        """Append a new file to the table."""
        row = self.file_table.rowCount()
        self.file_table.insertRow(row)

        self.file_table.setItem(row, 0, QTableWidgetItem(file_metadata["name"]))
        self.file_table.setItem(row, 1, QTableWidgetItem(file_metadata["description"]))
        self.file_table.setItem(row, 2, QTableWidgetItem(file_metadata["date_uploaded"]))
        self.file_table.setItem(row, 3, QTableWidgetItem(file_metadata["type"]))
        self.file_table.setItem(row, 4, QTableWidgetItem(file_metadata["size"]))

        # Preview Button
        preview_button = QPushButton("Preview")
        preview_button.clicked.connect(lambda _, f=file_metadata["name"]: self.preview_file(f))
        self.file_table.setCellWidget(row, 5, preview_button)

        # Download Button
        download_button = QPushButton("Download")
        download_button.clicked.connect(lambda _, f=file_metadata["name"]: self.download_file(f))
        self.file_table.setCellWidget(row, 6, download_button)

    def preview_file(self, filename):
        """Request a file preview from the server."""
        try:
            self.client_socket.send(f"PREVIEW_FILE:{filename}".encode("utf-8"))
            preview = self.client_socket.recv(1024).decode("utf-8")
            print(f"Preview of {filename}:\n{preview}")
        except Exception as e:
            print(f"Error previewing file: {e}")

    def download_file(self, filename):
        """Download a file from the server and allow the user to choose the save location."""
        try:
            self.client_socket.send(f"DOWNLOAD_FILE:{filename}".encode("utf-8"))
            file_data = self.client_socket.recv(1024 * 1024)

            if file_data.startswith(b"File not found"):
                print(file_data.decode("utf-8"))
            else:
                file_path, _ = QFileDialog.getSaveFileName(self, "Save File", filename)
                if file_path:
                    with open(file_path, "wb") as file:
                        file.write(file_data)
                    print(f"File '{filename}' downloaded successfully to {file_path}.")
        except Exception as e:
            print(f"Error downloading file: {e}")

    def batch_download(self):
        """Download all files from the server."""
        try:
            save_folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Files")
            if not save_folder:
                return

            start_time = time.time()

            self.client_socket.send("LIST_FILES".encode("utf-8"))
            response = self.client_socket.recv(1024 * 1024).decode("utf-8")

            for line in response.split("\n"):
                if line.strip() and "|" in line:
                    filename = line.split("|")[0]

                    self.client_socket.send(f"DOWNLOAD_FILE:{filename}".encode("utf-8"))
                    file_data = self.client_socket.recv(1024 * 1024)

                    with open(os.path.join(save_folder, filename), "wb") as file:
                        file.write(file_data)

            end_time = time.time()
            duration = round(end_time - start_time, 2)

            QMessageBox.information(self, "Batch Download Complete", f"All files downloaded in {duration} seconds.")
        except Exception as e:
            QMessageBox.critical(self, "Batch Download Error", f"An error occurred: {e}")


class FileListRefreshThread(QThread):
    files_refreshed = pyqtSignal(list)

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

    def run(self):
        files = []
        try:
            self.client_socket.send("LIST_FILES".encode("utf-8"))
            response = self.client_socket.recv(1024 * 1024).decode("utf-8")
            for line in response.split("\n"):
                if line.strip() and "|" in line:
                    try:
                        name, description, date_uploaded, file_type, size = line.split("|")
                        files.append(
                            {
                                "name": name,
                                "description": description,
                                "date_uploaded": date_uploaded,
                                "type": file_type,
                                "size": size,
                            }
                        )
                    except ValueError:
                        print(f"Skipping malformed entry: {line.strip()}")
        except Exception as e:
            print(f"Error refreshing file list: {e}")
        self.files_refreshed.emit(files)


class FileUploadThread(QThread):
    file_uploaded = pyqtSignal(dict)

    def __init__(self, client_socket, file_path, description):
        super().__init__()
        self.client_socket = client_socket
        self.file_path = file_path
        self.description = description

    def run(self):
        try:
            file_name = os.path.basename(self.file_path)
            with open(self.file_path, "rb") as file:
                file_data = file.read()

            self.client_socket.send(f"UPLOAD_FILE:{file_name}|{self.description}".encode("utf-8"))
            self.client_socket.send(file_data)
            response = self.client_socket.recv(1024).decode("utf-8")
            print(response)

            # Emit file metadata to append directly to the table
            file_metadata = {
                "name": file_name,
                "description": self.description,
                "date_uploaded": "Now",
                "type": file_name.split(".")[-1],
                "size": str(len(file_data)),
            }
            self.file_uploaded.emit(file_metadata)
        except Exception as e:
            print(f"Error uploading file: {e}")
