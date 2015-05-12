#!/usr/bin/python

import sys
from pprint import pprint
from PyQt4 import QtGui, uic
from core import vault
from core import config

# Whether or not to cache all secrets for faster UI response.
SECRET_CACHING = False

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
        self.secret_dialog = Secret(parent=self)
        self.statusBar().showMessage('Ready')

        # Bind our actions such as exit, refresh, connect, etc.
        self.actionExit.triggered.connect(sys.exit)
        self.actionRefresh.triggered.connect(self.refresh)
        self.actionConnect.triggered.connect(self.login_dialog.show)
        self.actionAdd.triggered.connect(self.new_secret)
        self.actionRemove.triggered.connect(self.delete_secret)

        # Handle our path tree being selected.
        self.pathTreeWidget.clicked.connect(self.refresh_objects)
        pathTreeModel = self.pathTreeWidget.selectionModel()
        pathTreeModel.selectionChanged.connect(self.refresh_objects)
        self.selected_path = []

        # Handle our objects viewer being selected.
        objectsModel = self.objectsViewer.selectionModel()
        objectsModel.selectionChanged.connect(self.update_object_viewer)
        self.objectsViewer.doubleClicked.connect(self.edit_secret)
        self.objectsViewer.clicked.connect(self.update_object_viewer)

        # Handle our secret viewer being selected.
        self.secretTableWidget.doubleClicked.connect(self.update_secret_viewer_selection)


    def delete_secret(self):
        secret_name = self.get_secret_name_from_selection()
        secret_path = join_path(self.selected_path, secret_name)

        print "Deleting selected secret: %s" % secret_path
        vault.delete_secret(self.server_url, self.token, secret_path)
        self.refresh()


    def new_secret(self):
        self.secret_dialog.empty_table()
        self.secret_dialog.pathBox.setDisabled(0)
        self.secret_dialog.nameLineEdit.setDisabled(0)
        self.secret_dialog.show()


    def edit_secret(self):
        secret_viewer = self.secretTableWidget
        selected_row = secret_viewer.currentRow()
        selected_column = secret_viewer.currentColumn()

        # Fetch data about the selected secret
        secret_name = self.get_secret_name_from_selection()
        secret = self.fetch_secret(self.selected_path, secret_name)

        self.secret_dialog.populate_table(secret, self.selected_path, secret_name)
        self.secret_dialog.pathBox.setDisabled(1)
        self.secret_dialog.nameLineEdit.setDisabled(1)
        
        self.secret_dialog.show()


    def update_secret_viewer_selection(self):
        """If the user double clicks a field in the secret viewer, unmask it.
        """
        secret_viewer = self.secretTableWidget
        selected_row = secret_viewer.currentRow()
        selected_column = secret_viewer.currentColumn()

        # Fetch data about the selected secret
        secret_name = self.get_secret_name_from_selection()
        secret = self.fetch_secret(self.selected_path, secret_name)

        try:
            property_name = str(secret_viewer.item(selected_row, 0).text())
        except AttributeError:
            property_name = ""

        cb = QtGui.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(secret['data'][property_name], mode=cb.Clipboard)

        self.statusBar().showMessage('Copied %s to clipboard' % property_name)


    def update_object_viewer(self):
        """Updates the secret viewer on the bottom of the screen with details
        about the currently selected secret
        """
        secret_name = self.get_secret_name_from_selection()
        self.titleLabel.setText(secret_name)

        # Fetch data about the selected secret
        secret = self.fetch_secret(self.selected_path, secret_name)
        if 'data' not in secret:
            return

        # Populate our secret viewer in the bottom of the main window.
        unhide_data = ("comment", "url", "ip")
        self.secretTableWidget.setRowCount(len(secret['data'].keys()))
        i = 0
        for key, value in secret['data'].items():
            # Set the key
            self.secretTableWidget.setItem(i, 0, QtGui.QTableWidgetItem(key))

            # Set the value if it's not sensitive data.
            if key.lower() in unhide_data:
                self.secretTableWidget.setItem(i, 1, QtGui.QTableWidgetItem(value))
            else:
                self.secretTableWidget.setItem(i, 1, QtGui.QTableWidgetItem("***************"))

            i += 1

        self.secretTableWidget.resizeColumnsToContents()


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
        if not objects:
            return

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

        self.objectsViewer.resizeColumnsToContents()


    def path_tree_parents(self, tree_widget):
        """Updates the 'self.selected_path' attribute with the given item's
        parents.

        Args:
          item (QtGui.QTreeWidgetItem): A tree widget item to get the parents of.

        """
        parent = tree_widget.parent()
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


    def fetch_secret(self, selected_path, item):
        """Fetches a single secret from vault given the currently selected path and
        secret name.

        Args:
          selected_path (list): Top-level path to the secret, e.g. ['secret', 'servers']
          item (str): The name of the secret to fetch, e.g. "web01"

        Returns:
          A dictionary of the fetched secret.

        """
        # Fetch data about the selected secret
        item_path = join_path(selected_path, item)

        if SECRET_CACHING:
            secret = self.secrets[item_path]
        else:
            secret = vault.read_secret(self.server_url, self.token, item_path)

        return secret


    def get_secret_name_from_selection(self):
        """Gets the name of the secret selected in the objects viewer.
        """
        objects_viewer = self.objectsViewer
        selected_row = objects_viewer.currentRow()
        selected_column = objects_viewer.currentColumn()

        try:
            secret_name = objects_viewer.item(selected_column, selected_row).text()
        except AttributeError:
            secret_name = ""

        # If our secret name is blank, remove all our rows from our secret viewer.
        if not secret_name:
            self.secretTableWidget.setRowCount(0)

        return secret_name


    def refresh(self):
        if SECRET_CACHING:
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
        if SECRET_CACHING:
            parent.fetch_secrets()

        # Populate our main window with data from the server.
        populate_path_tree(parent.pathTreeWidget,
                           parent.listing_url,
                           parent.server_url,
                           parent.token)
        parent.secret_dialog.populate_paths()


class Secret(QtGui.QDialog):
    """The dialog used to add or modify secrets

    Args:
      parent (QtGui.QMainWindow): Parent of this window.

    """
    def __init__(self, parent=None):
        super(Secret, self).__init__(parent)
        uic.loadUi('ui/secret.ui', self)

        self.addButton.clicked.connect(self.add_row)
        self.buttonBox.accepted.connect(self.save_selected)


    def add_row(self):
        table = self.tableWidget
        table.setRowCount(table.rowCount() + 1)


    def save_selected(self):
        parent = self.parent()
        print "Save clicked!"

        # Only save if we validate our input
        if not self.valid_input():
            print "Error, input is invalid"
            return False

        # Format our data for saving
        data = {}
        for row in range(self.tableWidget.rowCount()):
            try:
                key = str(self.tableWidget.item(row, 0).text())
            except AttributeError:
                continue
            try:
                value = str(self.tableWidget.item(row, 1).text())
            except AttributeError:
                value = ""
            data[key] = value

        pprint(data)

        # Get our path to save the data to
        secret_name = str(self.nameLineEdit.text())
        secret_path = str(self.pathBox.currentText())

        save_path = join_path([secret_path], secret_name)
        print "Saving %s to %s." % (data, save_path)

        # Write our secret to the specified path
        vault.write_secret(parent.server_url, parent.token, save_path, data)

        # Update our tree view
        populate_path_tree(parent.pathTreeWidget,
                           parent.listing_url,
                           parent.server_url,
                           parent.token)

        parent.refresh()


    def valid_input(self):
        secret_name = self.nameLineEdit.text()
        secret_path = self.pathBox.currentText()

        if not secret_name or not secret_path:
            return False

        if self.tableWidget.rowCount() < 1:
            return False

        for row in range(self.tableWidget.rowCount()):
            try:
                key = str(self.tableWidget.item(row, 0).text())
            except AttributeError:
                key = ""
            try:
                value = str(self.tableWidget.item(row, 1).text())
            except AttributeError:
                value = ""

            if not key and value:
                return False

        return True


    def populate_paths(self):
        parent = self.parent()
        listings = vault.get_listings(parent.config.get('VaultKee',
                                                        'listing_url'))
        if not listings:
            return
        for key in listings:
            if listings[key]:
                self.pathBox.addItems(['secret/' + key])


    def empty_table(self):
        table = self.tableWidget
        table.setRowCount(0)
        table.setRowCount(1)
        self.nameLineEdit.setText("")


    def populate_table(self, secret, secret_path, secret_name):
        table = self.tableWidget
        table.setRowCount(len(secret['data']))

        i = 0
        for key, value in secret['data'].items():
            table.setItem(i, 0, QtGui.QTableWidgetItem(key))
            table.setItem(i, 1, QtGui.QTableWidgetItem(value))
            i += 1

        # Get all the currently available paths
        current_items = [self.pathBox.itemText(i) for i in range(self.pathBox.count())]

        # Get the string path of the current item
        secret_path = join_path(secret_path, "")
        if secret_path.endswith('/'):
            secret_path = secret_path[:-1]

        # Loop through our current items and set our path
        i = 0
        path_found = False
        for item in current_items:
            if str(item) == secret_path:
                path_found = True
                self.pathBox.setCurrentIndex(i)
            i += 1
        if not path_found:
            self.pathBox.addItems([secret_path])
            self.pathBox.setCurrentIndex(len(current_items))

        self.nameLineEdit.setText(secret_name)


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

def join_path(selected_path, path):
    """Combines a list of paths to a single '/' separated string.
    """
    item_path = '/'.join(selected_path) + '/' + str(path)
    item_path = item_path.replace('//', '/')

    return item_path



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
    if not d:
        return
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
