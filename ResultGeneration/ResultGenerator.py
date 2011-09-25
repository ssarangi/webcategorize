from globals.global_imports import *
from DB.UrlInterface import *
from ResultGeneration import HTML

class ResultGenerator:
    """ Generate the results in the form of an HTML Page """
    def __init__(self, db, output_file):
        self.db = db
        self.outputFile = output_file
        self.htmlHeaderFile = "ResultGeneration/header.html"
        self.fptr = open(self.outputFile, 'w')
        
        f = open(self.htmlHeaderFile, 'r')
        
        self.htmlHeader = f.read()
        self.fptr.write(self.htmlHeader)
        
        
    def __addCompanyHeader(self, companyName):
        html = "<p> %s </p>" % companyName
        print html
        return html
    
    def __addTagStatistics(self, tagObj):
        keywords = tagObj.keywords
        
        tableData = []
        for kwrdObj in keywords:
            tableData.append([kwrdObj.keyword, kwrdObj.count])
            
        htmlCode = HTML.table(tableData,
                              header_row=[tagObj.tag, 'Count'])
        
        print htmlCode
        return htmlCode
    
    def generateResults(self):
        urls = UrlInterface.analyzedURLs(self.db)
        print urls
        
        for url in urls:
            print url.address
            companyHeader = self.__addCompanyHeader(url.company)
            self.fptr.write(companyHeader)
            
            for tag in url.tags:
                tagHtml = self.__addTagStatistics(tag)
                self.fptr.write(tagHtml)
        
        self.fptr.close()

def ResultGeneratorMain():
    resgen = ResultGenerator(getUrlDB(), "ResultGeneration/results.html")
    print "Generating Results"
    resgen.generateResults()
    print "Done with Generation"