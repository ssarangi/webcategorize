class Site:
    """
    A class for representing the information that is collected for
    a specific site.
    """
    
    def __init__(self, stringUrl, links, parsedContent, rawContent):
        """
        Creates a new site. 
        @param stringUrl: the url of the site
        @param links: a map from link types to links which appear on this page
        @param parsedContent: BeautifulSoup instance which contains the parsed content
        of the page.
        @param rawContent: The raw content of the page as a string.
        """
        self.stringUrl = stringUrl
        self.links = links
        self.content = parsedContent
        self.rawContent = rawContent
        self.evilLinks = []
        self.evilness = 0
        self.matches = [] 
