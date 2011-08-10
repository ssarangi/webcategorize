import lxml
import re

class Extractor:
    """
    A class responsible for parsing and analyzing html content and extracting
    various forms of links from it. The goal is to provide the user with a datastructure
    representing the parsed HTML and a set of links that appear on the given page.
    Supported links type are:
        1. simple <a href="...">link</a> type links (done)
        2. relative links
        3. BASE tag (done)
        4. LINK tag (done)
        5. FRAMESET links (done)
        6. IMG links (done)
        7. client side image maps (done)
        8. server side image maps (unsupported)
        9. Object links
        10. JavaScript links
        11. Meta refresh tags
        12. iframes
        13. form links
    """
    
    # These are the definition of the different link types and their patterns
    # (see __extractLinks for a detailed description of each element)
    LINK_PATTERNS = [('regular',       # type
      re.compile('^[aA]$'),            # tagPattern
      {'href' : re.compile('.+')},     # attrPatternMap
      'href'),                         # urlAttr

     ('base',                          # type
      re.compile('^(BASE)|(base)$'),   # tagPattern
      {'href' : re.compile('.+')},     # attrPatternMap
      'href'),                         # urlAttr

     ('link',                          # type
      re.compile('^(LINK)|(link)$'),   # tagPattern
      {'href' : re.compile('.+')},     # attrPatternMap
      'href'),                         # urlAttr

     ('frame',                         # type
      re.compile('^(FRAME)|(frame)$'), # tagPattern
      {'src' : re.compile('.+')},      # attrPatternMap
      'src'),                          # urlAttr

     ('area',                          # type
      re.compile('^(AREA)|(area)$'),   # tagPattern
      {'href' : re.compile('.+')},     # attrPatternMap
      'href'),                         # urlAttr

     ('iframe',                          # type
      re.compile('^(IFRAME)|(iframe)$'),   # tagPattern
      {'src' : re.compile('.+')},     # attrPatternMap
      'src'),                         # urlAttr

     ('script',                          # type
      re.compile('^(SCRIPT)|(script)$'),   # tagPattern
      {'src' : re.compile('.+')},     # attrPatternMap
      'src'),                         # urlAttr

     ('image',                         # type
      re.compile('^(IMG)|(img)$'),     # tagPattern
      {'src' : re.compile('.+')},      # attrPatternMap
      'src')]                          # urlAttr

    
    # TODO: add all the other link types
    
    def __init__(self):
        """
        Creates a new link extractor. Should be followed by a call to setSite
        """
        
        # The string representation of the url
        self.stringUrl = None
        
        # the domain of the url
        self.domain = None
        
        # The BeautifulSoup instance which contains the html
        # tree for this site
        self.parsedContent = None
        self.rawContent = None
        
        # a map from link type to arrays of links of that type
        self.links = {}
        
    def setSite(self, stringUrl, content):
        """
        Sets the current site url and content for the extractor.
        @param stringUrl: The url of the site being analyzed.
        @param content: The html content of the site.
        """
        # remove trailing / characters from the base ur
        self.stringUrl = stringUrl #.rstrip('/ ')
        preDomain = urlparse.urlparse(self.stringUrl)
        self.domain = urlparse.urlunparse((preDomain[0], preDomain[1],'', '', '', ''))
        #self.path = preDomain[2]
        #self.parentPath = preDomain[2].split('/')
        #self.parentPath = '/'.join(self.parentPath[0:-1])
        # clear the links
        self.links = {}
        
        # parse the content
        fullContent = content.read()
        self.parsedContent = BeautifulSoup(fullContent)
        self.rawContent = fullContent
        #logging.debug("Extractor url set. Soup created for: [%s]" % stringUrl)
        
    def getParsedContent(self):
        """
        Returns the BeautifulSoup datastructure of the HTML of the
        site that was set using setSite .
        """
        return self.parsedContent
    
    def getRawContent(self):
        return self.rawContent
    
    def getLinks(self):
        """
        Returns a map from link type to a list of links of that type that appeared 
        in the page.
        """
        return self.links
        
    def extract(self):
        """
        Extracts all the links in the page according to the patterns
        specified in LINK_PATTERNS. The links are stored in 
        a map (link type -> url list) called links (accessible 
        by 'extractor.links' where extractor is an instance of HtmlLinkExtractor)
        """
        #logging.debug("Extracting links")
        # extract the links from the html
        for p in self.LINK_PATTERNS:
            self.__extractLinks(*p)
            
        #logging.debug("Link extraction succesful")

    def __processRelativeLink(self, link):
        """
        Go over the links and see if any of them are relative (like '/about.html').
        When a relative link is found it is replaced by a full link 
        ('http://www.site.com/about.html').
        """
        # compile a RE which matches relatives paths
        relativePathRe = re.compile('/.*')
        
        if relativePathRe.match(link):
            # update the link to be a full link
            link = self.domain + link
        elif urlparse.urlparse(link)[0] == '':
            link = self.domain + self.path  + '/' + link
        
        return link
        
    def __extractLinks(self, type, tagPattern, attrPatternMap, urlAttr):
        """
        Extracts links with the specified configuration from the content
        and stores them in the appropriate list of links, according to their
        type.
        @param type: The type of the links to extract. This is also the key name
        under which the links will be added. 
        For example: 'regular', 'iframe'.
        @param tagPattern: a string or compiler regular expression which matches the names
        of the TAGS which contain the links. 
        For example: 'a', 'img', 'link'.
        @param attrPatternMap: A map of attribute names to strings or compiled regular 
        expressions. Only tags that have attribute that match the conditions
        in the map will be scanned for links.
        For example: {'href' : re.compile('.+')}
        @param urlAttr: The attribute from which the url of link should be extracted.
        For example: 'href', 'src'.
        """
        #logging.debug("Extracting links of type %s" % type)
        # fetch the links from the page
        links = self.parsedContent.fetch(tagPattern, attrPatternMap)
        #logging.debug("Got links from soup")
        
        # check if the list is already defined and if not
        # create an empty one
        if not self.links.has_key(type):
            self.links[type] = []

        # go over the links and place them in the array
        # of the links of the specified type
        
        #logging.debug("Adding and preprocessing links")
        #logging.debug(str(links))
        for l in links:
            #logging.debug(str(l))
            try:
                self.links[type] += [urlparse.urljoin(self.stringUrl, l[urlAttr].strip())]
            except:
                None
        #self.links[type] += [self.__processRelativeLink(l[urlAttr].strip()) for l in links]
        #logging.debug("Links added!")
