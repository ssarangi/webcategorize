import controller
import logging
import socket
from threading import *
from fetcher import *


class Controller(Thread):
    """
    This class is responsible for controlling the fetchers and distributing
    the work load.
    """
    def __init__(self, linksToFetch, siteQueueAndCond, analyzer, numFetchers = 1, 
                 maxFetches = 100, socketTimeOut = 20, delay = 5):
        """
        Creates a new controller. Typically you will need only one.
        @param linksToFetch: A tuple of the form (Dict, Condition) where the dict
        is the map of domains to links to be fetched (which is updated by the analyzer)
        and the condition is a L{threading.Condition} object which is used to synchronize
        access to the list.
        @param siteQueueAndCond: a tuple of the form (list, cond) where list is the site queue
        into which fetchers insert new sites that have been fetched. cond is a Condition
        object which is used to lock the queue.
        @param analyzer: The analyzer which we are using for analyzing crawled data.
        @param numFetchers: The number of active threads used for crawling.
        @param maxFetches: Maximum number of pages to crawl.
        @param socketTimeOut: The timeout to use for opening urls. 
        WARNING: the timeout is set using socket.setdefaulttimeout(..)
        which affects ALL the sockets in the multiverse.
        @param delay: The delay in seconds between assignments of urls to fetchers.
        """
        Thread.__init__(self)

        self.__linksToFetch = linksToFetch
        self.__db = siteQueueAndCond
        self.__maxFetches = maxFetches
        
        # set the timeout
        socket.setdefaulttimeout(socketTimeOut)
        
        # the number of sites fetched so far
        self.__numFetches = 0
        
        # initialize the fetcher pool
        self.__fetchers = []
        
        # create the requested number of fetchers
        siteQueue, siteQueueCond = siteQueueAndCond
        for i in range(numFetchers):
            # create the condition for the fetcher
            c = Condition()
            
            # create the stop condition lock
            scl = Lock()
            
            # create the fetcher
            f = Fetcher(siteQueue, siteQueueCond, c, scl)
            
            # store the information about the fetcher
            self.__fetchers += [(f, c, scl)]

        self.__verificationMap = {}
        self.__delay = delay
        
        self.__analyzer = analyzer
            
    def getFetcherThreadUtilization(self):
        """
        Returns a list of number of urls each fetcher thread handler.
        """
        return [ftuple[0].getUrlsCounter() for ftuple in self.__fetchers]

    def getNumFetchersUsed(self):
        """
        Returns the number of fetchers that handled at least one url.
        """
        u = [ftuple[0].getUrlsCounter() for ftuple in self.__fetchers]
        counter = 0
        for x in u:
            if x > 0:
                counter += 1
        return counter
        
    def run(self):
        """
        Runs this controller thread. The controller will use it's
        fetchers to fill the links and sites databases.
        """
        logging.info("Starting the controller thread")
        
        # start all the fetcher threads
        for ftuple in self.__fetchers:
            ftuple[0].start()
        
        # let's, for comfort, separate the linksTofetch
        toFetchQueue, toFetchCond = self.__linksToFetch
        
        while (self.__numFetches < self.__maxFetches):
            sleep(self.__delay)
            # Check if we have something to fetch
            logging.debug('getting cond')
            toFetchCond.acquire()
            logging.debug('got cond')
            while (len(toFetchQueue) == 0):
                logging.debug('waiting')
                toFetchCond.wait()

            logging.debug('done waiting')
            # pop a url to fetch
            curUrl = self.__analyzer.selectNextUrl()
            #print str(toFetchQueue)
            if self.__verificationMap.has_key(curUrl):
                raise Exception, ("Duplicate URL [%s]" % curUrl)
            else:
                self.__verificationMap[curUrl] = True
            
            logging.debug("Controller acquired URL: [%s]" % curUrl)
            
            # release the lock
            toFetchCond.release()
            # increment the counter of fetched urls (we don't care if it succeeded)
            self.__numFetches += 1
            
            logging.info("Processed %d out of %d pages" % (self.__numFetches, self.__maxFetches))
            
            # find some fetcher to take the url
            foundFreeFetcher = False
            while (not foundFreeFetcher):
                for ftuple in self.__fetchers:
                    # if we can lock the condition then the fetcer might be free
                    if (ftuple[1].acquire(False)):
                        # if the fetcher is indeed free assign it a new url
                        if ftuple[0].isFree():
                            logging.debug("Controller found free fetcher")
                            # assign the new url to the fetcher
                            ftuple[0].setUrl(curUrl)
                            ftuple[1].notify()
                            ftuple[1].release()
                            foundFreeFetcher = True
                            break
                        else:
                            # if not, nudge it
                            ftuple[1].notify()
                            ftuple[1].release()
        
        # stop the fetchers    
        self.__stopFetchers()
        logging.debug("Stopping controller, %d fetcher threads were useful." % self.getNumFetchersUsed())

#    def selectNextUrl(self, toFetchQueue):
#        dom = toFetchQueue.keys()
#        selectedDom = dom[randint(0,len(dom) - 1)]
#        curUrl = toFetchQueue[selectedDom].pop()
#        if len(toFetchQueue[selectedDom]) == 0:
#            toFetchQueue.pop(selectedDom)
#        return curUrl

    def __stopFetchers(self):
        """
        Stops all the fetchers
        """
        logging.debug("Stopping fetchers")
        for ftuple in self.__fetchers:
            # set the stop condition
            ftuple[2].acquire()
            ftuple[0].setStopCondition(True)
            ftuple[2].release()
            
            # notify the fetcher
            ftuple[1].acquire()
            ftuple[1].notify()
            ftuple[1].release()
            
            # wait for the fetcher to terminate
            ftuple[0].join()
