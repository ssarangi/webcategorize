import urllib2
from naiveAnalyzer import *
from controller import *

class Crawler:
    """
       The main class of the crawler. 
    """

    def __init__(self, seed, fetcherThreads, maxUrlsToCrawl, timeOut, delay,
                 analyzer = NaiveAnalyzer, args = []):
        """
          Creates a new crawler. 
          @param seed: A map of domain names to urls in that domain from
          which to start crawling.
          @param fetcherThreads: The number of fetcher threads to use.
          @param maxUrlsToCrawl: How many pages to crawl
          @param timeOut: The socket timeout for loading a page.
          @param delay: The delay between crawls
          @param analyzer: The class of the analyzer to use.
        """

        authHandler = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(authHandler)
        urllib2.install_opener(opener)
        self.__linksToFetchAndCond = (dict(seed), Condition())
        self.__siteQueueAndCond = ([], Condition())
        self.__dbAndLock = ({}, Lock())

        self.__maxUrlsToCrawl = maxUrlsToCrawl

        # Create an analyzer
        self.__analyzer = analyzer(self.__linksToFetchAndCond, self.__siteQueueAndCond,
                                   self.__dbAndLock, *args)

        # Create a controller
        self.__controller = Controller(self.__linksToFetchAndCond, self.__siteQueueAndCond,
                                       fetcherThreads, maxUrlsToCrawl, timeOut, delay)

    def crawl(self):
        """
        Performs the crawling operation.
        """
        self.__analyzer.start()
        self.__controller.start()
        self.__controller.join()
        self.__analyzer.setStopCondition(True)
        self.__siteQueueAndCond[1].acquire()
        self.__siteQueueAndCond[1].notifyAll()
        self.__siteQueueAndCond[1].release()
        self.__analyzer.join()
        print "%d fetchers were useful" % self.__controller.getNumFetchersUsed()
        print("%d out of %d sites were succesfully crawles" % 
                (len(self.__dbAndLock[0]['sites']),self.__maxUrlsToCrawl))
        print "The sites that were succesfully crawled:"
        for s in self.__dbAndLock[0]['sites']:
            print self.__dbAndLock[0]['sites'][s].stringUrl

        self.__analyzer.report()

    def extractServerName(url):
        """
        Extracts the domain name from a string URL and returns it.
        """
        u = urlparse.urlparse(url)
        return u[1]
