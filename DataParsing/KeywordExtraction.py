from xlrd import open_workbook
from globals.global_imports import *
from globals.Utils import *
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
                 
        keywords_column = StringUtils.remove_empty_rows(self.raw_keywords)
            
        keywords_column = StringUtils.reparse_keywords(keywords_column)
        
        serviceLineSet = zip(sl1_list, sl2_list, sl3_list)
            
        # Now create the DB objects
        serviceLine_List = [ServiceLine(serviceLine[0], serviceLine[1], serviceLine[2]) for serviceLine in serviceLineSet]
        
        self.db.session.add_all(serviceLine_List)
        self.db.session.commit()

        assert(len(keywords_column) == len(sl1_list))
        assert(len(keywords_column) == len(sl2_list)) 
        assert(len(keywords_column) == len(sl3_list)) 

        # Now add the Keywords
        keywordList = []        
        total_items = len(sl1_list)

        for index in range(0, total_items):
            sl1 = sl1_list[index]
            sl2 = sl2_list[index]
            sl3 = sl3_list[index]
            sl_id = self.findServiceLineID(serviceLine_List, sl1, sl2, sl3)
            kwrd_list = keywords_column[index]
            
            for kwrd in kwrd_list:
                if kwrd.strip() != "":
                    k = KeywordTable(kwrd, sl_id)
                    keywordList.append(k)
                    
        
        self.db.session.add_all(keywordList)
        self.db.session.commit()          
    
    def findServiceLineID(self, ServiceLinesList, sl1, sl2, sl3):
        for s in ServiceLinesList:
            if (s.serviceLine1 == sl1 and s.serviceLine2 == sl2 and s.serviceLine3 == sl3):
                return s.id
        
        raise Exception("Service Line ID not found.")
    
def createKeywordDB():
    ''' Read Excel File and recreate the Database '''
    db = getKeywordDB()
    db.createTable()
    excel_interface = KeywordExcelInterface(db)
    excel_interface.read_excel('DataParsing/automapping.xls')
    
if __name__ == "__main__":
    createKeywordDB()