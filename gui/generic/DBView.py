from globals.global_imports import *

class DatabaseView(QtGui.QWidget):
    """ Crawler Information display Class """
    def __init__(self, db, table):
        QtGui.QWidget.__init__(self)
        self.centralLayout = QtGui.QHBoxLayout()
        self.centralLayout.addWidget(QtGui.QTextBrowser())
        
        # Set the central layout
        self.setLayout(self.centralLayout)
        
        self.view = QtGui.QTableView()

    def __introspectTableColumns(self, table):
        pass