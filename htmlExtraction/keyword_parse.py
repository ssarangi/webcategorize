from xlrd import open_workbook
import sqlite3
import os

class KeywordRelationship:
    def __init__(self, sl1, sl2, sl3, kwrd):
        self.sl1 = sl1
        self.sl2 = sl2
        self.sl3 = sl3
        self.keyword = kwrd
        
    def __str__(self):
        return self.sl1 + " -- " + self.sl2 + " -- " + self.sl3 + " -- " + self.keyword + "\n"

class Utils:
    @staticmethod
    def remove_text_from_string(orig_str, to_be_removed_str):
        new_str = orig_str[len(to_be_removed_str):]
        new_str = new_str.replace("'", " ").strip()
        return new_str
    
    @staticmethod
    def remove_empty_rows(column):
        final_ls = []
        for col in column:
            if (str(col).find('empty') == -1):
                final_ls.append(str(col))
                
        return final_ls
    
    @staticmethod
    def reparse_keywords(keywords_column):
        ''' Keyword lists can be separated by a separator '|'. For this 
            reason we need to split them and create separate rows for them '''
        new_column = []
        for keyword_row in keywords_column:
            # Take the row and replace the '|' character with ','
            keyword_row_text = Utils.remove_text_from_string(str(keyword_row), "text:u'")
            kwrd_row_list = [s.strip() for s in keyword_row_text.replace('|', ',').split(',')]
            new_column.append(kwrd_row_list)
        
        return new_column
    
    @staticmethod
    def add_quotes(string_list):
        new_str = []
        for string in string_list:
            string = "'" + string + "'"
            new_str.append(string)
        
        return new_str
        
class DB:
    def __init__(self, db_filename, schema_filename):
        db_is_new = not os.path.exists(db_filename)
        self.conn = sqlite3.connect(db_filename)
        if db_is_new:
            print 'Creating schema'
            with open(schema_filename, 'rt') as f:
                schema = f.read()
            self.conn.executescript(schema)

        self.cursor = self.conn.cursor()

    
    def query(self, table, query_list, column, value, all_values=False):
        q_str = ','.join(query_list)
        
        sql_query = """
          select id, %s from %s where %s='%s'
        """ % (q_str, table, column, value)
        
        self.cursor.execute(sql_query)
        
        if (all_values == False):
            return self.cursor.fetchall()[0]
        else:
            return [row for row in self.cursor.fetchall()]
            
    def insert(self, table_name, column_list, data_list):
        ''' Both column_list & data_list are expected to be list of strings '''
        col_str = ','.join(column_list)
        data_list = Utils.add_quotes(data_list)
        data_str = ','.join(data_list)
        
        sql_query = """insert into %s (%s) values(%s)""" % (table_name, col_str, data_str)
        self.conn.execute(sql_query)
    
class DBExplore:
    def __init__(self, db):
        self.db = db
                
    def find_keyword_db(self, keyword):        
        kwrd_id, keyword = self.db.query('keyword_table', ['keyword'], 'keyword', keyword)
            
        id, sl1_id, sl2_id, sl3_id, kwrd_id = self.db.query('relationship', ["sl1_index", "sl2_index", "sl3_index", "keyword_index"], 'keyword_index', kwrd_id)
        sl1_id, sl1 = self.db.query('service_line_1', ["sl1_keyword"], 'id', sl1_id)
        sl2_id, sl2 = self.db.query('service_line_2', ["sl2_keyword"], 'id', sl2_id)
        sl3_id, sl3 = self.db.query('service_line_3', ["sl3_keyword"], 'id', sl3_id)
            
        rel = KeywordRelationship(sl1, sl2, sl3, keyword)
        
        print rel
 
class ExcelInterface:
    def __init__(self, db):
        self.relationships = [] 
        self.db = db
        
    def _insert(self, table_name, column_name, data_set):
        ''' Use this function to insert multiple inserts into DB '''
        if (len(data_set) > 0):
            for d in data_set:
                self.db.insert(table_name, [column_name], [d])
    
    def read_excel(self, filename):
        ''' sl are service lines '''
        wb = open_workbook(filename)
        sheet0 = wb.sheet_by_index(0)
        
        self.raw_sl1 = sheet0.col_slice(3, 2)
        self.raw_sl2 = sheet0.col_slice(4, 2)
        self.raw_sl3 = sheet0.col_slice(5, 2)
        self.raw_keywords = sheet0.col_slice(10, 2)
    
        sl1_list = [Utils.remove_text_from_string(s, "text:u'") for s in Utils.remove_empty_rows(self.raw_sl1)] 
        sl2_list = [Utils.remove_text_from_string(s, "text:u'") for s in Utils.remove_empty_rows(self.raw_sl2)]
        sl3_list = [Utils.remove_text_from_string(s, "text:u'") for s in Utils.remove_empty_rows(self.raw_sl3)]
         
        sl1_set = set(sl1_list)
        sl2_set = set(sl2_list)
        sl3_set = set(sl3_list)
        
        keywords_column = Utils.remove_empty_rows(self.raw_keywords)
            
        keywords_column = Utils.reparse_keywords(keywords_column)
            
        # serialize the keyword column
        serialized_col = []
        for klist in keywords_column:
            for k in klist:
                serialized_col.append(k)
        
        serialized_col = set(serialized_col)

        self._insert('service_line_1', 'sl1_keyword', sl1_set)
        self._insert('service_line_2', 'sl2_keyword', sl2_set)
        self._insert('service_line_3', 'sl3_keyword', sl3_set)        
        self._insert('keyword_table', 'keyword', serialized_col)
        
        # Generate the relationship in memory
        total_items = len(sl1_list)
            
        for index in range(0, total_items):
            sl1 = sl1_list[index]
            sl2 = sl2_list[index]
            sl3 = sl3_list[index]
            keyword_list = keywords_column[index]
            
            for kwrd in keyword_list:
                rel = KeywordRelationship(sl1, sl2, sl3, kwrd)
                self.relationships.append(rel)
        
        return self.relationships
    
    def create_relationship_db(self, relationships):
        ''' relationships: A List of relationship instance object '''
        global conn
        kwrd = ""
        for rel in relationships:
            sl1_id, kwrd = self.db.query("service_line_1", ["sl1_keyword"], "sl1_keyword", rel.sl1)
            sl2_id, kwrd = self.db.query("service_line_2", ["sl2_keyword"], "sl2_keyword", rel.sl2)
            sl3_id, kwrd = self.db.query("service_line_3", ["sl3_keyword"], "sl3_keyword", rel.sl3)
            kwrd_id, kwrd = self.db.query("keyword_table", ["keyword"], "keyword", rel.keyword)
            
            self.db.insert("relationship", ["sl1_index", "sl2_index", "sl3_index", "keyword_index"], [str(sl1_id), str(sl2_id), str(sl3_id), str(kwrd_id)])
            # sql_query = """insert into relationship (sl1_index, sl2_index, sl3_index, keyword_index)  
            #                values(%s, %s, %s, %s)""" % (sl1_id, sl2_id, sl3_id, kwrd_id)
            
            # conn.execute(sql_query)
    
if __name__ == "__main__":
    db_filename = 'keywords.db'
    schema_filename = 'keywords_schema.sql'    
    db = DB(db_filename, schema_filename)
    excel_interface = ExcelInterface(db)
    relationships = excel_interface.read_excel('automapping.xls')
    excel_interface.create_relationship_db(relationships)
    
    db_explore = DBExplore(db)
    db_explore.find_keyword_db('Portal')