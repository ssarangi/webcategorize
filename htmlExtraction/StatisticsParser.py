import lxml.etree
import string

global debug

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

class HandleTarget:
    ''' Class to Handle the Meta Tags and other content lines we are looking for
        eg. h1, h2, etc '''
    def __init__(self):
        self.handle_tags = {"meta": self.handle_meta_tags,}   
                
    def handle_meta_tags(self, attribs):
        print "Handling Meta Tags"
        keywords, content = extract_key_value_pair(attribs, "name", "keywords", "content")
        content = string.split(content, ' ')
        return keywords, content        
        
    def handle(self, tag, attribs):
        global debug
        try:        
            return self.handle_tags[tag](attribs)
        except:
            if (debug):
                print "Unhandled Keyword: %s" % tag
            pass

class CollectorTarget:
    def __init__(self):
        self.events = []
        self.handle_target = HandleTarget()
        self.keywords = ""
        self.extracted_data = {}
        
    def start(self, tag, attribs):
        self.events.append("start %s %s" % (tag, attribs))
        key, res = self.handle_target.handle(tag, attribs)
        if (key != None):
            self.extracted_data[key] = res
                
    def end(self, tag):
        self.events.append("end %s" % tag)
        
    def data(self, data):
        self.events.append("data %r" % data)
        
    def comment(self, text):
        self.events.append("comment %s" % text)
        
    def close(self):
        self.events.append("close")
        return "closed!"
        
class StatisticsParser:
    def __init__(self, html_file):
        self.parser = lxml.etree.HTMLParser(remove_blank_text=True,
                                       remove_comments=True,
                                       target=CollectorTarget())
        
        self.tree = lxml.etree.parse(html_file, parser=self.parser)
        
        meta_tags = self.tree.getroot().
        print self.parser.target.handle_target.keywords
#        for event in self.parser.target.events:
#            print event
            

if __name__ == "__main__":
    global debug
    debug = False
    ss = StatisticsParser('test.html')
                                           