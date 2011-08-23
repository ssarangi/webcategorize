import lxml.html
import string
from lxml.html import clean

class HtmlTokenParser:
    def __init__(self, html, removal_tag_list = []):
        # Clean the HTML
        cleaner = clean.Cleaner()
        cleaner.remove_tags = removal_tag_list
        cleaned_html = cleaner.clean_html(html)
        self.html_tree = lxml.html.fromstring(cleaned_html)        
        
    def remove_tag(self, tag):                        
        for itag in self.html_tree.getiterator():
            if (itag.tag == tag):
                itag.drop_tree()

    def remove_empty_lines(self):
        for itag in self.html_tree.getiterator():
            if (itag.text != None and string.strip(itag.text) == ""):
                itag.drop_tag()
            
    def display_tree(self):
        for element in self.html_tree.getiterator():
            print element.tag
    
    def display_html_content(self):
        print lxml.html.tostring(self.html_tree, pretty_print = True)
        
if __name__ == "__main__":
    fptr = open('test.html', 'r')
    html = fptr.read()
    
    remove_tags = ["script", "remark"]
    parser = HtmlTokenParser(html, remove_tags)
    parser.remove_empty_lines()
    
    # parser.display_tree()
    # parser.display_html_content()