from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)


class Client(Base):

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)


class Master(Base):

    __tablename__ = "masters"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Request(Base):

    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    device = Column(String)
    model = Column(String)
    problem = Column(String)
    status = Column(String)
    repair_time = Column(Integer)

    client_id = Column(Integer, ForeignKey("clients.id"))
    master_id = Column(Integer, ForeignKey("masters.id"))