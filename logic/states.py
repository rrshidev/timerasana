from aiogram.dispatcher.filters.state import State, StatesGroup


class User(StatesGroup):
    id = State()
    fullname = State()
    birthdate = State()
    phone = State()


class Friend(StatesGroup):
    friend_id = State()


class Gift(StatesGroup):
    wish_name_to_add = State()
    wish_name_to_del = State()
