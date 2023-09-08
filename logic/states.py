from aiogram.dispatcher.filters.state import State, StatesGroup


class Meditation(StatesGroup):
    time = State()


class PranaYama(StatesGroup):
    name = State()
    time = State()


class Asana(StatesGroup):
    number = State()
    time = State()
    delay = State()
