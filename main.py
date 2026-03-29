from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    app = QApplication([])
    window = MainWindow()
    window.resize(900, 650)
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
