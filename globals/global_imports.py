import sys
import logging
import os
import sqlite3
from xlrd import open_workbook
import optparse
import sys
from string import *
from DB.DBInterface import *

def getUrlDB():
    db_filename = 'sqlite_dbs/urls.db'
    schema_filename = 'sqlite_dbs/urls_schema.sql'
    db = DB(db_filename, schema_filename)
    return db

def getKeywordDB():
    db_filename = 'sqlite_dbs/keywords.db'
    schema_filename = 'sqlite_dbs/keywords_schema.sql'
    db = DB(db_filename, schema_filename)
    return db