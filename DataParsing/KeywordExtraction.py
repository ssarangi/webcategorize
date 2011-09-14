from xlrd import open_workbook
from globals.Utils import *
from DB.DBInterface import *

class KeywordExcelInterface:
    ''' Excel Interface - Class to read an excel file and generate the keyword DB '''
    def __init__(self, db):
        self.relationships = [] 
        self.db = db
        
    def __insert(self, tableName, columnName, dataSet):
        ''' Use this function to insert multiple inserts into DB
            tableName: String: DB Table name
            columnName: String: DB Column in DB Table
            dataSet: List: 
        '''
        if (len(dataSet) > 0):
            for d in dataSet:
                self.db.insert(tableName, [columnName], [d])
    
    def read_excel(self, filename):
        ''' sl are service lines '''
        wb = open_workbook(filename)
        sheet0 = wb.sheet_by_index(0)
        
        self.raw_sl1 = sheet0.col_slice(3, 2)
        self.raw_sl2 = sheet0.col_slice(4, 2)
        self.raw_sl3 = sheet0.col_slice(5, 2)
        self.raw_keywords = sheet0.col_slice(10, 2)
    
        sl1_list = [StringUtils.remove_text_from_string(s, "text:u'") for s in StringUtils.remove_empty_rows(self.raw_sl1)] 
        sl2_list = [StringUtils.remove_text_from_string(s, "text:u'") for s in StringUtils.remove_empty_rows(self.raw_sl2)]
        sl3_list = [StringUtils.remove_text_from_string(s, "text:u'") for s in StringUtils.remove_empty_rows(self.raw_sl3)]
         
        sl1_set = set(sl1_list)
        sl2_set = set(sl2_list)
        sl3_set = set(sl3_list)
        
        keywords_column = StringUtils.remove_empty_rows(self.raw_keywords)
            
        keywords_column = StringUtils.reparse_keywords(keywords_column)
            
        # serialize the keyword column
        serialized_col = []
        for klist in keywords_column:
            for k in klist:
                serialized_col.append(k)
        
        serialized_col = set(serialized_col)
        
        self.db.insert_many('service_line_1', 'sl1_keyword', sl1_set)
        self.db.insert_many('service_line_2', 'sl2_keyword', sl2_set)
        self.db.insert_many('service_line_3', 'sl3_keyword', sl3_set)        
        self.db.insert_many('keyword_table', 'keyword', serialized_col)        
        
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
        data_list = []
        for rel in relationships:
            sl1_id, kwrd = self.db.query("service_line_1", ["sl1_keyword"], "sl1_keyword", rel.sl1)
            sl2_id, kwrd = self.db.query("service_line_2", ["sl2_keyword"], "sl2_keyword", rel.sl2)
            sl3_id, kwrd = self.db.query("service_line_3", ["sl3_keyword"], "sl3_keyword", rel.sl3)
            kwrd_id, kwrd = self.db.query("keyword_table", ["keyword"], "keyword", rel.keyword)
            
            temp_list = [sl1_id, sl2_id, sl3_id, kwrd_id]
            data_list.append(temp_list)
            
        self.db.insert_many_list('relationship', ["sl1_index", "sl2_index", "sl3_index", "keyword_index"], data_list)
        
def createKeywordDB():
    ''' Read Excel File and recreate the Database '''
    db_filename = 'sqlite_dbs/keywords.db'
    schema_filename = 'sqlite_dbs/keywords_schema.sql'
    db = DB(db_filename, schema_filename)
    excel_interface = KeywordExcelInterface(db)
    relationships = excel_interface.read_excel('DataParsing/automapping.xls')
    excel_interface.create_relationship_db(relationships)
    
if __name__ == "__main__":
    createKeywordDB()