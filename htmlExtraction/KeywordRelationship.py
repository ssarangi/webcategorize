class KeywordRelationship:
    def __init__(self, sl1, sl2, sl3, kwrd):
        self.sl1 = sl1
        self.sl2 = sl2
        self.sl3 = sl3
        self.keyword = kwrd
        
    def __str__(self):
        return self.sl1 + " -- " + self.sl2 + " -- " + self.sl3 + " -- " + self.keyword + "\n"