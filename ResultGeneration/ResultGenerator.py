from globals.global_imports import *
from DB.UrlInterface import *
from ResultGeneration import HTML
from DB.alchemy import *
from DB.KeywordInterface import *

class ResultGenerator:
    """ Generate the results in the form of an HTML Page """
    def __init__(self, urlDB, keywordDB, output_file):
        self.urlDB = urlDB
        self.keywordDB = keywordDB
        self.outputFile = output_file
        self.htmlHeaderFile = "ResultGeneration/header.html"
        self.fptr = open(self.outputFile, 'w')
        
        f = open(self.htmlHeaderFile, 'r')
        
        self.htmlHeader = f.read()
        self.fptr.write(self.htmlHeader)
        self.footer = "</meta></head></html>"
        
    def __addCompanyHeader(self, companyName):
        html = "<p> %s </p>" % companyName
        return html
    
    def __addTagStatistics(self, tagObj):
        keywords = tagObj.keywords
        
        # print keywords
        
        tableData = []
        for kwrdObj in keywords:
            # Get the original keyword object
            origKeywordObj = KeywordInterface.getKeywordByID(self.keywordDB, kwrdObj.keywordTable_index)
            serviceLine = origKeywordObj.serviceLine
            sl3 = serviceLine.serviceLine3
            sl2 = serviceLine.serviceLine2
            sl1 = serviceLine.serviceLine1
            text = kwrdObj.keyword + "<br>" + sl1 + "<br>" + sl2 + "<br>" + sl3
            tableData.append([text, kwrdObj.count])
        
            
        htmlCode = HTML.table(tableData,
                              header_row=[tagObj.tag, 'Count'])
        
        return htmlCode
    
    def generateResults(self):
        urls = UrlInterface.analyzedURLs(self.urlDB)
        
        for url in urls:
            # print len(url.tags)
            companyHeader = self.__addCompanyHeader(url.company.name)
            self.fptr.write(companyHeader)
            
            for tag in url.tags:
                tagHtml = self.__addTagStatistics(tag)
                self.fptr.write(tagHtml)
        
        self.fptr.write(self.footer)
        self.fptr.close()

def ResultGeneratorMain():
    resgen = ResultGenerator(getUrlDB(), getKeywordDB(), "ResultGeneration/results.html")
    print "Generating Results"
    resgen.generateResults()
    print "Done with Generation"