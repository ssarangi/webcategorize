from alchemy import *

class UrlInterface:
    @staticmethod
    def crawlingComplete(db, company):
        company.crawled = 1
        db.session.commit()
    
    @staticmethod    
    def uncrawledCompanies(db):
        sql_query = db.session.query(Company).filter(Company.crawled == 0).order_by(Company.id)
        companies = sql_query.all()
        return companies
    
    @staticmethod
    def crawledCompanies(db):
        sql_query = db.session.query(Company).filter(Company.crawled == 1).order_by(Company.id)
        companies = sql_query.all()
        return companies
    
    @staticmethod
    def urlAnalyzed(db, url):
        ''' url: Object '''
        url.analyzed = 1
        db.session.commit()
    
    @staticmethod
    def urlError(db, url):
        url.analyzed = -1
        db.session.commit()
    
    @staticmethod
    def unAnalyzedURLs(db):
        sql_query = db.session.query(URL).filter(URL.analyzed == 0).order_by(URL.id)
        urls = sql_query.all()
        return urls
    
    