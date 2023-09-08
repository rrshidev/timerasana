from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from logic.utils import get_moscow_datetime


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tg_id = Column(Integer, nullable=False)
    tg_nickname = Column(String, nullable=False)
    register_datetime = Column(DateTime, default=get_moscow_datetime())


class Asana(Base):
    __tablename__ = "asana"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, ForeignKey("users.tg_id"), nullable=False)
    name = Column(String, nullable=False)
    time = Column(Integer, nullable=False)
    is_reserved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class Pranayma(Base):
    __tablename__ = "pranayama"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, ForeignKey("users.tg_id"), nullable=False)
    time = Column(Integer, nullable=False)
    is_reserved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
