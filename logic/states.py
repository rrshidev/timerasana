from aiogram.dispatcher.filters.state import State, StatesGroup


class Meditation(StatesGroup):
    time = State()
    
class PranaYama(StatesGroup):
    count = State()
    prana_time = State()
    reload = State()
    meditation_time = State()

class Asana(StatesGroup):
    count = State()
    asana_time = State()
    relax_time = State()
    shavasana_time = State()