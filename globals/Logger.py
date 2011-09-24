import logging
import sqlite3
import time
from globals.global_imports import *

class SQLiteHandler(logging.Handler): # Inherit from logging.Handler
    def __init__(self, filename):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Our custom argument
        self.db = sqlite3.connect(filename) # might need to use self.filename
        self.db.execute("CREATE TABLE IF NOT EXISTS debug(date_time text, loggername text, srclineno integer, func text, level text, msg text)")
        self.db.commit()

    def emit(self, record):
        # record.message is the log message
        thisdate = time.time()
        print record.getMessage()
        self.db.execute('INSERT INTO debug(date_time, loggername, srclineno, func, level, msg) VALUES(?,?,?,?,?,?)',
                         (thisdate, record.name, record.lineno, record.funcName, record.levelname, record.msg))
        self.db.commit()

class QTableViewHandler(logging.Handler):
    """ QTableViewHandler: Logs to QTable """
    def __init__(self, qTableView):
        logging.Handler.__init__(self)
        self.QTableView = qTableView
        self.index = 0
        
        # Add the logging objects
        self.model = QtGui.QStandardItemModel(1, 6)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "Date/Time")
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Logger Name")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Src Line No.")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Function")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Level")
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, "Message")
        
        self.QTableView.setModel(self.model)
        
    def emit(self, record):
        thisdate = time.time()        
        self.model.setItem(self.index, 0, QtGui.QStandardItem(thisdate))
        self.model.setItem(self.index, 1, QtGui.QStandardItem(record.name))
        self.model.setItem(self.index, 2, QtGui.QStandardItem(record.lineno))
        self.model.setItem(self.index, 3, QtGui.QStandardItem(record.funcName))
        self.model.setItem(self.index, 4, QtGui.QStandardItem(record.levelname))
        self.model.setItem(self.index, 5, QtGui.QStandardItem(record.msg))
               
        self.index += 1
        
class ConsoleHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        
    def emit(self, record):
        thisdate = time.time()
        print "[%s]: [%s] - [%s] - [%s] - [%s] - %s" % (thisdate, record.name, record.lineno, record.funcName, record.levelname, record.msg)
    
        
        