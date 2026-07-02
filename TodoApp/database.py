from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL='sqlite:///./todosapp.db'
# SQLALCHEMY_DATABASE_URL='postgresql://postgres:postgres@localhost/TodoApplicationDatabase'

# check_same_thread is to prevent accidently sharing same connection with different thread.
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


"""
a foreign key represent a relationship between two tables. It is a column in one table that referes
to the primary key of another table. its used to establish a link between the data in two tables.
most relational DBs use foreign key to maintain links between tables and ensure data integraty.
"""