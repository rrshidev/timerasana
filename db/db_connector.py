import sqlalchemy as database
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql.elements import and_, or_
from .models import *
from os import getenv
from sqlalchemy import select, Column, Integer, String, ForeignKey, Boolean, DateTime, SmallInteger, Text, DECIMAL, \
    text, func
from random import randint
from logic import states


# from logic.controller import get_phone


class Database:
    def __init__(self):
        engine = database.create_engine(getenv("DATABASE"))
        self.session = scoped_session(sessionmaker(bind=engine))

    def is_user_exist(self, tg_id):
        with self.session() as session:
            with session.begin():
                query = session \
                    .execute(select(User.tg_id) \
                             .where(User.tg_id.__eq__(tg_id))) \
                    .scalar()
                return bool(query)

    def add_user(self, user_data):
        with self.session() as session:
            with session.begin():
                data = User(**user_data)
                session.add(data)

    # def get_user_id(self, tg_id):
    #     with self.session() as session:
    #         with session.begin():
    #             query = session \
    #                 .execute(select(User.id) \
    #                          .where(User.tg_id.__eq__(tg_id))) \
    #                 .scalar()
    #             return query
    #
    # def get_wishes(self, tg_id):
    #     with self.session() as session:
    #         with session.begin():
    #             user_id = session \
    #                 .execute(select(User.id) \
    #                          .where(User.tg_id.__eq__(tg_id))) \
    #                 .scalar()
    #             query = session \
    #                 .execute(
    #                 select(Wishlist.id, Wishlist.name, Wishlist.gift_image, Wishlist.gift_link, Wishlist.is_reserved) \
    #                     .where(and_(Wishlist.user_id.__eq__(user_id), Wishlist.is_active.__eq__(1)))) \
    #                 .fetchall()
    #             return [dict(row) for row in query if query]
    #
    # def get_friend_wishes(self, friend_id):
    #     with self.session() as session:
    #         with session.begin():
    #             user_id = session \
    #                 .execute(select(User.id) \
    #                          .where(User.id.__eq__(friend_id))) \
    #                 .scalar()
    #             query = session \
    #                 .execute(
    #                 select(Wishlist.id, Wishlist.name, Wishlist.gift_image, Wishlist.gift_link, Wishlist.is_reserved) \
    #                     .where(and_(Wishlist.user_id.__eq__(user_id), Wishlist.is_active.__eq__(1)))) \
    #                 .fetchall()
    #             return [dict(row) for row in query if query]
    #
    # def get_ids(self):
    #     with self.session() as session:
    #         with session.begin():
    #             ids = session.execute(select(User.id)).fetchall()
    #             return ids
    #
    # def get_friend_data(self, id):
    #     with self.session() as session:
    #         with session.begin():
    #             user_data = session.query(User.fullname, User.birthdate, User.phone, User.id).filter(User.id == id).all()
    #             return user_data
    #
    # def check_id(self):
    #     with self.session() as session:
    #         with session.begin():
    #             ids = session.execute(select(User.id)).fetchall()
    #             random_id = randint(100000, 999999)
    #             if random_id not in ids:
    #                 return random_id
    #             else:
    #                 self.check_id(self)
    #
    # def add_user(self, user_data):
    #     with self.session() as session:
    #         with session.begin():
    #             data = User(**user_data)
    #             session.add(data)
    #
    # def add_gift(self, wishlist_data):
    #     with self.session() as session:
    #         with session.begin():
    #             data = Wishlist(**wishlist_data)
    #             session.add(data)
    #
    # def del_gift(self, gift_id):
    #     with self.session() as session:
    #         with session.begin():
    #             session.query(Wishlist) \
    #                 .where(Wishlist.id.__eq__(gift_id)) \
    #                 .update({Wishlist.is_active: 0})
    #
    # def book_gift(self, gift_id):
    #     with self.session() as session:
    #         with session.begin():
    #             session.query(Wishlist) \
    #                 .where(Wishlist.id.__eq__(gift_id)) \
    #                 .update({Wishlist.is_reserved: 1})
