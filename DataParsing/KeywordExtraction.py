from xlrd import open_workbook
from globals.global_imports import *
from globals.Utils import *
from DB.DBInterface import *
from DB.alchemy import *

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
        
        serialized_col = filter(lambda x: x.strip() != "", serialized_col)
        serialized_colSet = set(serialized_col)

        # Now create the DB objects
        serviceLine1_List = [ServiceLine1(sl1) for sl1 in sl1_set]
        self.db.session.add_all(serviceLine1_List)
        self.db.session.commit()

        # Now add the Service Line 2's
        serviceLine2_List = []
        for sl2 in sl2_set:
            # First find the index in original list
            sl2_original_index = sl2_list.index(sl2)
            sl1 = sl1_list[sl2_original_index]
            sl1_id = self.find_DB_id(sl1, ServiceLine1)
            sl2_db = ServiceLine2(sl2, sl1_id)
            serviceLine2_List.append(sl2_db)
            
        self.db.session.add_all(serviceLine2_List)
        self.db.session.commit()
        
        # Now add the Service Line 3's
        serviceLine3_List = []
        for sl3 in sl3_set:
            # First find the index in original list
            sl3_original_index = sl3_list.index(sl3)
            sl2 = sl2_list[sl3_original_index]
            sl2_id = self.find_DB_id(sl2, ServiceLine2)
            sl3_db = ServiceLine3(sl3, sl2_id)
            serviceLine3_List.append(sl3_db)
            
        self.db.session.add_all(serviceLine3_List)
        self.db.session.commit()
        
        assert(len(keywords_column) == len(sl1_list))
        assert(len(keywords_column) == len(sl2_list)) 
        assert(len(keywords_column) == len(sl3_list)) 

        # Now add the Keywords
        keywordList = []        
        total_items = len(sl1_list)

        for index in range(0, total_items):
            sl3 = sl3_list[index]
            sl3_id = self.find_DB_id(sl3, ServiceLine3)
            kwrd_list = keywords_column[index]
            
            for kwrd in kwrd_list:
                if kwrd.strip() != "":
                    k = KeywordTable(kwrd, sl3_id)
                    keywordList.append(k)
                    
        
        self.db.session.add_all(keywordList)
        self.db.session.commit()          
    
    def find_DB_id(self, wrd, className):
        obj = self.db.session.query(className).filter(className.keyword == wrd).one()
        return obj.id
    
#    def create_relationship_db(self, sl1_list, sl2_list, sl3_list, keywords_column):
#        ''' relationships: A List of relationship instance object '''
#
#        assert(len(keywords_column) == len(sl1_list))
#        assert(len(keywords_column) == len(sl2_list)) 
#        assert(len(keywords_column) == len(sl3_list)) 
#
#        total_items = len(sl1_list)
#
#        relationshipList = []
#
#        for index in range(0, total_items):
#            sl1 = sl1_list[index]
#            sl2 = sl2_list[index]
#            sl3 = sl3_list[index]
#            kwrd_list = keywords_column[index]
#            
#            for kwrd in kwrd_list:
#                if kwrd.strip() != "":
#                    # Find the id for sl1, sl2, sl3 & kwrd
#                    sl1_id = self.find_DB_id(sl1, ServiceLine1)
#                    sl2_id = self.find_DB_id(sl2, ServiceLine2)
#                    sl3_id = self.find_DB_id(sl3, ServiceLine3)
#                    kwrd_id = self.find_DB_id(kwrd, KeywordTable)
#                    r = Relationship(sl1_id, sl2_id, sl3_id, kwrd_id)
#                    relationshipList.append(r)
#                
#        self.db.session.add_all(relationshipList)
#        self.db.session.commit()
        
def createKeywordDB():
    ''' Read Excel File and recreate the Database '''
    db = getKeywordDB()
    db.createTable()
    excel_interface = KeywordExcelInterface(db)
    relationships = excel_interface.read_excel('DataParsing/automapping.xls')
    excel_interface.create_relationship_db(relationships)
    
if __name__ == "__main__":
    createKeywordDB()