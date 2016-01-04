import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def seralize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
        }
 
class Category(Base):
    __tablename__ = 'categories'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture
        }
 
class Item(Base):
    __tablename__ = 'items'


    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    description = Column(String(250))
    category_id = Column(Integer,ForeignKey('categories.id'))
    category = relationship(Category) 
    picture = Column(String(250))

    @property
    def serialize(self):
       
       return {
           'id' : self.id,
           'name' : self.name,
           'description' : self.description,
           'picture': self.picture
       }



#engine = create_engine('postgres://mxjecomshjznqn:Ky9M6DXhTdpW3CV2sCFlUJExht@ec2-54-83-204-159.compute-1.amazonaws.com:5432/d6iivi4caaqog9')
#engine = create_engine('sqlite:///catalog.db')
#engine = create_engine('postgres://catalog:password@localhost/catalog')
engine = create_engine('postgres://catalog_test:8c33481e-9a13-4f23-89bd-8e81beecdd5d@localhost/catalog_test')
 

Base.metadata.create_all(engine)
