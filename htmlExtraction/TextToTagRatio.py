from lxml import etree
import string
from lxml.html import clean
from HTMLParser import HTMLParser
from formatter import *

class TrackingParser(HTMLParser):
    """Try to keep accurate pointer of parsing location."""
    def __init__(self):
        HTMLParser.__init__(self)
        
    def parse_starttag(self, i):
        print "Parsing Start Tag"
        index = HTMLParser.parse_starttag(self, i)
        print "Index found: %s" % index
        return index

    def parse_endtag(self, i):
        print "Parsing End Tag"
        index = HTMLParser.parse_endtag(self, i)
        print "Index Found: %s" % index

class HtmlTokenParser:
    def __init__(self, html, removal_tag_list = []):
        # Clean the HTML
        cleaner = clean.Cleaner()
        cleaner.remove_tags = removal_tag_list
        # cleaned_html = cleaner.clean_html(html)
        cleaned_html = html
        
        # Dictionary of line numbers & tag chars
        self.text_to_tag_ratio = {}
        self.html_tree = etree.fromstring(cleaned_html)        
        
    def remove_tag(self, tag):                        
        for itag in self.html_tree.getiterator():
            if (itag.tag == tag):
                print "hello"
                # itag.drop_tree()

    def remove_empty_lines(self):
        for itag in self.html_tree.getiterator():
            if (itag.text != None and string.strip(itag.text) == ""):
                print "Hello"
                # itag.drop_tag()
            
    def display_tree(self):
        for element in self.html_tree.getiterator():
            print element.tag
    
    def display_html_content(self):
        print etree.tostring(self.html_tree, pretty_print = True)
        
    def generate_statistics(self):
        for node in self.html_tree.iter():
            if (node.text != None):
                text = node.text
                
            if (node.tail != None):
                text += node.tail
                
            text_length = len(text)
            self.text_to_tag_ratio[node.tag] = text_length
        
    def display_statistics(self):
        for key,val in self.text_to_tag_ratio.items():
            print "Key: %s Value: %s" % (key, val)
            
        
if __name__ == "__main__":
    fptr = open('test.html', 'r')
    html = fptr.read()
    
    # remove_tags = ["script", "remark"]
    # parser = HtmlTokenParser(html, remove_tags)
    # parser.remove_empty_lines()
    # parser.generate_statistics()
    # parser.display_statistics()  
    parser = TrackingParser()
    parser.feed(html)
    parser.close()
    
    # parser.display_tree()
    # parser.display_html_content()