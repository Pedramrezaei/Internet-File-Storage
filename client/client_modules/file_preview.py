from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl

class FilePreviewWindow(QDialog):
    def __init__(self, filename, content):
        super().__init__()
        self.setWindowTitle(f"Preview: {filename}")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Clear any old content in the window
        self.setLayout(layout)

        if isinstance(content, str):  # For text files
            text_preview = QTextEdit()
            text_preview.setText(content)
            text_preview.setReadOnly(True)
            layout.addWidget(text_preview)

        elif isinstance(content, QPixmap):  # For image files (e.g., PNG, JPEG)
            image_label = QLabel()
            if not content.isNull():  # Check if the pixmap is loaded correctly
                image_label.setPixmap(content)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                image_label.setText("Failed to load image.")
            layout.addWidget(image_label)

        elif isinstance(content, str) and content.endswith(('.mp4', '.avi', '.mov')):  # For video files
            video_widget = QVideoWidget(self)
            media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
            media_player.setVideoOutput(video_widget)

            # Set video source directly for the file
            media_player.setSource(QUrl.fromLocalFile(content))  # Ensure it's a valid file path
            media_player.play()

            layout.addWidget(video_widget)

        else:
            label = QLabel("Preview not available for this file type.")
            layout.addWidget(label)

        self.setLayout(layout)
