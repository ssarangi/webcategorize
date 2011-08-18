from plinewriter import *
from tparser import *
from formatter import *

def extract_text(html):
    writer = LineWriter()
    
    formatter = AbstractFormatter(writer)
    
    pparser = TrackingParser(writer, formatter)
    
    pparser.feed(html)
    pparser.close()

    return writer.output()    
    
if __name__ == "__main__":
    html_file = open('test.html', 'r')
    html = html_file.read()
    extract_text(html)