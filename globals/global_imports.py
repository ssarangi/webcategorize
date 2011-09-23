import sys
import logging
import os
import sqlite3
from xlrd import open_workbook
import optparse
import sys
from string import *
from DB.DBInterface import *
from DB.alchemy import *
from types import *
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtSql

def getUrlDB():
    db_filename = 'sqlite_dbs/urls.db'
    schema_filename = 'sqlite_dbs/urls_schema.sql'
    db = Alchemy(db_filename)
    # db = DB(db_filename, schema_filename)
    return db

def getKeywordDB():
    db_filename = 'sqlite_dbs/keywords.db'
    schema_filename = 'sqlite_dbs/keywords_schema.sql'
    db = DB(db_filename, schema_filename)
    return db

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
    
__version__ = "1.0"