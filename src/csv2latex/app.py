import sys

from PyQt6.QtWidgets import QApplication

from .main_window import CSVToLatexConverter


def cli():
    app = QApplication(sys.argv)
    window = CSVToLatexConverter()
    window.show()
    sys.exit(app.exec())