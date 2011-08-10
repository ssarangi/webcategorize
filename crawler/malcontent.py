#Copyright (c) 2005 Eugene Vahlis, Li Yan
#
#Permission is hereby granted, free of charge, to any person obtaining a 
#copy of this software and associated documentation files (the "Software"), 
#to deal in the Software without restriction, including without limitation 
#the rights to use, copy, modify, merge, publish, distribute, sublicense, 
#and/or sell copies of the Software, and to permit persons to whom the 
#Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included 
#in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
#IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
#DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
#OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
#OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
This package is an implementation of an exploit detection analyzer
for the Orchid system and several rules for detecting specific
types of exploits.
"""

from crawler import *
import re
import logging

class Malcontent(NaiveAnalyzer):
    """
    This is a concrete analyzer which used together with the Orchid crawler
    to detect malicious web pages based on a given set of rules.
    """
    def __init__(self, linksToFetchAndCond, siteQueueAndCond, db, rules):
        """
        Creates a new malicious content analyzer.
        @param rules: a list of Rule objects to be applied against crawled sites.
        """
        NaiveAnalyzer.__init__(self, linksToFetchAndCond, siteQueueAndCond, db)
        self.__newLinksToCrawl = []
        self.__evilServers = {}
        self.__rules = rules
        self.__evilnessCounter = {Rule.GOOD: 0, Rule.MAY_BE_EVIL: 0, Rule.EVIL: 0}
        self.__exploitCounter = {}
    
    def analyzeSite(self, db, site):
        """
        Applies all the available rules to the given site and extracts the
        links that we intend to crawl. Currently we follow regular ('<a...'), frame,
        iframe and script links.
        """
        # initialize the db during the first call
        if not db.has_key('evilSites'):
            db['evilSites'] = {}
            
        # check all the rules against the site and if any of them matched
        # record the site as evil.
        if self.__checkSiteEvilness(site) > Rule.GOOD:
            del(site.content)
            del(site.rawContent)
            db['evilSites'][site.stringUrl] = site
            logging.warning("Evil site found: url [%s], evilness [%d]" % (site.stringUrl, site.evilness))
        
        # mark the site to avoid crawling it in the future
        db['crawled'][site.stringUrl] = True
        
        # extract the links that we want to follow some day
        self.__newLinksToCrawl = [link for link in site.links['regular'] if (not db['crawled'].has_key(link))]
        self.__newLinksToCrawl += [link for link in site.links['frame'] if (not db['crawled'].has_key(link))]
        self.__newLinksToCrawl += [link for link in site.links['iframe'] if (not db['crawled'].has_key(link))]
        self.__newLinksToCrawl += [link for link in site.links['script'] if (not db['crawled'].has_key(link))]

        # remove duplicates
        tempList = []
        for l in self.__newLinksToCrawl:
            db['crawled'][l] = True
            if not l in tempList:
                tempList += [l]
                
        # remove links that are evil and we don't want to crawl
        tempList = [l for l in tempList if not (l in site.evilLinks)]
        self.__newLinksToCrawl = tempList
        
    def addSiteToFetchQueue(self, lfs):
        """
        Add the sites we extracted in analyzeSite to the "to fetch" queue.
        """
        logging.debug("Adding to lfs")
        # we want to organize the links by their domain name
        domMap = self.reorganizeByDomain(self.__newLinksToCrawl)
        
        # add our list to the global list
        for dom in domMap:
            if lfs.has_key(dom):
                lfs[dom] += domMap[dom]
            else:
                lfs[dom] = domMap[dom]
        
    def selectNextUrl(self):
        """
        Select the next url to crawl to. This is done by selecting
        a random domain and then taking one page from it's queue.
        """
        toFetchQueue = self.linksToFetch[0]
        dom = toFetchQueue.keys()
        #badServs = [s for s in self.__evilServers if s in dom]
        #if len(badServs) > 0 and random() >= 0.1:
        #    selectedDom = badServs[randint(0,len(badServs) - 1)]
        #else:
        
        # choose a random domain
        selectedDom = dom[randint(0,len(dom) - 1)]
        
        # remove one link from it's queue
        curUrl = toFetchQueue[selectedDom].pop()
        
        # if there are no more links in this domain, trash it
        if len(toFetchQueue[selectedDom]) == 0:
            toFetchQueue.pop(selectedDom)
        return curUrl

    def __checkSiteEvilness(self, site):
        """
        Applies all the rules to the given site and records
        the results.
        """
        # apply the rules
        ruleEvilness = self.__checkSiteEvilnessWithRules(site)
        evilness = ruleEvilness
        self.__evilnessCounter[evilness] += 1
        
        # if we're evil record it
        if evilness > Rule.GOOD:
            serverName = extractServerName(site.stringUrl)
            if not self.__evilServers.has_key(serverName):
                self.__evilServers[serverName] = evilness
            else:
                self.__evilServers[serverName] = max(evilness, self.__evilServers[serverName])
                
        site.evilness = evilness
        return evilness
        
    def __checkSiteEvilnessWithRules(self, site):
        """
        Applies all the rules to the given site. 
        Helper method.
        """
        finalEvilness = Rule.GOOD
        
        for rule in self.__rules:
            evilness, exploits = rule(site)
            if evilness > finalEvilness:
                finalEvilness = evilness
                
            if evilness > Rule.GOOD:
                for exploit in exploits:
                    if not self.__exploitCounter.has_key(exploit):
                        self.__exploitCounter[exploit] = exploits[exploit]
                    else:
                        self.__exploitCounter[exploit] += exploits[exploit]
        return finalEvilness
    
    def report(self):
        """
        Logs the results of the crawl.
        """
        logging.info('Report:')
        logging.info('============')
        logging.info('Malicious sites detected: %d' % sum(self.__evilnessCounter))
        logging.info('    Breakdown: Good [%d], maybe evil [%d], evil [%d]' % (self.__evilnessCounter[Rule.GOOD],
                      self.__evilnessCounter[Rule.MAY_BE_EVIL], self.__evilnessCounter[Rule.EVIL]))
        logging.info('Exploits:')
        for e in self.__exploitCounter:
            logging.info('    [%s] : %d' % (e, self.__exploitCounter[e]))
            
        logging.info('Evil servers:')
        for s in self.__evilServers:
            logging.info('    [%s] : %d' % (s, self.__evilServers[s]))
            
        logging.info('Exploit Info:')
        for s in self.db[0]['evilSites']:
            logging.info('    [%s]' % s)
            for l in self.db[0]['evilSites'][s].matches:
                logging.info('        [%s] [%s]' % (l[0], l[1]))
                      
        
class Rule:
    """
    An abstract class representing rules for detecting malicious content.
    """
    GOOD = 0
    MAY_BE_EVIL = 1
    EVIL = 2
    
    def __call__(self, site):
        """
        Applies the rule to the given site. Should be overriden by real
        rules.
        """
        raise Exception, "This is an abstract class"

class LinkRule(Rule):
    """
    This rule applies regular expressions to certain link 
    types.
    """
    def __init__(self, reMap, reFlags = re.I | re.X):
        """
        Creates a new LinkRule
        @param reMap: a map which maps regular expression strings to tuples
        of the form (exploitName, linkTypes, level) where exploitName is the
        name of the exploit, linkTypes is a list of link types on which to match
        the regular expression (see orchid.OrchidExtractor for more detail), and level
        is the level of maliciousness for example: Rule.EVIL
        """
        self.__reMap = {}
        for pattern in reMap:
            self.__reMap[re.compile(pattern, reFlags)] = reMap[pattern]

    def __call__(self, site):
        """
        Applies the rule to the given site.
        """
        links = site.links
        curLevel = Rule.GOOD
        exploits = {}
        # go over all the patterns
        for pattern in self.__reMap:
            exploitName, linkTypes, level = self.__reMap[pattern]
            # for each pattern go over all the link types
            for linkType in linkTypes:
                # we have links of that type...
                if links.has_key(linkType) and len(links[linkType]) != 0:
                    for link in links[linkType]:
                        # try to match them
                        m = pattern.search(link)
                        if m:
                            site.evilLinks += [link]
                            site.matches += [(m.group(), exploitName)]
                            if curLevel < level:
                                curLevel = level
                            if exploits.has_key(exploitName):
                                exploits[exploitName] += 1
                            else:
                                exploits[exploitName] = 1
        return (curLevel, exploits)
    
class ContentRule(Rule):
    """
    This rule type matches regular expressions against the 
    raw content of the pages.
    """
    def __init__(self, reMap, reFlags = re.I | re.X):
        """
        Creates a new ContentRule.
        @param reMap: a map from regular expression strings to tuples
        of the form (exploitName, level) where exploit name is the exploit
        name and level is the badness level like Rule.EVIL
        """
        self.__reMap = {}
        for pattern in reMap:
            self.__reMap[re.compile(pattern, reFlags)] = reMap[pattern]

    def __call__(self, site):
        """
        Applies the rule to the given site
        """
        links = site.links
        curLevel = Rule.GOOD
        exploits = {}
        content = ' '.join(site.rawContent.split())
        # go over the patterns
        for pattern in self.__reMap:
            exploitName, level = self.__reMap[pattern]
            # try to match
            m = pattern.search(content) 
            if m:
                # if matches record the results
                site.matches += [(m.group(), exploitName)]
                if curLevel < level:
                    curLevel = level
                if exploits.has_key(exploitName):
                    exploits[exploitName] += 1
                else:
                    exploits[exploitName] = 1
        return (curLevel, exploits)

class ExternalIframeRule(Rule):
    """
    This rule type identifies IFRAME elements which load
    content from external servers.
    """
    def __init__(self):
        """Creates a new ExternalIframeRule"""
        None
        
    def __call__(self, site):
        """Applies this rule to the given site"""
        links = site.links
        curLevel = Rule.GOOD
        siteServerName = extractServerName(site.stringUrl)
        exploits = {'external iframe' : 0}
        for l in links['iframe']:
            sName = extractServerName(l)
            if sName != siteServerName:
                curLevel = Rule.MAY_BE_EVIL
                exploits['external iframe'] += 1
                site.matches += [(l, 'external iframe')]
        return (curLevel, exploits)
