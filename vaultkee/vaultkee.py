#!/usr/bin/python

import sys
from pprint import pprint
from PyQt4 import QtGui, uic
from core import vault
from core import config

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/main.ui', self)
        self.config = config.load_config()
        self.login_dialog = Login(parent=self)

        self.pathTreeWidget.clicked.connect(self.path_tree_clicked)
        self.selected_path = []

        # Populate the object viewer
        for column in range(3):
            for row in range(3):
                self.objectsViewer.setItem(row, column, QtGui.QTableWidgetItem("BOO"))  # your contents

    def path_tree_clicked(self):
        path_tree = self.pathTreeWidget
        self.selected_path = [str(path_tree.currentItem().text(0))]
        self.path_tree_parents(path_tree.currentItem())

        # Get all the items in this path from our listings dictionary
        self.listings = vault.get_listings(self.listing_url)
        objects = getFromDict(self.listings, self.selected_path[1:])

        # Update our table with available keys in the selected path.
        for item, value in objects.items():
            if not value:
                text = item[1:]
                self.objectsViewer.setItem(0, 0, QtGui.QTableWidgetItem(text))

    def path_tree_parents(self, item):
        parent = item.parent()
        if parent:
            self.selected_path.insert(0, str(parent.text(0)))
            self.path_tree_parents(parent)
            

class Login(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        uic.loadUi('ui/login.ui', self)
        self.buttonBox.accepted.connect(self.ok_clicked)

        # Load our settings if they were defined
        url = self.parent().config.get('VaultKee', 'url')
        listing_url = self.parent().config.get('VaultKee', 'listing_url')
        token = self.parent().config.get('VaultKee', 'token')
        saved = self.parent().config.getboolean('VaultKee', 'save')
        if url:
            self.serverURLBox.addItems([url])
            self.serverURLBox.setCurrentIndex(1)
        if listing_url:
            self.listingURLBox.addItems([listing_url])
            self.listingURLBox.setCurrentIndex(1)
        if token:
            self.loginTokenBox.setText(token)
        if not saved:
            self.saveLoginCheckbox.setChecked(False)


    def ok_clicked(self):
        self.save_login = self.saveLoginCheckbox.isChecked()
        self.token = self.loginTokenBox.text()
        self.server_url = self.serverURLBox.currentText()
        self.parent().listing_url = self.listingURLBox.currentText()
        self.parent().show()

        # Save our settings if requested
        if self.saveLoginCheckbox.checkState() > 0:
            config.save_config(self.server_url, self.parent().listing_url, self.token, True)
        else:
            config.save_config(self.server_url, self.parent().listing_url, "", False)

        # Populate our main window with data from the server.
        path_tree = self.parent().pathTreeWidget
        listings = vault.get_listings(self.parent().listing_url)
        mounts = vault.get_mounts(self.server_url, self.token)
        mounts_list = []
        for key in mounts:
            item = QtGui.QTreeWidgetItem()
            item.setText(0, key)

            # If this is the secrets mount, list all items found.
            if "secret" in key:
                build_paths_tree(listings, item)
                item.setExpanded(True)

            mounts_list.append(item)
        path_tree.addTopLevelItems(mounts_list)
        path_tree.expandAll()


def build_paths_tree(d, parent):
    for k, v in d.iteritems():
        child = QtGui.QTreeWidgetItem()
        child.setText(0, k)
        if v:
            parent.addChild(child)
        if isinstance(v, dict):
            build_paths_tree(v, child)

def getFromDict(dataDict, mapList):
    return reduce(lambda d, k: d[k], mapList, dataDict)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.login_dialog.show()
    sys.exit(app.exec_())
