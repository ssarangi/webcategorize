import robotparser

class UrlHandler:
    """
    A class responsible for parsing a url and retrieving it's contents.
    """
    
    def __init__(self):
        """
        A constructor for the url handler. Should be followed 
        by calls to setCurrentUrl and getSite.
        """
        # initialize the robot parser
        self.robotParser = robotparser.RobotFileParser()
        self.currentSite = None
        
    def processUrl(self, stringUrl):
        """
        Sets the url that the parser is working on.
        Raises an exception if we can't open it.
        """
        self.robotParser = robotparser.RobotFileParser()
        # check access rights, if not ok raise exception
        if not self.__canVisitSite(stringUrl):
            logging.info("access to [%s] was denied by robots.txt" % stringUrl)
            raise Exception, "robots.txt doesn't allow access to %s" % stringUrl
        
        # create the HTTP request
        req = self.__createRequest(stringUrl)
        # open the url and set our site to the opened url
        site = urllib2.urlopen(req)
        
        if (not (site.headers.type == 'text/html')) and (not (site.headers.type == 'application/x-javascript')):
            logging.info('Url contained mime type which is not text/html: [%s]' % stringUrl)
            raise Exception, "Not text/html mime type"
        
        logging.info("successfully opened %s" % stringUrl)
        self.currentSite = site

    def getSite(self):
        """
        Returns the url object which was opened by setCurrentUrl.
        The returned object acts just like a file object.
        """
        return self.currentSite

    def __createRequest(self, stringUrl):
        req = urllib2.Request(stringUrl)
        req.add_header('User-agent', 'MyCrawler/0.1')
        return req
        
    def __canVisitSite(self, stringUrl):
        """
        Checks whether we are allowed by robots.txt to visit some page.
        Returns true if we can, false otherwise.
        """
        # extract the robots.txt url
        parsedUrl = urlparse.urlparse(stringUrl)
        robotsUrl = urlparse.urlunparse((parsedUrl[0], parsedUrl[1], "robots.txt", 
                                         parsedUrl[3], parsedUrl[4], parsedUrl[5]))
        
        # parse robots.txt
        self.robotParser.set_url(robotsUrl)
        self.robotParser.read()
        
        # check permission to access page
        return self.robotParser.can_fetch("MyCrawler/0.1", stringUrl)
