from globals.Utils import *
from DB.KeywordInterface import *
from DB.UrlInterface import *
from StatisticsParser import *
from globals.global_imports import *
from gui.Worker import *

def addPageStatisticsToDB(url, db, pageStats):
    # Add everything to the DB
    for tag, tag_stats in pageStats.tag_statistics.items():
        tagObj = TagStats(tag, url.id)
        for kwrd, count in tag_stats.items():
            k_obj = KeywordStats(kwrd, count, tagObj.id)
            db.session.add(k_obj)
            
        db.session.add(tagObj)
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
                
        UrlInterface.urlAnalyzed(db, url)
        print pageStats
    except:
        print "Statistics Failed: %s" % url.address
        UrlInterface.urlError(db, url)
    # Add to DB
    
def GenerateStatisticsMain():
    keywordDB = getKeywordDB()
    urlDB     = getUrlDB()
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