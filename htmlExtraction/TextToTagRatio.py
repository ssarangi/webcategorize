import string
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from lxml.html import clean
from HTMLParser import HTMLParser
import numpy as np

class TagParser(HTMLParser):
    """Try to keep accurate pointer of parsing location."""
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_chars = 0
        self.nontag_chars = 0

    def handle_starttag(self, tag, attrs):
        print "Found start tag: %s" % tag
        # accumulate the length of the attrs
        attr_len = 0
        for attr in attrs:
            attr_len += len(attr)
        
        # Now count the number of attribute values
        total_attrs = len(attrs) / 2
        attr_len += total_attrs  # Add the length of '=' removed by the parser
        
        tag_len = len(tag) + attr_len
        self.tag_chars += tag_len
    
    def handle_endtag(self, tag):
        print "Found end tag: %s" % tag
        self.tag_chars += len(tag)
        
    def handle_data(self, data):
        if (data.strip() != ""):
            print "Found data: %s" % data
            self.nontag_chars += len(data)
        
class TextToTagRatio:
    def __init__(self, html_file, removal_tag_list = []):
        ''' Initialize the Tag statistics '''
        # clean the html
        self.fptr = open(html_file, 'r')
        self.html = html
        cleaner = clean.Cleaner()
        cleaner.remove_tags = removal_tag_list
        cleaned_html = cleaner.clean_html(self.html)
        self.html = cleaned_html
        self.html_list = string.split(self.html, '\n')    
        self.parser = TagParser()
        self.line_stats = []
        
    def analyze_html(self):
        line_no = 0
        for line in self.html_list:
            self.parser.feed(line)
            self.parser.reset()
            self.line_stats.append(0)
            self.line_stats[line_no] = float(self.parser.tag_chars) / float(self.parser.nontag_chars)
            line_no += 1
            
        self.parser.close()
        
    def display_results(self):
        for e in self.line_stats:
            print e
    
    def plot_graph(self):
        r = range(0, len(self.line_stats) - 1)
        twoD = np.array([r, self.line_stats])
        n, bins, patches = plt.hist(twoD, len(self.line_stats), normed=1, facecolor='g', alpha=0.75)
        plt.grid(True)
        plt.show()
        
if __name__ == "__main__":
    fptr = open('test.html', 'r')
    html = fptr.read()
    
    remove_tags = ["script", "remark"]

    TTR = TextToTagRatio('test.html', remove_tags)
    TTR.analyze_html()
    TTR.plot_graph()