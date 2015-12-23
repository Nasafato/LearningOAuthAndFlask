import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

 
class Category(Base):
    __tablename__ = 'category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }
 
class Item(Base):
    __tablename__ = 'item'


    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    description = Column(String(250))
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category) 

    @property
    def serialize(self):
       
       return {
           'id' : self.id,
           'name' : self.name,
           'description' : self.description
       }



# engine = create_engine('postgres://mxjecomshjznqn:Ky9M6DXhTdpW3CV2sCFlUJExht@ec2-54-83-204-159.compute-1.amazonaws.com:5432/d6iivi4caaqog9')
engine = create_engine('sqlite:///catalog.db')
 

Base.metadata.create_all(engine)
