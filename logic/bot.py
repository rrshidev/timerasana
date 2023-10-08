import asyncio
import logging
from email import message
from aiogram.types import Message
from os import getenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters import Text
from aiogram.utils import callback_data
from aiogram.utils.exceptions import *
from logic import markups
from .decorators import *
from .middlewares import LoggingMiddleware, ThrottlingMiddleware
from .controller import Controller
from .messages import timer_message
import const.const as const
from . import states
from db.db_connector import Database
import re

# ! temp
from dotenv import load_dotenv



load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=getenv("BOT_TOKEN"))
Bot.set_current(bot)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(ThrottlingMiddleware(dispatcher=dp))
c = Controller(bot=bot)


# Стартовая команда, запускает бот.
@dp.message_handler(commands='start')
@dp.message_handler(Text(equals='Назад'))
async def command_start_process(message: Message):
    print("command_start_process")
    response = await c.command_start(message=message)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# Ловим бесплатный раздел
@dp.message_handler(Text(equals='Выбрать тип практики'))
@dp.message_handler(Text(equals='Закончить практику'))
async def choice_of_practice_process(message: Message):
    print("choice_of_practice_process")
    response = await c.choice_of_practice(message=message)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# Ловим медитацию
@dp.message_handler(Text(equals='Медитация'), state='*')
async def meditation_process(message: Message, state: FSMContext):
    print("meditation_process")
    response = await c.meditation(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# Ловим количество минут для медитации
@dp.message_handler(filters.StateFilter(dp, states.Meditation.time))
@dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.Meditation.time)
async def get_time_process(message: Message, state: FSMContext):
    const.timer_stopped = False
    const.timer_paused = False
    print('hello world', const.timer_paused, const.timer_stopped) # отладка в консоле
    time_pattern = r'[+]?\d+$'
    count = int(message.text)
    const.timer_total = count
    if re.fullmatch(time_pattern, message.text):
        edit_message = await message.answer(
            text=timer_message(total=count),
            reply_markup=markups.practice_stop_process(),
        )
        asyncio.create_task(c.get_time(message=edit_message, count=count))
        await state.finish()
    else:
        await message.reply(text='Не похоже на количество минут. Введи любое целое число.',
                            reply_markup = markups.step_back_markup())
        
    

#Get callback Pause from markup
@dp.callback_query_handler(lambda c: c.data == 'Pause')
async def callback_pause(callback_query: types.CallbackQuery):
    print('Pause world', const.timer_paused, const.timer_stopped)
    if not const.timer_paused:
        const.timer_paused = True
        await callback_query.message.edit_text(
            text=timer_message(
                total=const.timer_total,
                rest=const.timer_rest,
                status=False,
            ),
            reply_markup=markups.practice_continue_process(),
        )


#Get callback Resume markup
@dp.message_handler(commands="resume")
@dp.callback_query_handler(lambda c: c.data == 'Resume')
async def callback_resume(callback_query: types.CallbackQuery):
    print('Resume world', const.timer_paused, const.timer_stopped)

    if const.timer_paused:
        const.timer_paused = False
        await callback_query.message.edit_text(
            text=timer_message(
                total=const.timer_total,
                rest=const.timer_rest,
                status=True,
            ),
            reply_markup=markups.practice_stop_process(),
        )


#get callback Stop markup
@dp.callback_query_handler(lambda c: c.data == 'Stop')
async def cmd_stop(callback_query: types.CallbackQuery):
    print('Stop world', const.timer_paused, const.timer_stopped)
    if not const.timer_stopped:
        const.timer_stopped = True
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Таймер остановлен.")


# Ловим пранаяму
@dp.message_handler(Text(equals='Пранаяма'), state='*')
async def pranayama(message: Message, state: FSMContext):
    response = await c.pranayama(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# Ловим количество пранаям
@dp.message_handler(Text(equals='Назад'))
@dp.message_handler(filters.StateFilter(dp, states.PranaYama.count))
@dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.PranaYama.count)
async def prana_time_process(message: Message, state: FSMContext):
    response = await c.prana_time(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# get time of pranayam
@dp.message_handler(filters.StateFilter(dp, states.PranaYama.prana_time))
@dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.PranaYama.prana_time)
async def get_prana_time_process(message: Message, state: FSMContext):
    response = await c.get_reload_time(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
    

#get reload time
@dp.message_handler(filters.StateFilter(dp, states.PranaYama.reload))
@dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.PranaYama.reload)
async def get_reload_time_process(message: Message, state: FSMContext):
    response = await c.get_medidation_time(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


#get meditation time
@dp.message_handler(filters.StateFilter(dp, states.PranaYama.meditation_time))
@dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.PranaYama.meditation_time)
async def get_meditation_time_process(message: Message, state: FSMContext):
    response = await c.practice_time(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# Ловим асану
@dp.message_handler(Text(equals='Асана'), state='*')
async def asana_process(message: Message, state: FSMContext):
    response = await c.asana(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)

# Ловим количество асан
# Ловим asana_time
@dp.message_handler(filters.StateFilter(dp, states.Asana.count))
@dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.Asana.count)
async def get_asana_time_process(message: Message, state: FSMContext):
    response = await c.get_asana_time(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# get time of relax
@dp.message_handler(filters.StateFilter(dp, states.Asana.asana_time))
@dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.Asana.asana_time)
async def get_relax_time_process(message: Message, state: FSMContext):
    response = await c.get_relax_time(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)

# get time of shavasana
@dp.message_handler(filters.StateFilter(dp, states.Asana.relax_time))
@dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.Asana.relax_time)
async def get_shavasana_time_process(message: Message, state: FSMContext):
    response = await c.get_shavasana_time(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
    
#get start of asana practice
@dp.message_handler(filters.StateFilter(dp, states.Asana.shavasana_time))
@dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.Asana.shavasana_time)
async def startasana_process(message: Message, state: FSMContext):
    response = await c.startasana(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
    
# # Ловим имя и фамилию пользователя. Предлагаем ввести дату рождения.
# @dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')),
#                     # lambda msg: not c.check_user_for_existence(msg.from_user_id),
#                     state=states.User.fullname)
# async def get_name_process(message: Message, state: FSMContext):
#     response = await c.get_name(message=message, state=state)
#     await message.reply(text=response['text'],
#                         reply_markup=response['markup'],
#                         parse_mode='HTML',
#                         reply=False)
#
#
# # Ловим дату рождения. Предлагаем ввести номер телефона. Реализуем возврат к вводу даты рождения.
# @dp.message_handler(Text(equals="Назад к вводу даты рождения"), state='*')
# @dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.User.birthdate)
# async def get_birthdate_process(message: Message, state: FSMContext):
#     response = await c.get_birthdate(message=message, state=state)
#     await message.reply(text=response['text'],
#                         reply_markup=response['markup'],
#                         parse_mode='HTML',
#                         reply=False)
#
#
# # Ловим номер телефона. Предлагаем создать список подарков. Реализуем возврат к вводу номера из последующего меня
# @dp.message_handler(Text(equals="Не хочу давать свой номер!"))
# @dp.message_handler(Text(equals="Назад к вводу номера телефона"), state='*')
# @dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/', 'Да, все верно')), state=states.User.phone)
# async def get_phone_process(message: Message, state: FSMContext):
#     response = await c.get_phone(message=message, state=state)
#     await message.reply(text=response['text'],
#                         reply_markup=response['markup'],
#                         parse_mode='HTML',
#                         reply=False)
#
#
# # Ловим утвердительный ответ из предыдущего меню и добавляем пользователя в БД, либо нажатие на кнопку в начальном меню,
# # если пользователь был создан ранее.
#
# @dp.message_handler(Text(equals="Да, все верно"), state='*')
# @dp.message_handler(Text(equals="Просмотреть свой список подарков"), state='*')
# @dp.message_handler(Text(equals="К списку подарков..."), state='*')
# async def get_wishes_process(message: Message, state: FSMContext):
#     if message.text == 'Да, все верно':
#         await c.add_user_to_db(message=message, state=state)
#     response = await c.get_wishes(message=message, state=state)
#     await message.reply(text=response['text'],
#                         reply_markup=response['markup'],
#                         parse_mode='HTML',
#                         reply=False)
#
#
# # Формируем список подарков
# @dp.message_handler(Text(equals='Создать подарок'), state='*')
# async def create_wish_list_process(message: Message, state: FSMContext):
#     response = await c.create_wish_list(state=state)
#     await message.reply(text=response['text'],
#                         reply_markup=response['markup'],
#                         parse_mode='HTML',
#                         reply=False)
#
#
# # Ловим название подарка и кладём в БД
# @dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/')), state=states.Gift.wish_name_to_add)
# async def add_point_in_list_process(message: Message, state: FSMContext):
#     response = await c.add_point_in_list(message=message, state=state)
#     await message.reply(text=response['text'],
#                         reply_markup=response['markup'],
#                         parse_mode='HTML',
#                         reply=False)
#
#
# # Ловим callback от кнопки УДАЛИТЬ подарок
# @dp.callback_query_handler(WishToDelete.filter(), state='*')
# async def del_point_from_list_process(query: CallbackQuery, callback_data: dict):
#     response = await c.del_point_from_list(с, wish_id=callback_data['wish_id'])
#     await bot.send_message(chat_id=query.from_user.id,
#                            text=response['text'],
#                            reply_markup=response['markup'])
#
#
# # Ловим callback от кнопки ЗАБРОНИРОВАТЬ подарок
# @dp.callback_query_handler(WishToBook.filter(), state='*')
# async def book_point_from_list_process(query: CallbackQuery, callback_data: dict):
#     response = await c.book_point_from_list(query=query, wish_id=callback_data['wish_id'])
#     await bot.send_message(chat_id=query.from_user.id,
#                            text=response['text'],
#                            reply_markup=response['markup'])
#
#
# # Просим ввести имя и фамилию пользователя.  Реализуем возврат к вводу имени и фамилии из последующего меню
# @dp.message_handler(Text(equals='Назад к вводу имени'), state='*')
# @dp.message_handler(Text(equals='Создать список подарков'))
# async def enter_fullname_process(message: Message, state: FSMContext):
#     response = await c.enter_fullname(state=state)
#     await message.reply(text=response['text'],
#                         reply_markup=response['markup'],
#                         parse_mode='HTML',
#                         reply=False)
#
#
# # Просим ввести информацию для поиска друга в БД, чтобы получить его лист желаний
# @dp.message_handler(Text(equals="Нет"))
# @dp.message_handler(Text(equals='Узнать подарки друга'))
# async def enter_friend_data_process(message: Message, state: FSMContext):
#     response = await c.enter_friend_data(state=state)
#     await message.reply(text=response['text'],
#                         reply_markup=response['markup'],
#                         parse_mode='HTML',
#                         reply=False)
#
#
# # Ловим уникальный ID друга
# @dp.message_handler(lambda msg: msg.text.isdigit(), state=states.Friend.friend_id)
# @dp.message_handler(lambda msg: not msg.text.startswith(('Назад', '/', 'Да, это он!', 'Нет')))
# async def search_friend_process(message: Message, state: FSMContext):
#     response = await c.search_friend(message=message, state=state)
#     await message.reply(text=response['text'],
#                         reply_markup=response['markup'],
#                         parse_mode='HTML',
#                         reply=False)
#
#
# # Ловим подтверждение личности друга
# @dp.message_handler(Text(equals='Да, это он!'))
# async def get_friend_wishes_process(message: Message):
#     response = await c.get_friend_wishes(message=message)
#     await message.reply(text=response['text'],
#                         reply_markup=response['markup'],
#                         parse_mode='HTML',
#                         reply=False)
