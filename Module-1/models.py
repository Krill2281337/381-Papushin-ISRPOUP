from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):

    __tablename__ = "users"

    userID = Column(Integer, primary_key=True)
    fio = Column(String)
    phone = Column(String)
    login = Column(String)
    password = Column(String)
    type = Column(String)


class Request(Base):

    __tablename__ = "requests"

    requestID = Column(Integer, primary_key=True)
    startDate = Column(String)
    homeTechType = Column(String)
    homeTechModel = Column(String)
    problemDescription = Column(String)
    requestStatus = Column(String)
    completionDate = Column(String)
    repairParts = Column(String)
    masterID = Column(Integer)
    clientID = Column(Integer)


class Comment(Base):

    __tablename__ = "comments"

    commentID = Column(Integer, primary_key=True)
    message = Column(String)
    masterID = Column(Integer)
    requestID = Column(Integer)