from sqlalchemy import  create_engine,Column, Integer, String, DateTime, Boolean
from utils import filename_by_guid
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



engine = create_engine('sqlite:///statistics.sqlite')
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Picture(Base):


    __tablename__ = 'pictures'


    id = Column(Integer, primary_key = True, autoincrement = True)
    guid = Column(String)
    filename = Column(String)
    cstart= Column(DateTime)
    cfinish= Column(DateTime)
    uploaded = Column(Boolean)
    ustart= Column(DateTime)
    ufinish= Column(DateTime)
    

    def __init__(self,guid,timestart,timefinish):

        self.guid = guid
        self.filename = filename_by_guid(guid)
        self.timestart = timestart
        self.timefinish = timefinish
        self.uploaded = False
        


    def mark_uploaded(self,ustart,ufinish):

        if self.uploaded:
            raise NameError('%s was already uploaded',self.filename)
            
        self.uploaded =True

        self.ustart = ustart
        self.ufinish = ufinish
        

Base.metadata.create_all(engine)    




