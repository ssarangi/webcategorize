import sys
import logging
import os
import sqlite3
from xlrd import open_workbook
import optparse
import sys
from string import *
from DB.alchemy import *
from types import *
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtSql
from DB import alchemy
from globals.settings import settings

urlDB = None
keywordDB = None

def getUrlDB():
    global urlDB
    dbName = "urls"
    if (urlDB == None):
        urlDB = Alchemy(dbName, alchemy.URLBase, settings.username, settings.password)
        
    return urlDB

def getKeywordDB():
    global keywordDB
    dbName = "keywords"
    if (keywordDB == None):
        keywordDB = Alchemy(dbName, alchemy.KeywordBase, settings.username, settings.password)

    return keywordDB

def getCrawlerLogDB():
    db_filename = 'sqlite_dbs/crawlerLogs.db'
    return db_filename

def getHTMLParserLogDB():
    db_filename = 'sqlite_dbs/htmlParserLogs.db'
    return db_filename

def assertType(data, expected):
    if (type(data) != expected):
        msg = "Error: %s expected. Given %s" % (expected, type(data))
        raise(msg)
    
