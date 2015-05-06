#!/usr/bin/python

import sys
from pprint import pprint
from PyQt4 import QtGui, uic
from core import vault
from core import config

class MainWindow(QtGui.QMainWindow):
    """The main window to display after connecting to a Vault server.

    Args:
      None

    """
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/main.ui', self)
        self.config = config.load_config()
        self.login_dialog = Login(parent=self)
        self.statusBar().showMessage('Ready')

        # Bind our actions
        self.actionExit.triggered.connect(sys.exit)
        self.actionRefresh.triggered.connect(self.refresh)
        self.actionConnect.triggered.connect(self.login_dialog.show)

        # Handle our path tree being selected.
        self.pathTreeWidget.clicked.connect(self.refresh_objects)
        pathTreeModel = self.pathTreeWidget.selectionModel()
        pathTreeModel.selectionChanged.connect(self.refresh_objects)
        self.selected_path = []

        # Handle our objects viewer being selected.
        objectsModel = self.objectsViewer.selectionModel()
        objectsModel.selectionChanged.connect(self.update_object_viewer)


    def update_object_viewer(self):
        objects_viewer = self.objectsViewer
        selected_row = objects_viewer.currentRow()
        selected_column = objects_viewer.currentColumn()
        #print selected_row
        #print dir(objects_viewer)


    def refresh_objects(self):
        """Refreshes the objects viewer table.
        """
        path_tree = self.pathTreeWidget
        if not path_tree.currentItem():
            return
        self.selected_path = [str(path_tree.currentItem().text(0))]
        self.path_tree_parents(path_tree.currentItem())

        # Get all the items in this path from our listings dictionary
        self.listings = vault.get_listings(self.listing_url)
        objects = getFromDict(self.listings, self.selected_path[1:])

        # Update our table with available keys in the selected path.
        available_items = []
        for item, value in objects.items():
            if not value:
                available_items.append(item)
        self.objectsViewer.setRowCount(len(available_items))

        for i, item in enumerate(available_items):
            item_path = '/'.join(self.selected_path) + '/' + item[1:]
            item_path = item_path.replace('//', '/')
            text = item[1:]
            self.objectsViewer.setItem(i, 0, QtGui.QTableWidgetItem(text))

            # Fetch some data about the available secrets.
            secret = self.secrets[item_path]
            if 'username' in secret['data']:
                self.objectsViewer.setItem(i, 1, QtGui.QTableWidgetItem(secret['data']['username']))
            if 'url' in secret['data']:
                self.objectsViewer.setItem(i, 2, QtGui.QTableWidgetItem(secret['data']['url']))
            if 'password' in secret['data']:
                self.objectsViewer.setItem(i, 3, QtGui.QTableWidgetItem("***************"))
            if 'comment' in secret['data']:
                self.objectsViewer.setItem(i, 4, QtGui.QTableWidgetItem(secret['data']['comment']))

        self.objectsViewer.resizeColumnsToContents()


    def path_tree_parents(self, item):
        """Updates the 'self.selected_path' attribute with the given item's
        parents.

        Args:
          item (QtGui.QTreeWidgetItem): A tree widget item to get the parents of.

        """
        parent = item.parent()
        if parent:
            self.selected_path.insert(0, str(parent.text(0)))
            self.path_tree_parents(parent)


    def fetch_secrets(self):
        """Fetches all secrets from the vault server.
        """
        self.statusBar().showMessage('Refreshing...')
        self.listings = vault.get_listings(self.listing_url)
        self.flat_listings = []
        self.secrets = {}
        items = extract(self.listings, {})
        for key in items:
            secret_path = find_key(self.listings, key)
            secret_path[-1] = secret_path[-1][1:]
            secret_path.insert(0, 'secret')
            secret_path = '/'.join(secret_path)
            self.flat_listings.append(secret_path)

        for item in self.flat_listings:
            secret = vault.read_secret(self.server_url, self.token, item)
            self.secrets[item] = secret

        self.statusBar().showMessage('Ready')


    def refresh(self):
        self.fetch_secrets()
        self.refresh_objects()


class Login(QtGui.QDialog):
    """The dialog used to log in to the Vault server.

    Args:
      parent (QtGui.QMainWindow): Parent of this window.

    """
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        uic.loadUi('ui/login.ui', self)
        self.buttonBox.accepted.connect(self.ok_selected)

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


    def ok_selected(self):
        """Executes when the OK button is selected.

        Args:
          None

        """
        parent = self.parent()
        self.save_login = self.saveLoginCheckbox.isChecked()
        parent.token = self.loginTokenBox.text()
        parent.server_url = self.serverURLBox.currentText()
        parent.listing_url = self.listingURLBox.currentText()
        parent.show()

        # Save our settings if requested
        if self.saveLoginCheckbox.checkState() > 0:
            config.save_config(parent.server_url, parent.listing_url, parent.token, True)
        else:
            config.save_config(parent.server_url, parent.listing_url, "", False)

        # Load all our secrets
        parent.fetch_secrets()

        # Populate our main window with data from the server.
        populate_path_tree(parent.pathTreeWidget,
                           parent.listing_url,
                           parent.server_url,
                           parent.token)


def extract(dict_in, dict_out):
    for key, value in dict_in.iteritems():
        if isinstance(value, dict): # If value itself is dictionary
            extract(value, dict_out)
        else:
            # Write to dict_out
            dict_out[key] = value
    return dict_out


def find_key(d, key):
    for k,v in d.items():
        if isinstance(v,dict):
            p = find_key(v,key)
            if p:
                return [k] + p
        elif k == key:
            return [k]



def populate_path_tree(path_tree, listing_url, server_url, token):
    """Populates a QTreeWidget with the paths from the listing server.

    Args:
      path_tree (QtGui.QTreeWidget): The path tree widget to populate.
      listing_url (str): URL of the listing server that will return the
        available secrets we can query.
      server_url (str): URL of the vault server to connect to.
      token (str): Authentication token for vault server.

    """
    listings = vault.get_listings(listing_url)
    mounts = vault.get_mounts(server_url, token)
    mounts_list = []
    for key in mounts:
        # Don't display the sys/ mount.
        if key == "sys/":
            continue

        item = QtGui.QTreeWidgetItem()
        item.setText(0, key)
        # If this is the secrets mount, list all items found.
        if "secret" in key:
            build_paths_tree(listings, item)

        mounts_list.append(item)
    path_tree.clear()
    path_tree.addTopLevelItems(mounts_list)
    path_tree.expandAll()


def build_paths_tree(d, parent):
    """Builds the directory path using Qt's TreeWidget items.

    Args:
      d (dict): A nested dictionary of file paths to construct our QTreeWidget.
      parent (QtGui.QTreeWidgetItem): The top-level parent of the path tree.

    """
    for k, v in d.iteritems():
        child = QtGui.QTreeWidgetItem()
        child.setText(0, k)
        if v:
            parent.addChild(child)
        if isinstance(v, dict):
            build_paths_tree(v, child)


def getFromDict(dataDict, mapList):
    """Look up an entry in a nested dictionary given the list of keys.

    Args:
      dataDict (dict): 
      mapList (list): List of keys to get.

    Returns:
      The value in the dictionary.

    Example:
      Say we have a nested dictionary like this:

      >>> mydict
      {
        'a': {
           'b': 5
        }
      }

      To get the value "5" in this example, we can do this:

      >>> getFromDict(mydict, ['a', 'b'])
      5

    """
    return reduce(lambda d, k: d[k], mapList, dataDict)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.login_dialog.show()
    sys.exit(app.exec_())
