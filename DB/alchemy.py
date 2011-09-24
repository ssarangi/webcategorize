from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref

KeywordBase = declarative_base()
URLBase = declarative_base()

class Alchemy:
    def __init__(self, filename, base, username="", password=""):
        self.filename = filename
        self.username = username
        self.password = password
        self.engine = create_engine(('sqlite:///%s' % (filename)))
        self._Session = sessionmaker(bind=self.engine)
        self.session = self._Session()
        self.base = base
        
    def createTable(self):
        print "Creating Table"
        self.base.metadata.create_all(self.engine)
        
#    def addObject(self, obj):
#        self.session.add(obj)
#        
#    def addAll(self, objList):
#        self.session.add_all(objList)
#        
#    def commit(self):
#        self.session.commit()
        
class ServiceLine1(KeywordBase):
    __tablename__ = 'ServiceLine1'
    
    id = Column(Integer, primary_key=True, nullable=False)
    keyword = Column(String, unique=True)
    
    def __init__(self, kwrd):
        self.keyword = kwrd
    
    @staticmethod    
    def tableName():
        return ServiceLine1.__tablename__
    
    def __repr__(self):
        return  "<Service Line 1: (%i,'%s')>" % (self.id, self.keyword)
    
    
class ServiceLine2(KeywordBase):
    __tablename__ = 'ServiceLine2'
    
    id = Column(Integer, primary_key=True, nullable=False)
    keyword = Column(String, unique=True)
    sl1_index = Column(Integer, ForeignKey('ServiceLine1.id'))
    
    serviceLine1 = relationship('ServiceLine1', backref='serviceline2_list')

    def __init__(self, kwrd, sl1_id):
        self.keyword = kwrd
        self.sl1_index = sl1_id

    @staticmethod
    def tableName():
        return ServiceLine2.__tablename__

    def __repr__(self):
        return  "<Service Line 2: (%i,'%s')>" % (self.id, self.keyword)

class ServiceLine3(KeywordBase):
    __tablename__ = 'ServiceLine3'
    
    id = Column(Integer, primary_key=True, nullable=False)
    keyword = Column(String, unique=True)
    sl2_index = Column(Integer, ForeignKey('ServiceLine2.id'))
    
    serviceLine2 = relationship('ServiceLine2', backref='serviceline3_list')

    def __init__(self, kwrd, sl2_id):
        self.keyword = kwrd
        self.sl2_index = sl2_id

    @staticmethod
    def tableName():
        return ServiceLine3.__tablename__

    def __repr__(self):
        return  "<Service Line 3: (%i,'%s')>" % (self.id, self.keyword)

class KeywordTable(KeywordBase):
    __tablename__ = 'KeywordTable'    
    
    id = Column(Integer, primary_key=True, nullable=False)
    keyword = Column(String)
    sl3_index = Column(Integer, ForeignKey('ServiceLine3.id'))
    
    serviceLine3 = relationship('ServiceLine3', backref='keywords_list')
    
    def __init__(self, kwrd, sl3_id):
        self.keyword = kwrd
        self.sl3_index = sl3_id
    
    @staticmethod    
    def tableName():
        return KeywordTable.__tablename__
    
    def __repr__(self):
        return  "<Keyword Table: (%i,'%s')>" % (self.id, self.keyword)
    
class Relationship(KeywordBase):
    __tablename__ = 'Relationship'
    
    id = Column(Integer, primary_key=True)
    sl1_index = Column(Integer, ForeignKey('ServiceLine1.id'))
    sl2_index = Column(Integer, ForeignKey('ServiceLine2.id'))
    sl3_index = Column(Integer, ForeignKey('ServiceLine3.id'))
    keyword_index = Column(Integer, ForeignKey('KeywordTable.id'))
    
    keyword = relationship("KeywordTable", uselist=False, backref="relationship")
    serviceLine1 = relationship("ServiceLine1", backref="relationships")
    serviceLine2 = relationship("ServiceLine2", backref="relationships")
    serviceLine3 = relationship("ServiceLine3", backref="relationships")
    
    
    def __init__(self, sl1_id, sl2_id, sl3_id, kwrd_id):
        self.sl1_index = sl1_id
        self.sl2_index = sl2_id
        self.sl3_index = sl3_id
        self.keyword_index = kwrd_id
    
    @staticmethod    
    def tableName():
        return Relationship.__tablename__    
    
    def __repr__(self):
        return  "<Relationship: (%i, %i, %i, %i, %i)>" % (self.id, self.sl1_index, self.sl2_index,
                                                          self.sl3_index, self.keyword_index)
    
    
class Company(URLBase):
    __tablename__ = 'Company'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    crawled = Column(Integer, default=0)
    
    def __init__(self, name, base_url, crawled=0):
        self.name = name
        self.base_url = base_url
        self.crawled = crawled

    @staticmethod        
    def tableName():
        return Company.__tablename__        

    def __repr__(self):
        return  "<Company: (%i,'%s','%s',%i)>" % (self.id, self.name, self.base_url,
                                                    self.crawled)
    
    
class URL(URLBase):
    __tablename__ = 'URL'
    
    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)
    content = Column(String)
    analyzed = Column(Integer, default=0)
    company_index = Column(Integer, ForeignKey('Company.id'))

    company = relationship("Company", backref=backref('urls', order_by=id))
    
    def __init__(self, address, content, analyzed, company_index):
        self.address = address
        self.content = content
        self.analyzed = analyzed
        self.company_index = company_index

    @staticmethod
    def tableName():
        return URL.__tablename__    

    def __repr__(self):
        return  "<Relationship: (%i,'%s','%s','%i','%i')>" % (self.id, self.address, self.content,
                                                              self.analyzed, self.company_index)

class TagStats(URLBase):
    __tablename__ = 'TagStats'
    
    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False, unique=True)
    url_index = Column(Integer, ForeignKey('URL.id'))
    
    url = relationship("URL", backref=backref('tags'))
    
    def __init__(self, tag, url_id):
        self.tag = tag
        self.url_index = url_id
    
    @staticmethod
    def tableName():
        return TagStats.__tablename__        
    
    def __repr__(self):
        return "<Tag: (%i, %s)>" % (self.id, self.tag)
    
def KeywordStats(URLBase):
    __tablename__ = 'KeywordStats'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String, nullable=False)
    count = Column(Integer, nullable=False, default=0)
    tagStat_index = Column(Integer, ForeignKey('TagStats.id'))
    
    tag = relationship("TagStats", backref=backref('keywords', order_by=count))
    
    def __init__(self, keyword, count, tag_id):
        self.keyword = keyword
        self.count = count
        self.tagStat_index = tag_id
    
    @staticmethod
    def tableName():
        return KeywordStats.__tablename__    
            
    def __repr__(self):
        return "<Keyword: (%i, %s, %i)>" % (self.id, self.keyword, self.count)