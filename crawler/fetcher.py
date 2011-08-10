from threading import *
from urlhandler import *
from extractor import *
import logging

class Fetcher(Thread):
    """
    This class is responsible for fetching url contents, processing them
    with UgrahExtractor and updating the site and link database.
    """
    
    def __init__(self, siteQueue, siteQueueCond, fetcherCondition, stopConditionLock):
        """
        Creates a new fetcher thread (not started) with the following
        @param siteQueue: the site queue from which the analyzer takes sites
        to analyze.
        @param siteQueueCond: A Condition object used to lock the siteQueue.
        @param fetcherCondition: a threading.Condition object which is used for
        communication between the fetcher and the controller: whenever
        a fetcher finishes working on it's assignment it calls 
        fetcherCondition.wait() and waits until the controller assigns
        a new url for it to fetch.
        @param stopConditionLock: a threading.Lock object which is used to lock
        the internal stop condition variable. A thread that wishes
        to change this variable should lock it first.
        """
        Thread.__init__(self)
        self.siteQueue = siteQueue
        self.condition = fetcherCondition
        self.siteQueueCond = siteQueueCond
        self.stopConditionLock = stopConditionLock
        
        # the stop condition, the loop will run while it's false
        self.stopCondition = False
        
        # the url of the site we're currently supposed to process
        self.currentStringUrl = None
        
        # the url handler used for processing
        self.urlHandler = UrlHandler()
        
        # the extractor we're going to use to process the page
        self.extractor = Extractor()
        
        # a statistical used for debugging and ... statistics
        self.handledUrlsCounter = 0

    def setStopCondition(self, val):
        """ 
        Can receive either True or False. Set to Ture when the fetcher
        should stop working. WARNING: It's *necessary* to acquire the lock
        which was passed to the constructor as stopConditionLock before
        calling this method.
        """
        self.stopCondition = val
        
    def setUrl(self, stringUrl):
        """
        Sets the url that the fetcher should work on. It's *necessary*
        to acquire the condition instance which was passed to the constructor
        as fetcherCondition before calling this method and call notify afterwards
        """
        self.currentStringUrl = stringUrl
        
    def getUrlsCounter(self):
        """
        Returns the number of URLs this fetcher has handled.
        Should be called only AFTER the thread is dead.
        """
        return self.handledUrlsCounter
        
    def isFree(self):
        """
        Returns True if the fetcher hasn't been assigned a URL yet.
        """
        return (self.currentStringUrl == None)
    
    def run(self):
        """
        Performs the main function of the fetcher which is to fetch
        the contents of the url specified by setCurrentStringUrl.
        This method loops until the stop condition is set.
        """
        
        # lock our condition (this a is standard pattern)
        self.condition.acquire()
        
        # lock the stop condition variable
        self.stopConditionLock.acquire()
        while (not self.stopCondition) or (self.currentStringUrl):
            # wait until we get a new url to fetch
            while (not self.currentStringUrl) and (not self.stopCondition):
                # release the stop condition lock
                self.stopConditionLock.release()
                self.condition.wait()
                self.stopConditionLock.acquire()
                
            # we have to check the stop condition since it could
            # have changed while we were waiting
            if self.stopCondition and (not self.currentStringUrl):
                # we do not release the lock here because it is
                # release immidiately after exiting the loop
                break
            else:
                self.stopConditionLock.release()
            
            # increase the url counter
            self.handledUrlsCounter += 1
            #logging.debug("URL acquired by fetcher: [%s]", self.currentStringUrl)
            
            try:
                # step 1: fetch the url
                #######################
                
                # process the site
                self.__processSite()
                
                # retrieve the data
                links = self.extractor.getLinks()
                parsedContent = self.extractor.getParsedContent()
                rawContent = self.extractor.getRawContent()
    
                # step 2: file the retrieved data
                #################################
                s = Site(self.currentStringUrl, links, parsedContent, rawContent)
                self.__fileData(s, links)
                logging.info("URL processing succeeded: [%s]" % self.currentStringUrl)
            except Exception, e:
                logging.info("URL processing failed: [%s], error: %s" % (self.currentStringUrl, e))
            
            # nullify the current url
            self.currentStringUrl = None
            
            # lock the stop condition variable for the next while check
            self.stopConditionLock.acquire()
        
        # release the condition
        self.condition.release()
        # release the stop condition lock
        self.stopConditionLock.release()


    def __fileData(self, s, links):
        """
        Stores the given site and links in the databases
        """
        # lock the db
        self.siteQueueCond.acquire()
        
        # store the new site information
        self.siteQueue.insert(0, s)
        
        # wake an analyzer
        self.siteQueueCond.notify()
        
        # unlock the db
        self.siteQueueCond.release()

    def __processSite(self):
        """
        Fetches the url contents and creates a parsed structure
        """
        self.urlHandler.processUrl(self.currentStringUrl)
        content = self.urlHandler.getSite()
        self.extractor.setSite(self.currentStringUrl, content)
        self.extractor.extract()
