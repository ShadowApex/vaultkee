#!/usr/bin/python

import sys
from PyQt4 import QtGui, uic

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main.ui', self)
        self.login_dialog = Login(parent=self)

        # Populate the object viewer
        for column in range(3):
            for row in range(3):
                self.objectsViewer.setItem(row, column, QtGui.QTableWidgetItem("BOO"))  # your contents

class Login(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        uic.loadUi('login.ui', self)
        self.buttonBox.accepted.connect(self.ok_clicked)

    def ok_clicked(self):
        self.data = {}
        self.save_login = self.saveLoginCheckbox.isChecked()
        self.token = self.loginTokenBox.text()
        self.server_url = self.serverURLBox.currentText()
        self.parent().show()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()

    window.login_dialog.show()
    sys.exit(app.exec_())
