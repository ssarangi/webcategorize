import sys
import time
from globals.global_imports import *
from crawler.crawler import *
from DataParsing.KeywordExtraction import *
from DataParsing.URLParsing import *
from DB.UrlInterface import *
from DB.alchemy import *
from PyQt4 import QtGui
from globals.settings import settings
from htmlExtraction.GenerateStatistics import *
from ResultGeneration.ResultGenerator import *
import gui.MainWindow


__version__ = "0.1"
USAGE = "%prog [options] <url>"
VERSION = "%prog v" + __version__
LOG_LEVEL  = logging.INFO
        
def correctURL(url):
    ''' url: String '''
    if (len(url) > 8):
        index_http = find(url, "http://", 0, 7)
        index_https = find(url, "http://", 0, 8)

        if (index_http == -1 and index_https == -1):
            url = "http://" + url
            
        return url            

def parse_options():
    """parse_options() -> opts, args

    Parse any command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-q", "--quiet",
            action="store_true", default=False, dest="quiet",
            help="Enable quiet mode")

    parser.add_option("-l", "--links",
            action="store_true", default=False, dest="links",
            help="Get links for specified url only")    

    parser.add_option("-d", "--depth",
            action="store", type="int", default=3, dest="depth_limit",
            help="Maximum depth to traverse")

    parser.add_option("-c", "--confine",
            action="store", type="string", dest="confine",
            help="Confine crawl to specified prefix")

    parser.add_option("-x", "--exclude", action="append", type="string",
                      dest="exclude", default=[], help="Exclude URLs by prefix")
    
    parser.add_option("-L", "--show-links", action="store_true", default=False,
                      dest="out_links", help="Output links found")

    parser.add_option("-s", "--show-urls", action="store_true", default=False,
                      dest="out_urls", help="Output URLs found")

    parser.add_option("-D", "--dot", action="store_true", default=False,
                      dest="out_dot", help="Output Graphviz dot file")
    
    parser.add_option("-K", "--keyword_parse", action="store_true", default=False,
                      dest="keyword_parse", help="Parse Keywords from Excel")

    parser.add_option("-U", "--url_parse", action="store_true", default=False,
                      dest="url_parse", help="Parse URL's from Excel")

    parser.add_option("--crawler", action="store_true", default=False,
                      dest="run_crawler", help="Run the crawler")

    parser.add_option("--stats", action="store_true", default=False,
                      dest="run_stats", help="Generate the statistics")

    parser.add_option("--results", action="store_true", default=False,
                      dest="results", help="Generate the results")

    opts, args = parser.parse_args()

    if opts.out_links and opts.out_urls:
        parser.print_help(sys.stderr)
        parser.error("options -L and -u are mutually exclusive")

    return opts, args

def showDB(db, className):
    print "Showing DB: %s" % className
    objs = db.session.query(className).all()
    for obj in objs:
        print obj
    
def main():    
    opts, args = parse_options()
    settings.opts = opts

    app = QtGui.QApplication(sys.argv)
    
    # mainWindow = gui.MainWindow.MainWindow(settings.version())
    # mainWindow.show()
    
    if opts.keyword_parse:
        createKeywordDB()
        exit()
        
    if opts.url_parse:
        createUrlDB()
        exit()

    # showDB(getKeywordDB(), ServiceLine1)
    if (opts.run_crawler):
        # crawlerThread = CrawlerThread(opts)
        # crawlerThread.start()
        while True:
            print "Waiting for URL's to Crawl"
            CrawlerMain(opts)
            time.sleep(10)
    
    keywordDB = getKeywordDB()
    urlDB     = getUrlDB()

    if (opts.run_stats):
        #statisticsThread = GenerateStatisticThread()
        #statisticsThread.start()
        while True:
            print "Waiting for URL's to Analyze"
            GenerateStatisticsMain(urlDB, keywordDB)
            time.sleep(10)
            
    if (opts.results):
        ResultGeneratorMain()
        
    # showDB(getUrlDB(), Company)
    # exit()
        
    # Test the keyword parsing
    # KeywordParse.KeywordParseMain()

    # showDB(getUrlDB(), URL)
        
            
if __name__ == "__main__":
    main()