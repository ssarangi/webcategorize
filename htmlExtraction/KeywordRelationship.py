class KeywordRelationship:
    ''' Class stores the relationship between all Service lines and keyword
        self.sl1 - Service Line 1
        self.sl2 - Service Line 2
        self.sl3 - Service Line 3
        self.keyword - Keyword
    '''
    def __init__(self, sl1, sl2, sl3, kwrd):
        ''' Constructor '''
        self.sl1 = sl1
        self.sl2 = sl2
        self.sl3 = sl3
        self.keyword = kwrd
        
    def __str__(self):
        ''' String representation for Keyword Relationship '''
        return self.sl1 + " -- " + self.sl2 + " -- " + self.sl3 + " -- " + self.keyword + "\n"