from alchemy import *

class KeywordInterface:
    @staticmethod    
    def getKeywordsList(db):
        keywords = db.session.query(KeywordTable).all()
        return keywords
    
    @staticmethod
    def getRelationship(keywordObj):
        sl3_obj = keywordObj.serviceLine3
        sl2_obj = sl3_obj.serviceLine2
        sl1_obj = sl2_obj.serviceLine1
        
        return (sl1_obj, sl2_obj, sl3_obj)
        
    @staticmethod
    def getKeywordByID(db, keyword_id):
        return db.session.query(KeywordTable).filter(KeywordTable.id == keyword_id).one()
        