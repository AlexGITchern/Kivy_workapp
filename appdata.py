from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String

engine = create_engine('sqlite:///appdata.db', echo=False)
base = declarative_base()


class Visit(base):
    __tablename__ = 'visit'
    id = Column(Integer, primary_key=True)
    month = Column(String)
    date = Column(String)
    type = Column(String)
    name = Column(String)
    address = Column(String)
    distance = Column(Integer)
    money = Column(Integer)


class Oil(base):
    __tablename__ = 'oil'
    id = Column(Integer, primary_key=True)
    month = Column(String)
    date = Column(String)
    pay = Column(Integer)
    comment = Column(String)


base.metadata.create_all(engine)