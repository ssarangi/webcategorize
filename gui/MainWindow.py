import sys
import time
from PyQt4 import QtCore, QtGui
from globals.settings import settings
from gui.Icons import Ico
from gui.Icons import Icon
from gui.generic.TabManager import *
from gui.CrawlerTab import *
from crawler.crawler import *

class MainWindow(QtGui.QMainWindow):
    """
        Implements the Main Window
    """
    def __init__(self, version):
        """ version: String representing the Version """
        QtGui.QMainWindow.__init__(self)
        
        # User customizable style
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('CleanLooks'))
        
        # Set the Title
        self.title_text = "WebCategorize " + version
        ## Set Window Properties        
        self.setWindowTitle(self.title_text)
        self.setWindowIcon(Icon(Ico.Webcategorize))
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.setDockNestingEnabled(True)
        self.setDockOptions(self.AllowNestedDocks | self.AllowTabbedDocks | self.ForceTabbedDocks | self.AnimatedDocks | QtGui.QMainWindow.VerticalTabs)

#        self.topToolBar = QtGui.QToolBar()
#        self.topToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
#        self.addToolBar( self.topToolBar )

        ##############################################################
        ## File Menu
        ##############################################################
        menuFile    = self.menuBar().addMenu( "File" )
        menuSettings = menuFile.addAction(Icon(Ico.Settings), "Settings", self.on_settings_dialog)
        menuFile.addSeparator()
        # TODO: Connect this to something
        menuExit = menuFile.addAction(Icon(Ico.Exit), "Exit", self.on_exit)

        ##########################################################
        ## Central Widget
        ##########################################################

        self.mainTabWidget = QtGui.QTabWidget()
        self.mainTabWidget.setTabsClosable(True)
        self.mainTabWidget.setMovable(True)
        self.setCentralWidget(self.mainTabWidget)
        self.connect(self.mainTabWidget, QtCore.SIGNAL("tabCloseRequested (int)"), self.on_close_tab_requested)
        self.connect(self.mainTabWidget, QtCore.SIGNAL("currentChanged (int)"), self.on_tab_change)
        self.crawlerTab = CrawlerTab()
        self.mainTabWidget.addTab(self.crawlerTab, "Crawler")

        ##################################################
        ## Populate Central Tabs        
        self.on_action_view(QtCore.QString("welcome"))        
        self.on_action_view(QtCore.QString("projects"))
        self.on_action_view(QtCore.QString("api_browser"))
        #self.on_open_project(settings.app_path().absoluteFilePath("etc/example_project/example.pde"))

        self.mainTabWidget.setCurrentIndex(0)
        
    def on_settings_dialog(self):
        pass
    
    def on_exit(self):
        pass
    
    def on_close_tab_requested(self):
        pass
    
    def on_tab_change(self):
        pass
    
    def on_action_view(self, args):
        pass
    
    def getCrawlerTab(self):
        return self.crawlerTab
        