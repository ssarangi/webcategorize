from xlrd import *
from globals.Utils import *
from globals.global_imports import *
from DB.alchemy import *

class URLExcelInterface:
    ''' Excel Interface - Class to read an excel file and generate the keyword DB '''
    def __init__(self, db):
        self.relationships = [] 
        self.db = db
        
    def read_excel(self, filename):
        ''' sl are service lines '''
        wb = open_workbook(filename)
        sheet0 = wb.sheet_by_index(0)
        
        self.raw_company_name = sheet0.col_slice(1, 1)
        self.raw_url          = sheet0.col_slice(2, 1)
            
        company_list = [StringUtils.remove_text_from_string(str(s), "text:u'") for s in self.raw_company_name]
        url_list = [StringUtils.remove_text_from_string(str(s), "text:u'") for s in self.raw_url]
         
        #company_set = set(company_list)
        #url_set = set(url_list)
                    
        total_items = len(company_list)
        
        self.final_company_list = []
        self.final_url_list     = []
        
        db_list = []        # Temporary list to add data
        for i in range(0, total_items):
            if (url_list[i].strip() != ""):
                self.final_company_list.append(company_list[i])
                self.final_url_list.append(url_list[i])
                c = Company(company_list[i], url_list[i])
                db_list.append(c)
        
        self.db.session.add_all(db_list)        
        self.db.session.commit()
        # self.db.insert_many_list('Company', ['name', 'base_url'], db_list)
        
    
def createUrlDB():
    ''' Read Excel File and recreate the Database '''
    print "Recreating the URL database"
    urlDB = getUrlDB()
    urlDB.createTable()
    excel_interface = URLExcelInterface(urlDB)
    excel_interface.read_excel('DataParsing/URLs.xls')
    # excel_interface.create_relationship_db(relationships)
    
if __name__ == "__main__":
    createUrlDB()