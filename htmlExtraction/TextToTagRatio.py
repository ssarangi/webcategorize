import string
import matplotlib.pyplot as plt
from lxml.html import clean
from HTMLParser import HTMLParser

from numpy import array
from numpy import std
from scipy.cluster.vq import *
import pylab
import fileinput
pylab.close()

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
        
        # attr_len = 0        
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
        wfptr = open('output.html', 'w')
        wfptr.writelines(self.html)
        self._create_final_html()

    def _create_final_html(self):
        self.html_list = []
        for line in fileinput.input('output.html'):
            if (line.strip() != ""):
                self.html_list.append(line)
                
        self.line_TTR = []
        self.mean_TTR = []
        
    def compute_text_to_tag_ratio(self):
        line_no = 0
        for line in self.html_list:
            parser = TagParser()
            parser.feed(line)
            parser.reset()
            self.line_TTR.append(0)
            if (parser.tag_chars <= 0):
                self.line_TTR[line_no] = float(parser.text_chars)
            else:
                self.line_TTR[line_no] = float(parser.text_chars) / float(parser.tag_chars)
#            print line
#            print "Line No %s: ---> Tag Chars: %s ---> Text Chars: %s" % (line_no, parser.tag_chars, parser.text_chars)
            # raw_input()
            line_no += 1
            parser.close()

        self.total_lines = len(self.line_TTR)
        
    def _summation(self, i, rad):
        summation = 0
        for counter in range(i-rad, i + rad):
            if (counter >= 0 and counter < self.total_lines):
                summation += self.line_TTR[counter]
                
        return summation        
        
    def compute_mean_TTR(self, _radius):
        radius = _radius
        self.mean_TTR = [0 for i in range(0, self.total_lines)]
        for i in range(0, self.total_lines):
            self.mean_TTR[i] = self._summation(i, radius) / (2 * radius + 1)
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
        
def compute_standard_deviation(list_of_vals):
    # Numpy function to compute standard deviation
    return std(list_of_vals)

def threshold_clustering(mean_ttr, html_lines):
    std_dev = compute_standard_deviation(mean_ttr)
    print "Standard Deviation: %s" % std_dev
    print len(mean_ttr)
    print len(html_lines)
    for index in range(0, len(mean_ttr)):
        if (float(mean_ttr[index]) > float(std_dev)):
            print "-------------------------------------------------------------------------------"
            print html_lines[index]
            print "Val: %s ---> Standard Deviation: %s" % (mean_ttr[index], std_dev)
            print "-------------------------------------------------------------------------------"
            raw_input()

def _calculate_moving_avg(ttr, index, size):
    backward_start = (index - 1) - size
    backward_end   = (index - 1)
    forward_start  = (index + 1)
    forward_end    = (index + 1) + size
    
    backward_moving_avg = 0
    forward_moving_avg = 0
    
    for i in range(backward_start, backward_end + 1):
        if (i >= 0 and i < len(ttr)):
            backward_moving_avg += ttr[i]

    for i in range(forward_start, forward_end + 1):
        if (i >= 0 and i < len(ttr)):
            forward_moving_avg += ttr[i]

    return backward_moving_avg, forward_moving_avg    
        
def prediction_clustering(ttr, html_lines):
    ''' Pass the non-smoothed TTR list to this function '''
    content = ""
    size = 3
    for index in range(0, len(ttr)):
        backward_moving_avg, forward_moving_avg = _calculate_moving_avg(ttr, index, size)
        current_ttr = ttr[index]
        if (current_ttr > (backward_moving_avg + 1)):
            content += html_lines[index]
        
        if (current_ttr < (forward_moving_avg + 1)):
            index += size + 1
    
    print "----------------------------------------------------------------------------------------"
    print "                                      Content Found                                     "
    print "----------------------------------------------------------------------------------------"
    print content
    
def kmeans(ttr_arr):
    # Now convert this 1d-list into an array
    x_axis = range(0, len(ttr_arr))
    zipped_arr = zip(x_axis, ttr_arr)
    res, idx = kmeans2(array(zipped_arr), 3)
    # plot colored points
    colors = ([([0.4,1,0.4],[1,0.4,0.4],[0.1,0.8,1])[i] for i in idx])
    pylab.scatter(x_axis,ttr_arr, c=colors)
    pylab.scatter(res[:,0],res[:,1], marker='o', s = 500, linewidths=2, c='none')
    pylab.scatter(res[:,0],res[:,1], marker='x', s = 500, linewidths=2)
    pylab.savefig('kmeans.png')
    # print res, idx
        
        
if __name__ == "__main__":
    fptr = open('test.html', 'r')
    html = fptr.read()
    
    remove_tags = ["script", "remark", "style"]

    TTR = TextToTagRatio('test.html', remove_tags)
    TTR.compute_text_to_tag_ratio()
    TTR.compute_mean_TTR(2)
    # TTR.plot_TTR()
    threshold_clustering(TTR.mean_TTR, TTR.html_list)
    prediction_clustering(TTR.line_TTR, TTR.html_list)
    kmeans(TTR.mean_TTR)
    TTR.plot_mean_TTR()