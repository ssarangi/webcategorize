#!/usr/bin/env python

"""Web Crawler/Spider

This module implements a web crawler. This is very _basic_ only
and needs to be extended to do anything useful with the
traversed pages.

"""

import re
import sys
import time
import math
import urllib2
import urlparse
import optparse
import hashlib
import socket
from string import *
from cgi import escape
from traceback import format_exc
from Queue import Queue, Empty as QueueEmpty
from BeautifulSoup import BeautifulSoup
from globals.global_imports import *
from globals.Logger import *
from DB.alchemy import *
from DB.UrlInterface import *
from gui.Worker import *
from django.conf.locale import te

__version__ = "0.1"
__copyright__ = "CopyRight (C) 2008-2011 by Satyajit Sarangi. Originally by James Miller (https://github.com/ewa/python-webcrawler/blob/master/crawler.py)"
__license__ = "MIT"
__author__ = "Satyajit Sarangi"
__author_email__ = "Satyajit Sarangi, Satyajit dot Sarangi at gmail dot com"

AGENT = "%s/%s" % (__name__, __version__)

def getLinks(url):
    page = Fetcher(url)
    page.fetch()
    for i, url in enumerate(page):
        print "%d. %s" % (i, url)


class Link (object):

    def __init__(self, src, dst, link_type):
        self.src = src
        self.dst = dst
        self.link_type = link_type

    def __hash__(self):
        return hash((self.src, self.dst, self.link_type))

    def __eq__(self, other):
        return (self.src == other.src and
                self.dst == other.dst and
                self.link_type == other.link_type)
    
    def __str__(self):
        return self.src + " -> " + self.dst

class Crawler(object):
    def __init__(self, crawlerTab, company, depth_limit, confine=None, exclude=[], locked=True, filter_seen=True):
        self.company = company
        self.root = company.base_url
        self.host = urlparse.urlparse(self.root)[1]
        self.urlDB = getUrlDB()
#        sqlite_handler = SQLiteHandler(getCrawlerLogDB())
#        if (crawlerTab != None):
#            table_handler = QTableViewHandler(crawlerTab.TableView)
#            self.logger.addHandler(table_handler)            
#            self.logger.addHandler(table_handler)        
#        
#        console_handler = ConsoleHandler()
#        
#        self.logger = logging.getLogger()
#        # logging.handlers.SQLiteHandler = sqlite_handler
#        # logging.handlers.QTableViewHandler = table_handler
#        
#        sqlite_handler.setLevel(logging.INFO)
#        console_handler.setLevel(logging.INFO)
#        
#        self.logger.addHandler(sqlite_handler)
#
#        self.logger.addHandler(console_handler)
        
        ## Data for filters:
        self.depth_limit = depth_limit # Max depth (number of hops from root)
        self.locked = locked           # Limit search to a single host?
        self.confine_prefix=confine    # Limit search to this prefix
        self.exclude_prefixes=exclude; # URL prefixes NOT to visit
                

        self.urls_seen = set()          # Used to avoid putting duplicates in queue
        self.urls_remembered = set()    # For reporting to user
        self.visited_links= set()       # Used to avoid re-processing a page
        self.links_remembered = set()   # For reporting to user
        
        self.num_links = 0              # Links found (and not excluded by filters)
        self.num_followed = 0           # Links followed.  

        # Pre-visit filters:  Only visit a URL if it passes these tests
        self.pre_visit_filters=[self._prefix_ok,
                                self._exclude_ok,
                                self._not_visited,
                                self._same_host]

        # Out-url filters: When examining a visited page, only process
        # links where the target matches these filters.        
        if filter_seen:
            self.out_url_filters=[self._prefix_ok,
                                     self._same_host]
        else:
            self.out_url_filters=[]

    def _pre_visit_url_condense(self, url):
        
        """ Reduce (condense) URLs into some canonical form before
        visiting.  All occurrences of equivalent URLs are treated as
        identical.

        All this does is strip the \"fragment\" component from URLs,
        so that http://foo.com/blah.html\#baz becomes
        http://foo.com/blah.html """

        base, frag = urlparse.urldefrag(url)
        return base

    ## URL Filtering functions.  These all use information from the
    ## state of the Crawler to evaluate whether a given URL should be
    ## used in some context.  Return value of True indicates that the
    ## URL should be used.
    
    def _prefix_ok(self, url):
        """Pass if the URL has the correct prefix, or none is specified"""
        return (self.confine_prefix is None  or
                url.startswith(self.confine_prefix))

    def _exclude_ok(self, url):
        """Pass if the URL does not match any exclude patterns"""
        prefixes_ok = [ not url.startswith(p) for p in self.exclude_prefixes]
        return all(prefixes_ok)
    
    def _not_visited(self, url):
        """Pass if the URL has not already been visited"""
        return (url not in self.visited_links)
    
    def _same_host(self, url):
        """Pass if the URL is on the same host as the root URL"""
        try:
            host = urlparse.urlparse(url)[1]
            return re.match(".*%s" % self.host, host) 
        except Exception, e:
            print >> sys.stderr, "ERROR: Can't process url '%s' (%s)" % (url, e)
            return False
            

    def crawl(self):

        """ Main function in the crawling process.  Core algorithm is:

        q <- starting page
        while q not empty:
           url <- q.get()
           if url is new and suitable:
              page <- fetch(url)   
              q.put(urls found in page)
           else:
              nothing

        new and suitable means that we don't re-visit URLs we've seen
        already fetched, and user-supplied criteria like maximum
        search depth are checked. """
        
        q = Queue()
        q.put((self.root, 0))

        while not q.empty():
            this_url, depth = q.get()
                        
            #Non-URL-specific filter: Discard anything over depth limit
            if depth > self.depth_limit:
                continue
            
            #Apply URL-based filters.
            do_not_follow = [f for f in self.pre_visit_filters if not f(this_url)]
            
            #Special-case depth 0 (starting URL)
            if depth == 0 and [] != do_not_follow:
                # self.logger.info("Whoops! Starting URL %s rejected by the following filters:" % (do_not_follow))
                pass
            
            #If no filters failed (that is, all passed), process URL
            if [] == do_not_follow:
                try:
                    self.visited_links.add(this_url)
                    self.num_followed += 1
                    # self.logger.info("Following Link: %s" % this_url)
                    print "Following Link: %s" % this_url
                    page = Fetcher(this_url)
                    page.fetch()
                    content = page.content.encode("utf-8")
                    # URL
                    url = URL(this_url, content, 0, self.company.id)
                    # Now we have the url and the content. Add it to the DB
                    self.urlDB.session.add(url)
                    self.urlDB.session.commit()
                    
                    for link_url in [self._pre_visit_url_condense(l) for l in page.out_links()]:
                        if link_url not in self.urls_seen:
                            q.put((link_url, depth+1))
                            self.urls_seen.add(link_url)
                            
                        do_not_remember = [f for f in self.out_url_filters if not f(link_url)]
                        if [] == do_not_remember:
                                self.num_links += 1
                                self.urls_remembered.add(link_url)
                                link = Link(this_url, link_url, "href")
                                if link not in self.links_remembered:
                                    self.links_remembered.add(link)
                except Exception, e:
                    print >>sys.stderr, "ERROR: %s" % (e)
                    self.urlDB.session.rollback()
                                        
class OpaqueDataException (Exception):
    def __init__(self, message, mimetype, url):
        Exception.__init__(self, message)
        self.mimetype=mimetype
        self.url=url
        

class Fetcher(object):
    
    """The name Fetcher is a slight misnomer: This class retrieves and interprets web pages."""

    def __init__(self, url):
        self.url = url
        self.out_urls = []
        self.encoding = ""
        self.content = ""
        socket.setdefaulttimeout(2)
        
    def __getitem__(self, x):
        return self.out_urls[x]

    def out_links(self):
        return self.out_urls

    def _addHeaders(self, request):
        request.add_header("User-Agent", AGENT)

    def _open(self):
        url = self.url
        try:
            request = urllib2.Request(url)
            handle = urllib2.build_opener()
        except IOError:
            return None
        return (request, handle)

    def fetch(self):
        request, handle = self._open()
        self._addHeaders(request)
        if handle:
            try:
                data=handle.open(request)
                mime_type=data.info().gettype()
                url=data.geturl();
                if mime_type != "text/html":
                    raise OpaqueDataException("Not interested in files of type %s" % mime_type,
                                              mime_type, url)
                self.content = unicode(data.read(), "utf-8",
                                       errors="replace")
                soup = BeautifulSoup(self.content)
                self.encoding = "utf-8"
                tags = soup('a')
            except urllib2.HTTPError, error:
                if error.code == 404:
                    print >> sys.stderr, "ERROR: %s -> %s" % (error, error.url)
                else:
                    print >> sys.stderr, "ERROR: %s" % error
                tags = []
            except urllib2.URLError, error:
                print >> sys.stderr, "ERROR: %s" % error
                tags = []
            except OpaqueDataException, error:
                print >>sys.stderr, "Skipping %s, has type %s" % (error.url, error.mimetype)
                tags = []
            for tag in tags:
                href = tag.get("href")
                if href is not None:
                    url = urlparse.urljoin(self.url.encode(self.encoding), escape(href))
                    if url not in self:
                        self.out_urls.append(url.encode(self.encoding))


class DotWriter:

    """ Formats a collection of Link objects as a Graphviz (Dot)
    graph.  Mostly, this means creating a node for each URL with a
    name which Graphviz will accept, and declaring links between those
    nodes."""

    def __init__ (self):
        self.node_alias = {}

    def _safe_alias(self, url, silent=False):

        """Translate URLs into unique strings guaranteed to be safe as
        node names in the Graphviz language.  Currently, that's based
        on the md5 digest, in hexadecimal."""

        if url in self.node_alias:
            return self.node_alias[url]
        else:
            m = hashlib.md5()
            m.update(url)
            name = "N"+m.hexdigest()
            self.node_alias[url]=name
            if not silent:
                print "\t%s [label=\"%s\"];" % (name, url)                
            return name


    def asDot(self, links):

        """ Render a collection of Link objects as a Dot graph"""
        
        print "digraph Crawl {"
        print "\t edge [K=0.2, len=0.1];"
        for l in links:            
            print "\t" + self._safe_alias(l.src) + " -> " + self._safe_alias(l.dst) + ";"
        print  "}"
        
def CrawlerMain(opts, crawlerTab=None):
        urlDB = getUrlDB()
        companies = UrlInterface.uncrawledCompanies(urlDB)

        depth_limit = opts.depth_limit
        confine_prefix = opts.confine
        exclude = opts.exclude
    
        sTime = time.time()
    
        for i in range(0, len(companies)):
            if opts.links:
                getLinks(self.companies[i].base_url)
                raise SystemExit, 0

            print >> sys.stderr,  "Crawling %s (Max Depth: %d)" % (companies[i].base_url, depth_limit)
            crawler = Crawler(crawlerTab, companies[i], depth_limit, confine_prefix, exclude)
            crawler.crawl()
            UrlInterface.crawlingComplete(urlDB, companies[i])
            
        if opts.out_urls:
            print "\n".join(crawler.urls_seen)

        if opts.out_links:
            print "\n".join([str(l) for l in crawler.links_remembered])
            
        if opts.out_dot:
            d = DotWriter()
            d.asDot(crawler.links_remembered)
    
        eTime = time.time()
        tTime = eTime - sTime
    
        print >> sys.stderr, "Found:    %d" % crawler.num_links
        print >> sys.stderr, "Followed: %d" % crawler.num_followed
        print >> sys.stderr, "Stats:    (%d/s after %0.2fs)" % (
                int(math.ceil(float(crawler.num_links) / tTime)), tTime)
    
        for k,v in crawler.url_content.items():
            print "Url: %s\n" % k    
        
        
class CrawlerThread(WorkerThread):
    def __init__(self, opts, crawlerTab=None):
        WorkerThread.__init__(self, "Crawler Thread")
        self.opts = opts
        
    def run(self):
        CrawlerMain(self.opts)
        print "Waiting for more URL's to Crawl"
