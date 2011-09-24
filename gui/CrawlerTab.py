from globals.global_imports import *
from crawler.crawler import *
from globals.settings import *

class CrawlerTab(QtGui.QWidget):
    """ Crawler Information display Class """
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.centralLayout = QtGui.QHBoxLayout()
        self.TableView = QtGui.QTableView()
        self.centralLayout.addWidget(self.TableView)
        
        # Set the central layout
        self.setLayout(self.centralLayout)
        
        # Setup the buttons
        self.startButton = QtGui.QPushButton("Start Crawler")
        self.stopButton = QtGui.QPushButton("Stop Crawler")
        
        # Setup the Crawler Algo
        self.crawlerThread = CrawlerThread(settings.opts, self)

        # Connect the crawler
        self.connect(self.startButton, QtCore.SIGNAL("released()"), self.startCrawler)
        self.centralLayout.addWidget(self.startButton)
        self.centralLayout.addWidget(self.stopButton)
                
    def startCrawler(self):
        self.crawlerThread.start()