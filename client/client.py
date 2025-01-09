from PyQt6.QtWidgets import QApplication
from client_modules.main_window import MainWindow

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Load the stylesheet
    with open("client_modules/stylesheet.qss", "r") as file:
        app.setStyleSheet(file.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
