#!/usr/bin/python

import sys
from PyQt4 import QtGui, uic
from core import vault
from core import config

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main.ui', self)
        self.config = config.load_config()
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

        # Load our settings if they were defined
        url = self.parent().config.get('VaultKee', 'url')
        token = self.parent().config.get('VaultKee', 'token')
        saved = self.parent().config.getboolean('VaultKee', 'save')
        if url:
            self.serverURLBox.addItems([url])
            self.serverURLBox.setCurrentIndex(1)
        if token:
            self.loginTokenBox.setText(token)
        if not saved:
            self.saveLoginCheckbox.setChecked(False)


    def ok_clicked(self):
        self.save_login = self.saveLoginCheckbox.isChecked()
        self.token = self.loginTokenBox.text()
        self.server_url = self.serverURLBox.currentText()
        self.parent().show()

        # Save our settings if requested
        if self.saveLoginCheckbox.checkState() > 0:
            config.save_config(self.server_url, self.token, True)
        else:
            config.save_config("", "", False)

        # Populate our main window with data from the server.
        mounts = vault.get_mounts(self.server_url, self.token)
        mounts_list = []
        for key in mounts:
            print key
            item = QtGui.QTreeWidgetItem()
            item.text = key
            mounts_list.append(item)
        self.parent().pathTreeWidget.addTopLevelItems(mounts_list)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.login_dialog.show()
    sys.exit(app.exec_())
