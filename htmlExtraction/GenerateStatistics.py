from globals.Utils import *
from DB.KeywordInterface import *
from DB.UrlInterface import *
from StatisticsParser import *
from globals.global_imports import *
from gui.Worker import *

def addPageStatisticsToDB(url, db, pageStats):
    # Add everything to the DB
    tagObjList = []
    KeywordDict = {}
    for tag, tagStatistics in pageStats.tag_statistics.items():
        tagObj = TagStats(tag, url.id)
        # db.session.add(tagObj)
        tagObjList.append(tagObj)
        for kwrd, count in tagStatistics.tag_stats.items():
            # k_obj = KeywordStats(kwrd.keyword, count, tagObj.id)
            KeywordDict[(kwrd, count)] = tagObj
            # db.session.add(k_obj)
            # db.session.commit()
            # tagObj.keywords.append(k_obj)
            
    db.session.add_all(tagObjList)
    db.session.commit()
    
    # Now add all the Keyword Dicts
    kwrdObjList = []
    for (keyword, count), tagObj in KeywordDict.items():
        k_obj = KeywordStats(keyword.keyword, count, tagObj.id, keyword.id)
        kwrdObjList.append(k_obj)
        
    db.session.add_all(kwrdObjList)
    db.session.commit()

def SinglePageStatistics(url, keywords, db):
    ''' url: URL alchemy object
        keywords: KeywordTable alchemy object list
        db: Alchemy DB instance
    '''
    try:
        print "Generating Statistics for %s" % url.address
        statisticsParser = StatisticsParser(url, db)
        statisticsParser.accumulate_text_from_tags()
        pageStats = statisticsParser.search_for_keywords(keywords)

        print pageStats
        
        addPageStatisticsToDB(url, db, pageStats)
        UrlInterface.urlAnalyzed(db, url)
    except Exception as inst:
        print "Statistics Failed: %s" % url.address
        print "Exception: %s" % inst
        UrlInterface.urlError(db, url)
    
def GenerateStatisticsMain(urlDB, keywordDB):
    kwrd_list = KeywordInterface.getKeywordsList(keywordDB)
    
    # Now get the list of URL's
    urls = UrlInterface.unAnalyzedURLs(urlDB)
    
    for url in urls:
        SinglePageStatistics(url, kwrd_list, urlDB)

            
class GenerateStatisticThread(WorkerThread):
    def __init__(self):
        WorkerThread.__init__(self, "Generate Statistics Thread")
        
    def run(self):
        GenerateStatisticsMain()
        print "Waiting for more URL's to Analyze"
        
if __name__ == "__main__":
    GenerateStatisticsMain()