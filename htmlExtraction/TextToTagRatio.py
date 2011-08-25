import string
import matplotlib.pyplot as plt
from lxml.html import clean
from HTMLParser import HTMLParser

from numpy import array
from scipy.cluster.vq import whiten
from scipy.cluster.vq import vq

class TagParser(HTMLParser):
    """Try to keep accurate pointer of parsing location."""
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_chars = 0
        self.text_chars = 0

    def handle_starttag(self, tag, attrs):
        # print "Found start tag: %s" % tag
        # accumulate the length of the attrs
        attr_len = 0
        for attr_pair in attrs:
            attr_len += len(attr_pair[0]) + len(attr_pair[1]) + 2 + 1 # 2 for quotes, 1 for =
                
        tag_len = len(tag) + attr_len + 2
        self.tag_chars += tag_len        
        print "Tag Found: %s" % (tag)        
            
    def handle_endtag(self, tag):
        # print "Found end tag: %s" % tag
        self.tag_chars += len(tag) + 1 + 2 # For '/', '<' & '>'
        
    def handle_data(self, data):
        if (data.strip() != ""):
            print "Text Found: %s" % data
            self.text_chars += len(data)
        
class TextToTagRatio:
    def __init__(self, html_file, removal_tag_list = []):
        ''' Initialize the Tag statistics '''
        # clean the html
        self.fptr = open(html_file, 'r')
        self.html = self.fptr.read()
        cleaner = clean.Cleaner()
        cleaner.remove_tags = removal_tag_list
        cleaned_html = cleaner.clean_html(self.html)
        self.html = cleaned_html
        self.html_list = string.split(self.html, '\n')
        self.line_stats = []
        self.mean_TTR = []
        
    def analyze_html(self):
        line_no = 0
        for line in self.html_list:
            parser = TagParser()
            parser.feed(line)
            parser.reset()
            self.line_stats.append(0)
            if (parser.tag_chars <= 0):
                self.line_stats[line_no] = float(parser.text_chars)
            else:
                self.line_stats[line_no] = float(parser.text_chars) / float(parser.tag_chars)
            print line
            print "Line No %s: ---> Tag Chars: %s ---> Text Chars: %s" % (line_no, parser.tag_chars, parser.text_chars)
            # raw_input()
            line_no += 1
            parser.close()

        self.total_lines = len(self.line_stats)
        
    def _summation(self, i, rad):
        summation = 0
        for counter in range(i-rad, i + rad):
            if (counter >= 0 and counter < self.total_lines):
                summation += self.line_stats[counter]
        
        return summation        
        
    def compute_mean_TTR(self, _radius):
        radius = _radius
        self.mean_TTR = [0 for i in range(0, self.total_lines)]
        for i in range(0, self.total_lines):
            self.mean_TTR[i] = self._summation(i, radius)
            print self.mean_TTR[i]
        
    def display_results(self):
        for e in self.line_stats:
            print e
    
    def _plot_graph(self, plot_list, txt):
        r = range(0, len(plot_list))
        plt.plot(r, plot_list)
        plt.grid(True)
        plt.title(txt)
        plt.show()
        
    def plot_mean_TTR(self):
        self._plot_graph(self.mean_TTR, "Mean TTR")
        
    def plot_TTR(self):
        self._plot_graph(self.line_stats, "TTR")
        
def kmeans(oneDList):
    # Now convert this 1d-list into an array
    oneDArr = array(oneDList)
    whiten(oneDArr)
    res = vq(oneDArr, 5)
    print res
        
        
if __name__ == "__main__":
    fptr = open('test.html', 'r')
    html = fptr.read()
    
    remove_tags = ["script", "remark", "style"]

    TTR = TextToTagRatio('test.html', remove_tags)
    TTR.analyze_html()
    TTR.compute_mean_TTR(2)
    # TTR.plot_TTR()
    # TTR.plot_mean_TTR()
    kmeans(TTR.mean_TTR)