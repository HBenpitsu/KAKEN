# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class Widget(QWidget):
    def __init__(self,hor_size,ver_size):
        super(Widget, self).__init__()
        square_v=[True for _ in range(hor_size*ver_size)]
        ver_v=[True for _ in range(hor_size*ver_size-ver_size)]
        hor_v=[True for _ in range(hor_size*ver_size-hor_size)]
        self.load_ui()
    def toggle_button_color(self):
        pass
    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()


if __name__ == "__main__":
    app = QApplication([])
    widget = Widget(4,4)
    widget.show()
    sys.exit(app.exec_())
