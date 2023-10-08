from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, Date, Time, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from logic.utils import get_moscow_datetime


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
  #  id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    tg_nickname = Column(String, default=None)
    register_datetime = Column(DateTime, default=get_moscow_datetime())


class Asana(Base):
    __tablename__ = "asana"
    #id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, ForeignKey("users.tg_id"), primary_key=True)
    name = Column(String, ForeignKey("users.name"), nullable=False)
    count = Column(Integer, nullable=False)
    asana_time = Column(Integer, nullable=False)
    relax_time = Column(Integer, nullable=False)
    shavasana_time = Column(Integer, nullable=False)   


class Pranayma(Base):
    __tablename__ = "pranayama"
    tg_id = Column(BigInteger, ForeignKey("users.tg_id"), primary_key=True)
    name = Column(String, ForeignKey("users.name"), nullable=False)
    count = Column(Integer, nullable=False)
    prana_time = Column(Integer, nullable=False)
    reload = Column(Integer, nullable=False)
    meditation_time = Column(Time, nullable=False)
  
