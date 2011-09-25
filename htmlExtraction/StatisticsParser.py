import lxml.etree
import string, StringIO
from globals.Utils import *
from DB.KeywordInterface import *

global debug

html_tag_list = ["meta", \
                 "h1",
                 "h2",
                 "h3",
                 "h4",
                 "h5",
                 "h6",
                 "p",
                 "li",
                 "head",
                 "title",
                 "dd",
                 "dl"                 
                ]

def print_debug(msg):
    global debug
    if (debug == True):
        print msg

def extract_key_value_pair(attribs, attrib_key_1, key, attrib_key_2):
    ''' So for HTML, lets say we have a Meta tag. So that might have as
    a key with name="keywords". So attrib_key_1 = name & key = "keywords"
    Similarly, attrib_key_2=content'''
    found_key = False
    found_value = False
    
    for iter_key, iter_value in attribs.items():
        if (iter_key == attrib_key_1 and iter_value == key):
            found_key = True
        if (iter_key == attrib_key_2):
            result = iter_value
    
    if (found_key == True and found_value == True):
        return key, result
    else:
        return None, None


class TagStatistics:
    def __init__(self, tag):
        if (tag.strip() == ""):
            raise ValueError
        self.tag = tag
        self.tag_stats = {}
        self.kwrd_relationship = {}
    
    def add_keyword(self, kwrdObj, count):
        self.tag_stats[kwrdObj] = count
        self.kwrd_relationship[kwrdObj] = KeywordInterface.getRelationship(kwrdObj)
        
    def get_keyword_count(self, kwrdObj):
        try:
            return self.tag_stats[kwrdObj]
        except:
            return 0
        
    def __str__(self):
        ret_str =  "\nStatistics for Tag: %s\n" % self.tag
        for k, v in self.tag_stats.items():
            rel = self.kwrd_relationship[k]
            ret_str +=  "Keyword: %s\n" % k.keyword
            ret_str += "Count: %s\n" % str(v)
            ret_str += "Service Line 1: %s\n" % rel[0]
            ret_str += "Service Line 2: %s\n" % rel[1]
            ret_str += "Service Line 3: %s\n" % rel[2]
                         
        return ret_str
        
class PageStatistics:
    def __init__(self, urlObj):
        self.urlObj = urlObj
        self.url = urlObj.address
        self.tag_statistics = {}
        
    def _add_tag(self, tag):
        tag_stats = TagStatistics(tag)
        self.tag_statistics[tag] = tag_stats
        
    def update_count(self, tag, keyword, count):
        try:
            self.tag_statistics[tag].add_keyword(keyword, count)
        except:
            self.tag_statistics[tag] = TagStatistics(tag)
            self.tag_statistics[tag].add_keyword(keyword, count)
        
    def __str__(self):
        ret_str = ""
        ret_str =  "Page Statistics for Page: %s\n" % (self.url)
        ret_str += ''.join('=' for i in range(0, len(ret_str))) + "\n"
        for tag, tag_stats in self.tag_statistics.items():
            ret_str += str(tag_stats)
            
        return ret_str

class HandleTarget:
    ''' Class to Handle the Meta Tags and other content lines we are looking for
        eg. h1, h2, etc '''
    ''' tag_text_content: Contains the Text for each Tag. Eg. All the text from all h1 tags 
        will be contained in one place '''
    def __init__(self):
        self.tags_func_ptrs = {
                            "meta": self.handle_meta_tags,
                            "h1": self.handle_generic,
                            "h2" : self.handle_generic,
                            "h3" : self.handle_generic,
                            "h4" : self.handle_generic,
                            "h5" : self.handle_generic,
                            "h6" : self.handle_generic,
                            "p"  : self.handle_generic,
                            "li" : self.handle_generic,
                            "head" : self.handle_generic,
                            "title" : self.handle_generic,
                            "dd" : self.handle_generic,
                            "dl" : self.handle_generic
                            }   
        
        self.tag_text_content = {}
        
    def handle_generic(self, tag, attribs, element=None):
        # First search if the key exists
        if (element.text == None):
            text = ""
        else:
            text = element.text + " "
            
        try:
            self.tag_text_content[tag] += text
        except:
            self.tag_text_content[tag] = text
            
    def handle_meta_tags(self, tag, attribs, element=None):
        if (attribs == None):
            return
        keywords, content = extract_key_value_pair(attribs, "name", "keywords", "content")
        content = string.split(content, ' ')
        return keywords, content        
        
    def handle_tag(self, tag, attribs, element=None):
        global debug, html_tag_list
        if tag in html_tag_list:
            return self.tags_func_ptrs[tag](tag, attribs, element)

    def return_tag_text_content(self):
        return self.tag_text_content

class CollectorTarget:
    def __init__(self):
        self.events = []
        self.handle_target = HandleTarget()
        self.keywords = ""
        self.extracted_data = {}
        
    def start(self, tag, attribs):
        self.events.append("start %s %s" % (tag, attribs))
                
    def end(self, tag):
        self.events.append("end %s" % tag)
        
    def data(self, data):
        self.events.append("data %r" % data)
        
    def comment(self, text):
        self.events.append("comment %s" % text)
        
    def close(self):
        self.events.append("close")
        
class StatisticsParser:
    def __init__(self, urlObj, db):
        ''' This is the URL DB object '''
        self.collector_parser = lxml.etree.HTMLParser(remove_blank_text=True,
                                                      remove_comments=True,
                                                      target=CollectorTarget())
        
        self.parser = lxml.etree.HTMLParser(remove_blank_text=True,
                                            remove_comments=True)

        
        self.html = urlObj.content
        
        self.tree = lxml.etree.parse(StringIO.StringIO(self.html), parser=self.parser)
        doc_info = self.tree.docinfo
        self.encoding = doc_info.encoding
        self.db = db
        self.tag_text = {}
        self.page_statistics = PageStatistics(urlObj)
        
    def accumulate_text_from_tags(self):
        global html_tag_list
        handle = HandleTarget()
        root = self.tree.getroot()
        for element in root.iter():
            handle.handle_tag(element.tag, None, element)
        
        self.tag_text = handle.return_tag_text_content()
    
    def _search_for_keyword(self, tag, keywordObj, text):
        count = StringUtils.get_word_frequency(text, keywordObj.keyword)
        if (count > 0):
            self.page_statistics.update_count(tag, keywordObj, count)
                    
    def search_for_keywords(self, keywords):
        ''' Search for all the keywords in the accumulated text '''
        for tag, text in self.tag_text.items():
            if (text.strip() != "" ):
                for kwrd in keywords:
                    self._search_for_keyword(tag, kwrd, text)
            
        return self.page_statistics