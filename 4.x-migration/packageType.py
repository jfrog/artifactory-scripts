#!/usr/bin/python2
import sys
import base64
import StringIO
import xml.etree.ElementTree as ET
from PyQt4 import QtCore, QtGui, QtNetwork

class PackageTypeWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        # state constants
        self.Disconnected, self.Pending, self.Connected = 0, 1, 2
        # the xml file being modified
        self.repodata = None
        # the networking handler
        self.net = QtNetwork.QNetworkAccessManager()
        self.net.finished.connect(self.handleResponse)
        # the status bar
        self.status = self.statusBar()
        # create the window and populate it
        self.win = QtGui.QWidget(self)
        self.win.setLayout(self.buildUI())
        self.setCentralWidget(self.win)
        # set the current state
        self.stage = self.Disconnected
        # title, size, and show the window
        self.setWindowTitle("Artifactory Package Type Migration Tool")
        self.resize(800, 600)
        self.show()

    # return a layout containing the contents of the window
    def buildUI(self):
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.buildUrlBar())
        vbox.addLayout(self.buildTypeList())
        vbox.addLayout(self.buildButtonBar())
        return vbox

    # return a layout containing the contents of the url bar
    def buildUrlBar(self):
        self.urlEntry = QtGui.QLineEdit(self.win)
        self.userEntry = QtGui.QLineEdit(self.win)
        self.passEntry = QtGui.QLineEdit(self.win)
        self.passEntry.setEchoMode(QtGui.QLineEdit.Password)
        formbox = QtGui.QFormLayout()
        formbox.addRow("URL", self.urlEntry)
        formbox.addRow("Username", self.userEntry)
        formbox.addRow("Password", self.passEntry)
        return formbox

    # return a layout containing the repository type list box
    def buildTypeList(self):
        self.model = RepositoryListModel()
        self.typeList = QtGui.QTreeView(self.win)
        self.typeList.setModel(self.model)
        self.typeList.setItemDelegate(ComboBoxDelegate())
        self.typeList.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.typeList.header().setMovable(False)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.typeList)
        return hbox

    # return a layout containing the button bar
    def buildButtonBar(self):
        cancel = QtCore.QCoreApplication.instance().quit
        self.buttonConnect = QtGui.QPushButton("Connect", self.win)
        self.buttonConnect.clicked.connect(self.connectCallback)
        self.buttonConnect.setAutoDefault(True)
        self.buttonCancel = QtGui.QPushButton("Cancel", self.win)
        self.buttonCancel.clicked.connect(cancel)
        self.buttonSubmit = QtGui.QPushButton("Submit", self.win)
        self.buttonSubmit.clicked.connect(self.submitCallback)
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.buttonConnect)
        hbox.addWidget(self.buttonCancel)
        hbox.addWidget(self.buttonSubmit)
        return hbox

    # given a subpath, return a request object
    def getRequest(self, subpath):
        url = self.baseurl.resolved(QtCore.QUrl(subpath))
        if url.isRelative() or not url.isValid(): return None
        request = QtNetwork.QNetworkRequest(url)
        request.setRawHeader("Authorization", self.auth)
        return request

    # when the 'Connect' button is pressed
    def connectCallback(self, event):
        # if we are disconnected, connect
        if self.stage == self.Disconnected:
            # set the base url and auth data from the form fields
            self.baseurl = QtCore.QUrl(self.urlEntry.text())
            if not self.baseurl.path().endsWith("/"):
                self.baseurl.setPath(self.baseurl.path() + "/")
            userpass = self.userEntry.text() + ":" + self.passEntry.text()
            self.auth = "Basic " + base64.b64encode(unicode(userpass), "utf-8")
            # get a request for the config descriptor file
            request = self.getRequest("api/system/configuration")
            if request == None:
                self.status.showMessage("Error: Invalid URL", 3000)
                return
            # set the state appropriately
            self.stage = self.Pending
            msg = "Querying '" + request.url().toString() + "' ..."
            self.status.showMessage(msg)
            # send a get request
            self.net.get(request)
        # if we are connected, disconnect
        elif self.stage == self.Connected:
            # reset everything and set the state appropriately
            self.repodata = None
            self.model.table = {}
            self.stage = self.Disconnected
            self.status.showMessage("Disconnected successfully", 3000)

    # when the 'Submit' button is pressed
    def submitCallback(self, event):
        # get a list of changes that have been made to the repository data
        diff = self.model.diffTable()
        # if no changes were made, do nothing more
        if len(diff) < 1:
            diff = None
            self.status.showMessage("Nothing to do", 3000)
            return
        # get a request object to send the new config descriptor file
        request = self.getRequest("api/system/configuration")
        request.setRawHeader("Content-Type", "application/xml")
        # set the state appropriately
        self.stage = self.Pending
        msg = "Querying '" + request.url().toString() + "' ..."
        self.status.showMessage(msg)
        # get the xml data ready to modify
        root = self.repodata.getroot()
        ns = root.tag[:root.tag.index('}') + 1]
        layouts = self.model.layoutList
        # find the repos that are listed to have been modified
        for name in "local", "remote", "virtual":
            types = self.model.getPackTypes(name)
            for repo in root.iter(ns + name + "Repository"):
                key = repo.find(ns + "key")
                if key == None or key.text not in diff: continue
                # set the type and layout of each modified repo
                ptype = repo.find(ns + "type")
                layout = repo.find(ns + "repoLayoutRef")
                if ptype != None: ptype.text = types[diff[key.text][1]]
                if layout != None: layout.text = layouts[diff[key.text][2]]
        # create a file-like object and write the xml to it
        fobj = StringIO.StringIO()
        self.repodata.write(fobj)
        # send the resulting modified xml to the server
        self.net.post(request, fobj.getvalue())
        fobj.close()

    # extract the table data from the xml file
    def extractXmlData(self):
        layouts, data = [], {}
        # get the xml data ready to read
        root = self.repodata.getroot()
        ns = root.tag[:root.tag.index('}') + 1]
        # extract all the layout names from the file
        for layout in root.iter(ns + "repoLayout"):
            name = layout.find(ns + "name")
            if name != None: layouts.append(name.text)
        # iterate over all the repositories
        for name in "local", "remote", "virtual":
            types = self.model.getPackTypes(name)
            for repo in root.iter(ns + name + "Repository"):
                # extract the data from each repo entry
                key = repo.find(ns + "key")
                ptype = repo.find(ns + "type")
                layout = repo.find(ns + "repoLayoutRef")
                if key == None or ptype == None: return None
                if ptype.text not in types: return None
                rlayout = None
                # convert the type and layout strings to their index values
                if layout != None and layout.text in layouts:
                    rlayout = layouts.index(layout.text)
                elem = (name, types.index(ptype.text), rlayout)
                # save the final data set to the dict
                data[key.text] = elem
        # if no repositories were found, there may have been a problem
        if len(data) < 1: return None
        # save the list of layouts, and return the complete dict
        self.model.layoutList = layouts
        return data

    # when a response containing the config descriptor is recieved
    def getConfigCallback(self, reply):
        try:
            err = None
            xmlObj = None
            # if there was a network error, fail and print
            if reply.error() != QtNetwork.QNetworkReply.NoError:
                err = self.printNetworkError(reply)
            else:
                try:
                    # create a file-like object and read the xml from it
                    fobj = StringIO.StringIO(str(reply.readAll()))
                    xmlObj = ET.parse(fobj)
                    fobj.close()
                except IOError:
                    xmlObj = None
                    err = "Error: Invalid xml resource"
            if err == None:
                # if everything went fine, close the connection
                reply.close()
                self.repodata = xmlObj
                # extract the data from the xml object
                extractedData = self.extractXmlData()
                if extractedData != None:
                    # if the extraction succeeded, display the new data
                    self.model.table = extractedData
                    self.stage = self.Connected
                    rtc = QtGui.QHeaderView.ResizeToContents
                    self.typeList.header().resizeSections(rtc)
                    self.status.showMessage("Connected successfully", 3000)
                else:
                    # if the extraction failed, disconnect
                    self.repodata = None
                    err = "Error: Invalid or empty Artifactory config"
                    self.status.showMessage(err, 3000)
                    self.stage = self.Disconnected
            else:
                # abort and disconnect, something went wrong
                self.repodata = None
                reply.abort()
                if err == None: err = "Error: Response not valid"
                self.status.showMessage(err, 3000)
                self.stage = self.Disconnected
        except:
            self.repodata = None
            reply.abort()
            self.stage = self.Disconnected
            raise

    # when a response from the config descriptor update is recieved
    def postConfigCallback(self, reply):
        try:
            err = None
            if reply.error() != QtNetwork.QNetworkReply.NoError:
                # if there was a network error, fail and print
                err = self.printNetworkError(reply)
                reply.abort()
            else:
                # otherwise, print success
                err = "Configuration updated successfully"
                reply.close()
                # update the original model to match the new one
                self.model.orig = self.model.table.copy()
            self.status.showMessage(err, 3000)
            self.stage = self.Connected
        except:
            reply.abort()
            self.stage = self.Connected
            raise

    # when an http response is recieved
    def handleResponse(self, reply):
        # if the response calls for a redirect, do it
        attr = QtNetwork.QNetworkRequest.RedirectionTargetAttribute
        redirect = reply.attribute(attr).toUrl()
        if redirect.isValid():
            request = reply.request()
            request.setUrl(reply.url().resolved(redirect))
            self.net.createRequest(reply.operation(), request)
        elif reply.operation() == QtNetwork.QNetworkAccessManager.GetOperation:
            # if it's a response to a get, we're getting the descriptor
            self.getConfigCallback(reply)
        elif reply.operation() == QtNetwork.QNetworkAccessManager.PostOperation:
            # if it's a response to a post, we're posting the descriptor
            self.postConfigCallback(reply)

    # extract the network error information and print it to the status bar
    def printNetworkError(self, reply):
        statusAttr = QtNetwork.QNetworkRequest.HttpStatusCodeAttribute
        messageAttr = QtNetwork.QNetworkRequest.HttpReasonPhraseAttribute
        status = reply.attribute(statusAttr).toString()
        message = reply.attribute(messageAttr).toString()
        err = "Network Error: " + status + " '" + message + "'"
        self.status.showMessage(err, 3000)

    # stage getter
    def getStage(self):
        return self._stage

    # stage setter, also update ui appropriately
    def setStage(self, stage):
        if stage == self.Disconnected:
            self._stage = self.Disconnected
            self.urlEntry.setEnabled(True)
            self.userEntry.setEnabled(True)
            self.passEntry.setEnabled(True)
            self.typeList.setEnabled(False)
            self.typeList.setHeaderHidden(True)
            self.buttonConnect.setText("Connect")
            self.buttonConnect.setEnabled(True)
            self.buttonSubmit.setEnabled(False)
        elif stage == self.Pending:
            self._stage = self.Pending
            self.urlEntry.setEnabled(False)
            self.userEntry.setEnabled(False)
            self.passEntry.setEnabled(False)
            self.typeList.setEnabled(False)
            self.typeList.setHeaderHidden(True)
            self.buttonConnect.setEnabled(False)
            self.buttonConnect.setText("Working ...")
            self.buttonSubmit.setEnabled(False)
        elif stage == self.Connected:
            self._stage = self.Connected
            self.urlEntry.setEnabled(False)
            self.userEntry.setEnabled(False)
            self.passEntry.setEnabled(False)
            self.typeList.setEnabled(True)
            self.typeList.setHeaderHidden(False)
            self.buttonConnect.setText("Disconnect")
            self.buttonConnect.setEnabled(True)
            self.buttonSubmit.setEnabled(True)
        else:
            raise RuntimeError("Improper stage state")

    # connect the stage property to its getter and setter
    stage = property(getStage, setStage)

# allows the QTreeView to display data properly
class RepositoryListModel(QtCore.QAbstractItemModel):
    def __init__(self, parent = None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        # get the default size hint from a combo box
        # this is used to display rows of the proper height
        self.comboSize = QtGui.QComboBox().sizeHint()
        # _table contains the currently displayed data
        self._table = {}
        # orig contains the original data, so we can diff them later
        self.orig = {}
        # keys allows us to convert between table keys and indexes
        self.keys = []

    # overloaded, get a QModelIndex from a row, col, and parent
    def index(self, row, column, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return QtCore.QModelIndex()
        return self.createIndex(row, column, self.keys[row])

    # overloaded, get the parent index given a child index
    # this is always the root index, since it's just one layer
    def parent(self, child):
        return QtCore.QModelIndex()

    # overloaded, get the row count
    def rowCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._table)

    # overloaded, get the column count
    def columnCount(self, parent = QtCore.QModelIndex()):
        return 3

    # overloaded, get the value of an index in a given role
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        col, ptr = index.column(), index.internalPointer()
        # text to display in the table
        # ptr is the key, so show that if we're in the key column
        # otherwise, get the appropriate string given the index
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return ptr
            else:
                lst = None
                if col == 1: lst = self.getPackTypes(self._table[ptr][0])
                elif col == 2: lst = self.layoutList
                val = self._table[ptr][col]
                return "" if val == None else lst[val]
        # index of the combobox option to display
        elif role == QtCore.Qt.EditRole and col > 0:
            return self._table[ptr][col]
        # return the combobox size hint, so the rows will be big enough
        elif role == QtCore.Qt.SizeHintRole and col == self.columnCount() - 1:
            return self.comboSize
        return None

    # overloaded, return the displayed header string of a given column index
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation != QtCore.Qt.Horizontal or role != QtCore.Qt.DisplayRole:
            return None
        return ["Repository Key", "Package Type", "Layout"][section]

    # overloaded, set a given index to a specified value internally
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        col, ptr = index.column(), index.internalPointer()
        if role != QtCore.Qt.EditRole or col == 0:
            return False
        # convert the row to a list (tuples are immutable)
        data = list(self._table[ptr])
        # set the proper element
        data[col], _ = value.toInt()
        # convert back to a tuple and save the row
        self._table[ptr] = tuple(data)
        return True

    # overloaded, return flags for a given index
    def flags(self, index):
        val = self._table[index.internalPointer()][index.column()]
        # key names are not editable
        # null values are also not editable
        if index.column() > 0 and val != None:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsEnabled

    # given an index, return a list of available package types
    def getPackTypesList(self, index):
        if not index.isValid():
            return None
        ptr = index.internalPointer()
        return self.getPackTypes(self._table[ptr][0])

    # given a repo type, return a list of available package types
    def getPackTypes(self, repoType):
        # memoize these, they aren't going to change
        if not hasattr(self, "packTypesMap"):
            self.packTypesMap = {}
        if repoType in self.packTypesMap:
            return self.packTypesMap[repoType]
        # all the types that any repo can have
        types = ["bower", "gems", "gradle", "ivy", "maven", "npm", "nuget",
                 "pypi", "sbt"]
        # all the types that local repos can have
        if repoType == "local":
            types.extend(["debian", "docker", "gitlfs", "vagrant", "yum"])
        # all the types that remote repos can have
        elif repoType == "remote":
            types.extend(["debian", "docker", "p2", "vcs", "yum"])
        # all the types that virtual repos can have
        elif repoType == "virtual":
            types.extend(["p2"])
        else: raise ValueError("Incorrect package type: " + repoType)
        # sort them alphabetically and append generic to the end
        # this is how they are in the Artifactory ui
        types.sort()
        types.append("generic")
        self.packTypesMap[repoType] = types
        return types

    # list all the rows that have been modified
    def diffTable(self):
        diff = {}
        for key in self.keys:
            if self._table[key] != self.orig[key]:
                diff[key] = self._table[key]
        return diff

    # table getter
    def getTable(self):
        return self._table

    # table setter, also set orig and keys appropriately
    # also send reset signals so the QTreeView updates properly
    def setTable(self, tab):
        self.beginResetModel()
        self._table = tab.copy()
        self.orig = tab.copy()
        self.keys = tab.keys()
        self.endResetModel()

    # connect the table property to its getter and setter
    table = property(getTable, setTable)

# allows data to be modified properly in the QTreeView
class ComboBoxDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent = None):
        QtGui.QStyledItemDelegate.__init__(self, parent)

    # overloaded, create an editor widget for a given field
    def createEditor(self, parent, option, index):
        col, model = index.column(), index.model()
        if col == 0:
            par = QtGui.QStyledItemDelegate
            return par.createEditor(self, parent, option, index)
        # all of these are editable with a combobox
        widget = QtGui.QComboBox(parent)
        widget.setAutoFillBackground(True)
        widget.setFocusPolicy(QtCore.Qt.StrongFocus)
        # comboboxes need lists of items to display
        lst = None
        if col == 1: lst = model.getPackTypesList(index)
        elif col == 2: lst = model.layoutList
        widget.addItems(lst)
        return widget

    # overloaded, set an editor widget to display the data in a given index
    def setEditorData(self, editor, index):
        if index.column() == 0:
            return
        data, _ = index.data(QtCore.Qt.EditRole).toInt()
        editor.setCurrentIndex(data)

    # overloaded, modify the internal data to reflect the editor widget state
    def setModelData(self, editor, model, index):
        if index.column() == 0:
            return
        data = QtCore.QVariant(editor.currentIndex())
        model.setData(index, data)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = PackageTypeWindow()
    sys.exit(app.exec_())
