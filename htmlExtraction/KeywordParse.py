from globals.Utils import *
from DB.DBInterface import *
from StatisticsParser import *
from KeywordRelationship import *
from globals.global_imports import *

    
def KeywordParseMain():
    db_filename = 'sqlite_dbs/keywords.db'
    schema_filename = 'sqlite_dbs/keywords_schema.sql'
    db = DB(db_filename, schema_filename)

    # Assume that the DB is already created
    #if (db.is_DB_new()):
    #    create_DB(db)
    
    dbModel = DBModel(db)
    # db_explore.find_keyword_db('Portal')
    kwrd_list = dbModel.keyword_list()
    
    #TODO: We shouldn't have empty keywords. But if we do remove them here.
    index = 0
    
    kwrd_list = [k for k in kwrd_list if k.strip() != ""]
    
    ss = StatisticsParser('htmlExtraction/test.html', dbModel)
    ss.accumulate_text_from_tags()
    page_stats = ss.search_for_keywords(kwrd_list)
    print page_stats  