from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


"""
model for database is nothing but a class that inherits from Base and we need to define tablename and columns
"""

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)



class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True) # index is way for us to increase performance, id will be unique
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id")) 
