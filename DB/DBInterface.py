import sqlite3, os
from globals.Utils import *
from htmlExtraction.KeywordRelationship import *

class DB:
    def __init__(self, db_filename, schema_filename):
        self.db_is_new = not os.path.exists(db_filename)
        self.conn = sqlite3.connect(db_filename)
        if self.db_is_new:
            print 'Creating schema'
            with open(schema_filename, 'rt') as f:
                schema = f.read()
            self.conn.executescript(schema)

        self.cursor = self.conn.cursor()

    def is_DB_new(self):
        return self.db_is_new
    
    def query(self, table, query_list, column, value, all_values=False, show_query=False):
        q_str = ','.join(query_list)
        
        sql_query = """
          select id, %s from %s where %s='%s'
        """ % (q_str, table, column, value)
        
        if (show_query == True):
            print sql_query
        
        self.cursor.execute(sql_query)
        
        if (all_values == False):
            return self.cursor.fetchone()
        else:
            return [row for row in self.cursor.fetchall()]
        
    def query_all(self, table):
        ''' Return all the elements from the table '''
        sql_query = """select * from %s""" % (table)
        self.cursor.execute(sql_query)
        
        return self.cursor.fetchall()
            
    def insert(self, table_name, column_list, data_list):
        ''' Both column_list & data_list are expected to be list of strings '''
        print "Adding Data for Table: %s" % table_name
        col_str = ','.join(column_list)
        data_list = StringUtils.add_quotes(data_list)
        data_str = ','.join(data_list)
        
        sql_query = """insert into %s (%s) values(%s)""" % (table_name, col_str, data_str)
        self.conn.execute(sql_query)
        self.conn.commit()
        
    def insert_many(self, table_name, column_name, data_list):
        ''' Insert a complete list with this function into the DB '''
        # executemany requires a tuple of items
        tuple_list = []
        for item in data_list:
            tuple_list.append((item,))        
                    
        sql_query = """insert into %s (%s) values (?)""" % (table_name, column_name)
        self.cursor.executemany(sql_query, tuple_list)
        self.conn.commit()
        
    def insert_many_list(self, table_name, fields, objData):
        ''' Inserts a complex column list with a list of data. The data is assumed to be
            a list of lists '''
        
        colSets = []
        valSets = []
        if len(fields) == 1:
            colSets.append( fields[0])
            valSets.append(':' + fields[0])
        else:
            for name in fields:
                colSets.append( name)
                valSets.append(':' + name)
        if len(colSets)== 1:
            colNames = colSets[0]
            vals = valSets[0]
        else:
            colNames = ', '.join(colSets)
            vals = ', '.join(valSets)
                    
        sql = "insert into %s (%s) values(%s)" % (table_name, colNames, vals)
        self.cursor.executemany(sql , objData)
        self.conn.commit()
        
class DBModel:
    ''' The Database Model used for getting querying the DB and getting results '''
    def __init__(self, db):
        self.db = db
                
    def keyword_relationship(self, keyword):        
        kwrd_id, keyword = self.db.query('keyword_table', ['keyword'], 'keyword', keyword)
            
        rel_id, sl1_id, sl2_id, sl3_id, kwrd_id = self.db.query('relationship', ["sl1_index", "sl2_index", "sl3_index", "keyword_index"], 'keyword_index', kwrd_id)
        sl1_id, sl1 = self.db.query('service_line_1', ["sl1_keyword"], 'id', sl1_id)
        sl2_id, sl2 = self.db.query('service_line_2', ["sl2_keyword"], 'id', sl2_id)
        sl3_id, sl3 = self.db.query('service_line_3', ["sl3_keyword"], 'id', sl3_id)
            
        rel = KeywordRelationship(sl1, sl2, sl3, keyword)
        
        return rel
        
    def keyword_list(self):
        kwrd_list = []
        rows = self.db.query_all('keyword_table')
        for row in rows:
            k_id, kwrd = row
            kwrd_list.append(kwrd) 
        
        return kwrd_list
         