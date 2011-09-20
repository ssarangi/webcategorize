from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class Alchemy:
    def __init__(self, filename, username="", password=""):
        self.filename = filename
        self.username = username
        self.password = password
        self.engine = create_engine(('sqlite:///%s' % (filename)))
        self._Session = sessionmaker(bind=self.engine)
        self.session = self._Session()
        
    def createTable(self):
        Base.metadata.create_all(self.engine)
        
    def addObject(self, obj):
        self.session.add(obj)
        
    def addAll(self, objList):
        self.session.add_all(objList)
        
    def commit(self):
        self.session.commit()
        
        
class ServiceLine1(Base):
    __tablename__ = 'service_line_1'
    
    id = Column(Integer, primary_key=True, nullable=False)
    keyword = Column(String, unique=True)
    
    def __repr__(self):
        return  "<Service Line 1: ('%s','%s')>" % (str(self.id), self.keyword)
    
class ServiceLine2(Base):
    __tablename__ = 'service_line_2'
    
    id = Column(Integer, primary_key=True, nullable=False)
    keyword = Column(String, unique=True)

    def __repr__(self):
        return  "<Service Line 2: ('%s','%s')>" % (str(self.id), self.keyword)

class ServiceLine3(Base):
    __tablename__ = 'service_line_3'
    
    id = Column(Integer, primary_key=True, nullable=False)
    keyword = Column(String, unique=True)

    def __repr__(self):
        return  "<Service Line 3: ('%s','%s')>" % (str(self.id), self.keyword)

class KeywordTable(Base):
    __tablename__ = 'keyword_table'    
    
    id = Column(Integer, primary_key=True, nullable=False)
    keyword = Column(String, unique=True)

    def __repr__(self):
        return  "<Keyword Table: ('%s','%s')>" % (str(self.id), self.keyword)
    
class Relationship(Base):
    __tablename__ = 'relationship'
    
    id = Column(Integer, primary_key=True)
    sl1_index = Column(Integer, ForeignKey('service_line_1.id'))
    sl2_index = Column(Integer, ForeignKey('service_line_2.id'))
    sl3_index = Column(Integer, ForeignKey('service_line_3.id'))
    keyword_index = Column(Integer, ForeignKey('keyword_table.id'))
    
    def __repr__(self):
        return  "<Relationship: ('%s','%s','%s','%s','%s')>" % (str(self.id), str(self.sl1_index), str(self.sl2_index),
                                                                str(self.sl3_index), str(self.keyword_index))
    
    
class Company(Base):
    __tablename__ = 'Company'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    crawled = Column(Integer, default=0)
    
    urls = relationship("URL")    

    def __init__(self, name, base_url, crawled=0):
        self.name = name
        self.base_url = base_url
        self.crawled = crawled

    def __repr__(self):
        return  "<Company: ('%s','%s','%s','%s')>" % (str(self.id), self.name, self.base_url,
                                                      str(self.crawled))
    
    
class URL(Base):
    __tablename__ = 'URL'
    
    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)
    content = Column(String)
    analyzed = Column(Integer, default=0)
    company_index = Column(Integer, ForeignKey('Company.id'))

    company = relationship("Company", backref=backref('URL', order_by=id))
    
    def __init__(self, address, content, analyzed, company_index):
        self.address = address
        self.content = content
        self.analyzed = analyzed
        self.company_index = company_index

    def __repr__(self):
        return  "<Relationship: ('%s','%s','%s','%s','%s')>" % (str(self.id), self.address, self.content,
                                                                str(self.company_index))
