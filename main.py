import sys
from PyQt5 import QtWidgets
from Vista.login import Login

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    windows = Login()
    app.exec()