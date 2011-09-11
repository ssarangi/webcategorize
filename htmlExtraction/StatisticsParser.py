import lxml.etree
import string, StringIO
import sys

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
                 "title"                 
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

def get_word_frequency(string, keyword):
    ''' Calculate the Keyword Statistics '''
    return len(string.split(keyword)) - 1


class TagStatistics:
    def __init__(self, tag):
        self.tag = ""
        self.tag_stats = {}
    
    def add_keyword(self, kwrd, count):
        self.tag_stats[kwrd] = count
        
    def get_keyword_count(self, kwrd):
        try:
            return self.tag_stats[kwrd]
        except:
            return 0
        
    def __str__(self):
        ret_str =  "Statistics for Tag: " + self.tag + "\n"
        for k, v in self.tag_stats.items():
            ret_str +=  k + ": " + str(v) + "\n"
            
        return ret_str
        
class PageStatistics:
    def __init__(self, url):
        self.url = url
        self.tag_statistics = {}
        
    def add_tag(self, tag):
        tag_stats = TagStatistics(tag)
        self.tag_statistics[tag] = tag_stats
        
    def update_count(self, tag, keyword, count):
        try:
            self.tag_statistics[tag].add_keyword(keyword, count)
        except:
            pass
        
    def __str__(self):
        ret_str = ""
        for tag, tag_stats in self.tag_statistics.items():
            ret_str += str(tag_stats)
            
        return ret_str

class HandleTarget:
    ''' Class to Handle the Meta Tags and other content lines we are looking for
        eg. h1, h2, etc '''
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
                            "title" : self.handle_generic
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
#        try:
#            key, res = self.handle_target.handle(tag, attribs)
#        except:
#            print "Unexpected error:", sys.exc_info()[0]
#            
#        if (key != None and res != None):
#            self.extracted_data[key] = res
                
    def end(self, tag):
        self.events.append("end %s" % tag)
        
    def data(self, data):
        self.events.append("data %r" % data)
        
    def comment(self, text):
        self.events.append("comment %s" % text)
        
    def close(self):
        self.events.append("close")
        # return "closed!"
        
class StatisticsParser:
    def __init__(self, html_file):
        self.collector_parser = lxml.etree.HTMLParser(remove_blank_text=True,
                                                      remove_comments=True,
                                                      target=CollectorTarget())
        
        self.parser = lxml.etree.HTMLParser(remove_blank_text=True,
                                            remove_comments=True)

        
        fptr = open(html_file, 'r')
        html = fptr.read()
        
        self.tree = lxml.etree.parse(StringIO.StringIO(html), parser=self.parser)
        # self.tree = lxml.etree.parse(html_file, parser = self.collector_parser)
        doc_info = self.tree.docinfo
        self.encoding = doc_info.encoding
        self.page_statistics = PageStatistics(url='index.html')
        self.tag_text = {}
        
    def accumulate_text_from_tags(self):
        global html_tag_list
        handle = HandleTarget()
        root = self.tree.getroot()
        for element in root.iter():
            handle.handle_tag(element.tag, None, element)
        
        self.tag_text = handle.return_tag_text_content()
    
    def _search_for_keyword(self, keyword, tag, text):
        count = get_word_frequency(text, keyword)
        self.page_statistics.add_tag(tag)
        self.page_statistics.update_count(tag, keyword, count)
                    
    def search_for_keywords(self, keywords):
        ''' Search for all the keywords in the accumulated text '''
        for tag, text in self.tag_text.items():
            for kwrd in keywords:
                self._search_for_keyword(kwrd, tag, text)
            
        
        print self.page_statistics
            
if __name__ == "__main__":
    global debug
    debug = False
    ss = StatisticsParser('test.html')
    keywords = ["is", "and"]
    ss.accumulate_text_from_tags()
    ss.search_for_keywords(keywords)