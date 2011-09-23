from DBInterface import *
from alchemy import *

class UrlInterface:
    def __init__(self, db):
        self.db = db
    
    def crawlingComplete(self, company_name):
        self.db.update('Company', "crawling", 1, "name", company_name)
        
        
    def uncrawledCompanies(self):
        # result = self.db.query("Company", ["name", "base_url", "crawled"], "crawled", 0, all_values=True)
        session = self.db.session
        sql_query = session.query(Company).filter(Company.crawled == 0).order_by(Company.id)
        companies = sql_query.all()
        return companies
    
    def urlAnalyzed(self, url):
        ''' url: String '''
        url.analyzed = 1
        self.db.session.commit()
        
    def unAnalyzedURLs(self):
        sql_query = self.db.session(URL).filter(URL.analyzed == 0).order_by(URL.id)
        urls = sql_query.all()
        return urls
    
    