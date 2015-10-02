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
        self.net = QtNetwork.QNetworkAccessManager(self)
        self.net.finished.connect(self.handleResponse)
        # the status bar
        self.status = self.statusBar()
        self.progress = QtGui.QProgressBar(self)
        self.progress.hide()
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
        self.model = RepositoryListModel(self.win)
        self.filtermodel = MavenFilterModel(self.win)
        self.filtermodel.setSourceModel(self.model)
        self.typeList = QtGui.QTreeView(self.win)
        self.typeList.setSortingEnabled(True)
        self.typeList.setModel(self.filtermodel)
        self.typeList.setItemDelegate(ComboBoxDelegate(self.typeList))
        self.typeList.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.typeList.header().setMovable(False)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.typeList)
        return hbox

    # return a layout containing the button bar
    def buildButtonBar(self):
        def toggleFilterCallback(event):
            self.filtermodel.mavenOnly = event != 0
            self.filtermodel.invalidateFilter()
        self.toggleFilter = QtGui.QCheckBox("Maven Only", self.win)
        self.toggleFilter.stateChanged.connect(toggleFilterCallback)
        self.buttonExport = QtGui.QPushButton("Export", self.win)
        tooltip = "Export repositories with non-default layouts"
        self.buttonExport.setToolTip(tooltip)
        self.buttonExport.clicked.connect(self.exportCallback)
        self.buttonConnect = QtGui.QPushButton("Connect", self.win)
        self.buttonConnect.clicked.connect(self.connectCallback)
        self.buttonQuit = QtGui.QPushButton("Quit", self.win)
        self.buttonQuit.clicked.connect(self.quitCallback)
        self.buttonSave = QtGui.QPushButton("Save", self.win)
        self.buttonSave.clicked.connect(self.saveCallback)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.toggleFilter)
        hbox.addStretch(1)
        hbox.addWidget(self.buttonExport)
        hbox.addWidget(self.buttonConnect)
        hbox.addWidget(self.buttonQuit)
        hbox.addWidget(self.buttonSave)
        return hbox

    # given a subpath, return a request object
    def getRequest(self, subpath):
        url = self.baseurl.resolved(QtCore.QUrl(subpath))
        if url.isRelative() or not url.isValid(): return None
        request = QtNetwork.QNetworkRequest(url)
        request.setRawHeader("Authorization", self.auth)
        return request

    # when the 'Export' button is pressed
    def exportCallback(self, event):
        table = []
        # gather every line in the table with a non-default layout
        for repo in self.model.table:
            line = self.model.table[repo]
            if line[3] == None: continue
            ptype = self.model.getPackTypes(line[1])[line[2]]
            layout = self.model.layoutList[line[3]]
            layouts = self.model.deflayouts
            if layout not in layouts or (layout in layouts
                and ptype not in layouts[layout]):
                newlayout = None
                # find the default layout for each package type
                for lt in layouts:
                    if ptype in layouts[lt]:
                        newlayout = lt
                        break
                table.append((repo, ptype, layout, newlayout))
        # if the entire table has default layouts, don't do anything
        if len(table) <= 0:
            self.status.showMessage("Nothing to export", 3000)
            return
        # get a file to export to
        title = "Export Repositories with Non-Default Layouts"
        fname = QtGui.QFileDialog.getSaveFileName(self.win, title)
        # save to the file
        try:
            with open(fname, 'w') as f:
                for line in table:
                    ln = line[0] + " (" + line[1] + "): layout is "
                    ln += line[2] + ", default is " + line[3] + "\n"
                    f.write(ln)
            self.status.showMessage("Exported successfully", 3000)
        except IOError as ex: self.status.showMessage(str(ex), 3000)

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
            response = self.net.get(request)
            response.error.connect(self.handleNetError)
            response.downloadProgress.connect(self.handleProgress)
        # if we are connected, disconnect
        elif self.stage == self.Connected:
            # get a list of changes that have been made to the repository data
            diff = self.model.diffTable()
            # if changes were made, ask to discard
            if len(diff) > 0:
                txt = "Unsaved changes will be discarded. Really disconnect?"
                msg = QtGui.QMessageBox(self.win)
                msg.setWindowTitle("Warning: Unsaved Changes")
                msg.setText("Warning: Unsaved Changes")
                msg.setInformativeText(txt)
                msg.setIcon(QtGui.QMessageBox.Warning)
                msg.addButton(QtGui.QMessageBox.Ok)
                msg.addButton(QtGui.QMessageBox.Cancel)
                if msg.exec_() == QtGui.QMessageBox.Cancel: return
            # reset everything and set the state appropriately
            self.repodata = None
            self.model.table = {}
            self.stage = self.Disconnected
            self.status.showMessage("Disconnected successfully", 3000)

    # when the 'Save' button is pressed
    def saveCallback(self, event):
        # get a list of changes that have been made to the repository data
        diff = self.model.diffTable()
        # if no changes were made, do nothing more
        if len(diff) < 1:
            self.status.showMessage("Nothing to do", 3000)
            return
        # ask to overwrite Artifactory configuration
        txt = "Any changes made to the Artifactory system configuration while"
        txt += " this tool has been connected will be overwritten! Save anyway?"
        msg = QtGui.QMessageBox(self.win)
        msg.setWindowTitle("Warning")
        msg.setText("Warning")
        msg.setInformativeText(txt)
        msg.setIcon(QtGui.QMessageBox.Warning)
        msg.addButton(QtGui.QMessageBox.Ok)
        msg.addButton(QtGui.QMessageBox.Cancel)
        if msg.exec_() == QtGui.QMessageBox.Cancel: return
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
                if ptype != None: ptype.text = types[diff[key.text][2]]
                if layout != None: layout.text = layouts[diff[key.text][3]]
        # create a file-like object and write the xml to it
        fobj = StringIO.StringIO()
        self.repodata.write(fobj)
        # send the resulting modified xml to the server
        response = self.net.post(request, fobj.getvalue())
        response.error.connect(self.handleNetError)
        response.uploadProgress.connect(self.handleProgress)
        fobj.close()

    # when the 'Quit' button is pressed
    def quitCallback(self, event):
        # get a list of changes that have been made to the repository data
        diff = self.model.diffTable()
        # if changes were made, ask to discard
        if self.stage == self.Connected and len(diff) > 0:
            txt = "Unsaved changes will be discarded. Really quit?"
            msg = QtGui.QMessageBox(self.win)
            msg.setWindowTitle("Warning: Unsaved Changes")
            msg.setText("Warning: Unsaved Changes")
            msg.setInformativeText(txt)
            msg.setIcon(QtGui.QMessageBox.Warning)
            msg.addButton(QtGui.QMessageBox.Ok)
            msg.addButton(QtGui.QMessageBox.Cancel)
            if msg.exec_() == QtGui.QMessageBox.Cancel: return
        # quit the tool
        QtCore.QCoreApplication.instance().quit()

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
        layouts.sort()
        # iterate over all the repositories
        for name in "local", "remote", "virtual":
            types = self.model.getPackTypes(name)
            for repo in root.iter(ns + name + "Repository"):
                # extract the data from each repo entry
                key = repo.find(ns + "key")
                ptype = repo.find(ns + "type")
                descr = repo.find(ns + "description")
                layout = repo.find(ns + "repoLayoutRef")
                if key == None or ptype == None: return None
                if ptype.text not in types: return None
                # get the description, if one exists
                rdescr = None
                if descr != None and len(descr.text) > 0:
                    rdescr = descr.text
                # convert the type and layout strings to their index values
                rlayout = None
                if layout != None and layout.text in layouts:
                    rlayout = layouts.index(layout.text)
                rtype = types.index(ptype.text)
                elem = (rdescr, name, rtype, rlayout)
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
                if xmlObj == None:
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
                self.status.showMessage(err, 3000)
                self.stage = self.Connected
            else:
                # otherwise, print success
                err = "Configuration updated successfully"
                reply.close()
                self.status.showMessage(err, 3000)
                # send a get request for the config descriptor file again
                request = self.getRequest("api/system/configuration")
                response = self.net.get(request)
                response.error.connect(self.handleNetError)
                response.downloadProgress.connect(self.handleProgress)
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
            response = self.net.createRequest(reply.operation(), request)
            response.error.connect(self.handleNetError)
            post = QtNetwork.QNetworkAccessManager.PostOperation
            if reply.operation() == post:
                response.uploadProgress.connect(self.handleProgress)
            else:
                response.downloadProgress.connect(self.handleProgress)
        elif reply.operation() == QtNetwork.QNetworkAccessManager.GetOperation:
            # if it's a response to a get, we're getting the descriptor
            self.getConfigCallback(reply)
        elif reply.operation() == QtNetwork.QNetworkAccessManager.PostOperation:
            # if it's a response to a post, we're posting the descriptor
            self.postConfigCallback(reply)
        else: raise RuntimeError("Unanticipated HTTP response")

    # extract the network error information and print it to the status bar
    def printNetworkError(self, reply):
        statusAttr = QtNetwork.QNetworkRequest.HttpStatusCodeAttribute
        messageAttr = QtNetwork.QNetworkRequest.HttpReasonPhraseAttribute
        status = reply.attribute(statusAttr).toString()
        message = reply.attribute(messageAttr).toString()
        return "Network Error: " + status + " '" + message + "'"

    # if a network error occurs, print it somwhere
    def handleNetError(self, error):
        raise RuntimeError("Network Error: " + str(error))

    # when progress is made in the download/upload, update the progress bar
    def handleProgress(self, recvd, total):
        if total < 0:
            if self.progress.maximum() != 0: self.progress.setMaximum(0)
        else:
            if self.progress.maximum() != 100: self.progress.setMaximum(100)
            self.progress.setValue((100*recvd)/total)

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
            self.buttonExport.setEnabled(False)
            self.buttonConnect.setText("Connect")
            self.buttonConnect.setEnabled(True)
            self.buttonSave.setEnabled(False)
            self.status.removeWidget(self.progress)
        elif stage == self.Pending:
            self._stage = self.Pending
            self.urlEntry.setEnabled(False)
            self.userEntry.setEnabled(False)
            self.passEntry.setEnabled(False)
            self.typeList.setEnabled(False)
            self.typeList.setHeaderHidden(True)
            self.buttonExport.setEnabled(False)
            self.buttonConnect.setEnabled(False)
            self.buttonConnect.setText("Working ...")
            self.buttonSave.setEnabled(False)
            self.progress.reset()
            self.progress.setRange(0, 0)
            self.status.addPermanentWidget(self.progress)
            self.progress.show()
        elif stage == self.Connected:
            self._stage = self.Connected
            self.urlEntry.setEnabled(False)
            self.userEntry.setEnabled(False)
            self.passEntry.setEnabled(False)
            self.typeList.setEnabled(True)
            self.typeList.setHeaderHidden(False)
            self.buttonExport.setEnabled(True)
            self.buttonConnect.setText("Disconnect")
            self.buttonConnect.setEnabled(True)
            self.buttonSave.setEnabled(True)
            self.status.removeWidget(self.progress)
        else: raise RuntimeError("Improper stage state")

    # connect the stage property to its getter and setter
    stage = property(getStage, setStage)

# allows the QTreeView to display data properly
class RepositoryListModel(QtCore.QAbstractItemModel):
    def __init__(self, parent = None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        # get the default size hint from a combo box
        # this is used to display rows of the proper height
        self.comboSize = QtGui.QComboBox().sizeHint()
        # list of default layout and package type pairs
        self.deflayouts = {
            "bower-default": ["bower"], "gradle-default": ["gradle"],
            "ivy-default": ["ivy"], "maven-1-default": ["maven"],
            "maven-2-default": ["maven"], "npm-default": ["npm"],
            "nuget-default": ["nuget"], "sbt-default": ["sbt"],
            "vcs-default": ["vcs"], "simple-default": [
                "generic", "debian", "docker", "gems", "gitlfs",
                "pypi", "vagrant", "yum", "p2"]}
        # _table contains the currently displayed data
        self._table = {}
        # orig contains the original data, so we can diff them later
        self.orig = {}
        # keys allows us to convert between table keys and indexes
        self.keys = []

    # overload: get a QModelIndex from a row, col, and parent
    def index(self, row, column, parent = QtCore.QModelIndex()):
        if parent.isValid(): return QtCore.QModelIndex()
        return self.createIndex(row, column, self.keys[row])

    # overload: get the parent index given a child index
    # this is always the root index, since it's just one layer
    def parent(self, child):
        return QtCore.QModelIndex()

    # overload: get the row count
    def rowCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid(): return 0
        return len(self._table)

    # overload: get the column count
    def columnCount(self, parent = QtCore.QModelIndex()):
        return 4

    # overload: get the value of an index in a given role
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid(): return None
        col, ptr = index.column(), index.internalPointer()
        # text to display in the table
        # ptr is the key, so show that if we're in the key column
        # otherwise, get the appropriate string given the index
        if role == QtCore.Qt.DisplayRole:
            if col == 0: return ptr
            elif col == 1: return self._table[ptr][1]
            else:
                lst = None
                if col == 2: lst = self.getPackTypes(self._table[ptr][1])
                elif col == 3: lst = self.layoutList
                val = self._table[ptr][col]
                return "N/A" if val == None else lst[val]
        # the N/A string in the virtual layout field should be grey
        elif role == QtCore.Qt.ForegroundRole and col > 1:
            if self._table[ptr][col] != None: return None
            return QtGui.QBrush(QtCore.Qt.gray)
        # index of the combobox option to display
        elif role == QtCore.Qt.EditRole and col > 1:
            return self._table[ptr][col]
        # display an icon when the layout doesn't match the package type
        elif role == QtCore.Qt.DecorationRole and col == 3:
            if self._table[ptr][3] == None: return 0
            ptype = self.getPackTypes(self._table[ptr][1])[self._table[ptr][2]]
            layout = self.layoutList[self._table[ptr][3]]
            if layout not in self.deflayouts or (layout in self.deflayouts
                and ptype not in self.deflayouts[layout]):
                icon = QtGui.QStyle.SP_MessageBoxInformation
                return QtGui.qApp.style().standardIcon(icon)
            return 0
        # show a tooltip when the layout doesn't match the package type
        elif role == QtCore.Qt.ToolTipRole and col == 3:
            if self._table[ptr][3] == None: return None
            ptype = self.getPackTypes(self._table[ptr][1])[self._table[ptr][2]]
            layout = self.layoutList[self._table[ptr][3]]
            if layout not in self.deflayouts or (layout in self.deflayouts
                and ptype not in self.deflayouts[layout]):
                return "This layout is not the default for this package type."
            return None
        # show a tooltip containing the repository description
        elif role == QtCore.Qt.ToolTipRole and col == 0:
            if self._table[ptr][0] == None: return None
            return self._table[ptr][0]
        # return the combobox size hint, so the rows will be big enough
        elif role == QtCore.Qt.SizeHintRole and col == self.columnCount() - 1:
            return self.comboSize
        return None

    # overload: return the displayed header string of a given column index
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation != QtCore.Qt.Horizontal or role != QtCore.Qt.DisplayRole:
            return None
        hlist = ["Repository Key", "Repository Type", "Package Type", "Layout"]
        return hlist[section]

    # overload: set a given index to a specified value internally
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        col, ptr = index.column(), index.internalPointer()
        if role != QtCore.Qt.EditRole or col <= 1: return False
        # convert the row to a list (tuples are immutable)
        data = list(self._table[ptr])
        # set the proper element
        data[col], _ = value.toInt()
        # convert back to a tuple and save the row
        self._table[ptr] = tuple(data)
        return True

    # overload: return flags for a given index
    def flags(self, index):
        val = self._table[index.internalPointer()][index.column()]
        # key names are not editable
        # null values are also not editable
        if index.column() > 1 and val != None:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        return QtCore.Qt.ItemIsEnabled

    # given an index, return a list of available package types
    def getPackTypesList(self, index):
        if not index.isValid(): return None
        ptr = index.internalPointer()
        return self.getPackTypes(self._table[ptr][1])

    # given a repo type, return a list of available package types
    def getPackTypes(self, repoType, packTypesMap = {}):
        # memoize these, they aren't going to change
        if repoType in packTypesMap: return packTypesMap[repoType]
        # all the types that any repo can have
        types = ["bower", "docker", "gems", "gradle", "ivy", "maven", "npm",
                 "nuget", "pypi", "sbt"]
        # all the types that local repos can have
        if repoType == "local":
            types.extend(["debian", "gitlfs", "vagrant", "yum"])
        # all the types that remote repos can have
        elif repoType == "remote":
            types.extend(["debian", "p2", "vcs", "yum"])
        # all the types that virtual repos can have
        elif repoType == "virtual":
            types.extend(["p2"])
        else: raise ValueError("Incorrect package type: " + repoType)
        # sort them alphabetically and append generic to the end
        # this is how they are in the Artifactory ui
        types.sort()
        types.append("generic")
        packTypesMap[repoType] = types
        return types

    # list all the rows that have been modified
    def diffTable(self):
        diff = {}
        for key in self.keys:
            if self._table[key] != self.orig[key]: diff[key] = self._table[key]
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

# allows for filtering of non-maven repositories from the list
class MavenFilterModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent = None):
        QtGui.QSortFilterProxyModel.__init__(self, parent)
        self.source = None
        # whether to filter non-maven repos from the list
        self.mavenOnly = False

    # overload: get the source model so we can access it later
    def setSourceModel(self, model):
        QtGui.QSortFilterProxyModel.setSourceModel(self, model)
        self.source = model

    # overload: filter all the non-maven rows, only when the filter is enabled
    def filterAcceptsRow(self, row, parent):
        if not self.mavenOnly: return True
        rowdata = self.source.table[self.source.keys[row]]
        mvnidx = self.source.getPackTypes(rowdata[1]).index("maven")
        return rowdata[2] == mvnidx

    # allow the delegate to access the getPackTypesList function
    def getPackTypesList(self, index):
        return self.source.getPackTypesList(self.mapToSource(index))

    # allow the delegate to access the layoutList property
    def getLayoutList(self):
        return self.source.layoutList

    layoutList = property(getLayoutList)

# allows data to be modified properly in the QTreeView
class ComboBoxDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent = None):
        QtGui.QStyledItemDelegate.__init__(self, parent)

    # overload: create an editor widget for a given field
    def createEditor(self, parent, option, index):
        col, model = index.column(), index.model()
        if col <= 1:
            par = QtGui.QStyledItemDelegate
            return par.createEditor(self, parent, option, index)
        # all of these are editable with a combobox
        widget = QtGui.QComboBox(parent)
        widget.setAutoFillBackground(True)
        widget.setFocusPolicy(QtCore.Qt.StrongFocus)
        # comboboxes need lists of items to display
        lst = None
        if col == 2: lst = model.getPackTypesList(index)
        elif col == 3: lst = model.layoutList
        widget.addItems(lst)
        return widget

    # overload: set an editor widget to display the data in a given index
    def setEditorData(self, editor, index):
        if index.column() <= 1: return
        data, _ = index.data(QtCore.Qt.EditRole).toInt()
        editor.setCurrentIndex(data)

    # overload: modify the internal data to reflect the editor widget state
    def setModelData(self, editor, model, index):
        if index.column() <= 1: return
        data = QtCore.QVariant(editor.currentIndex())
        model.setData(index, data)
        if index.column() == 2 and editor.currentText() != "maven":
            try: model.invalidateFilter()
            except AttributeError: pass

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = PackageTypeWindow()
    sys.exit(app.exec_())
