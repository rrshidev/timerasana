from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from logic.utils import get_moscow_datetime


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    fullname = Column(String, nullable=False)
    birthdate = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    tg_id = Column(Integer, nullable=False)
    tg_nickname = Column(String, nullable=False)
    register_datetime = Column(DateTime, default=get_moscow_datetime())
    is_admin = Column(Boolean, default=False)

class Wishlist(Base):
    __tablename__ = "wishlists"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    gift_image = Column(String, nullable=True)
    gift_link = Column(Integer, nullable=True)
    is_reserved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class GiftHistory(Base):
    __tablename__ = "gift_histories"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, nullable=False)
    gift_id = Column(Integer, ForeignKey("wishlists.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, default=None)
