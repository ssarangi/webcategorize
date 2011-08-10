import logging
from threading import *

class NaiveAnalyzer(Thread):
    """
    This is an interface for the analyzers. To use the Ugrah crawler
    subclass this class with you logic of analyzing the gathered
    data and choosing which links to crawl.
    """
    
    def __init__(self, linksToFetchAndCond, siteQueueAndCond, db):
        """
        Creates a new analyzer. There can be as many analyzers as you like,
        depending on the type of processing of data you wish to do.
        @param linksToFetchAndCond: A tuple of the form (map, Condition) where the map
        is the map of domains to links to be fetched (which is updated by the analyzer)
        and the condition is a L{threading.Condition} object which is used to synchronize
        access to the list.
        @param siteQueueAndCond: A tuple (siteQueue, siteCond). The siteQueue is a queue
        unto which new sites (with their links) are inserted. The siteCond is a Condition
        object used to lock the queue and signal the analyzer to wake up.
        @param db: a tuple of the form (siteDb, siteDbLock) where the linkDb
        is the global link database, siteDb is the global site database and the lock
        is used to synchronize access to both of these databases.
        """
        Thread.__init__(self)
        self.linksToFetch = linksToFetchAndCond
        self.db = db
        self.siteQueueAndCond = siteQueueAndCond
        
        # stop condition variable
        self.__stopCondition = False
        
        # a lock to lock the stop condition
        self.__scl = Lock()
        
        # initialize the db
        if not self.db[0].has_key('crawled'):
            self.db[0]['crawled'] = {}

        if not self.db[0].has_key('sites'):
            self.db[0]['sites'] = {}
            
        self.__sitesProcessed = 0
        
    def setStopCondition(self, val):
        """
        Sets the stop condition to the specified value. Should be True to stop
        the analyzer thread.
        """
        self.__scl.acquire()
        self.__stopCondition = val
        self.__scl.release()
        
    def getNumSitesProcessed(self):
        """
        Returns the number of sites this analyzer has processed
        """
        return self.__sitesProcessed
        
    def run(self):
        """
        Performs the main function of the analyzer. In this case,
        just adds all the hyperlinks to the toFetch queue.
        """
        # separate the tuples for convinience
        lfs, lfsCond = self.linksToFetch
        siteDb, dbLock = self.db
        siteQueue, siteQueueCond = self.siteQueueAndCond
        
        # repeat while the stop condition hasn't been set
        self.__scl.acquire()
        siteQueueCond.acquire()
        while (not self.__stopCondition) or (len(siteQueue) != 0):
            # check if there's anything in the queue
            while (len(siteQueue) == 0) and (not self.__stopCondition):
                self.__scl.release()
                siteQueueCond.wait()
                self.__scl.acquire()

            if (self.__stopCondition) and (len(siteQueue) == 0):
                break

            # release the stop condition lock for now
            self.__scl.release()
            
            # get a site to process
            #logging.debug("siteQueue is [%s]" % (str([s.stringUrl for s in siteQueue])))
            siteToProcess = siteQueue.pop()
            self.__sitesProcessed += 1
            
            # release the lock on the site queue
            siteQueueCond.release()
            
            # process the new site
            dbLock.acquire()
            self.analyzeSite(siteDb, siteToProcess)
            dbLock.release()
            
            # add links to the links to fetch queue
            lfsCond.acquire()
            self.addSiteToFetchQueue(lfs)
            lfsCond.notify()
            lfsCond.release()
            
            # reacquire the lock before the while condition check
            self.__scl.acquire()
            
            # reacquire the site queue lock before the while condition check
            siteQueueCond.acquire()
        
        self.__scl.release()
        # release the lock on the site queue
        siteQueueCond.release()
            
    def analyzeSite(self, db, site):
        """
        Processes the site and adds it to the db.
        Any real analyzer should override this method with it's
        own logic.
        """
        # check if the site was already crawled
        #if db['crawled'].has_key(site.stringUrl):
        #    self.__newLinksToCrawl = []
        #    return
        
        # add the site
        #db['sites'][site.stringUrl] = site
        db['crawled'][site.stringUrl] = True
        
        # decide which links to crawl (in this case all regular links)
        self.__newLinksToCrawl = [link for link in site.links['regular'] if (not db['crawled'].has_key(link))]
        #logging.debug("Site: [%s], The new ltc of the analyzer is: [%s]" % (site.stringUrl, str(self.__newLinksToCrawl)))

        tempList = []
        for l in self.__newLinksToCrawl:
            db['crawled'][l] = True
            if not l in tempList:
                tempList += [l]
        self.__newLinksToCrawl = tempList

                
    def addSiteToFetchQueue(self, lfs):
        """
        Adds links to the fetch queue. A real analyzer should override
        this method.
        """
        logging.debug("Adding to lfs")
        domMap = self.reorganizeByDomain(self.__newLinksToCrawl)
        for dom in domMap:
            if lfs.has_key(dom):
                lfs[dom] += domMap[dom]
            else:
                lfs[dom] = domMap[dom]

    def reorganizeByDomain(self, listOfLinks):
        """
        Returns a map which maps domain names to links inside the domain.
        """
        pLinks = [urlparse.urlparse(l) for l in listOfLinks]
        domMap = {}
        for l in pLinks:
            if domMap.has_key(l[1]):
                domMap[l[1]] += [urlparse.urlunparse(l)]
            else:
                domMap[l[1]] = [urlparse.urlunparse(l)]

        return domMap
    
    def selectNextUrl(self):
        """
        Chooses the next url to crawl to. This implementation
        will select a random domain and then crawl to the first link 
        in that domain's queue.
        """
        toFetchQueue = self.linksToFetch[0]
        dom = toFetchQueue.keys()
        selectedDom = dom[randint(0,len(dom) - 1)]
        curUrl = toFetchQueue[selectedDom].pop()
        if len(toFetchQueue[selectedDom]) == 0:
            toFetchQueue.pop(selectedDom)
        return curUrl
    
    def report(self):
        """
        A real analyzer should override this method. Outputs the results
        of the analysis so far.
        """
        None
