from datetime import datetime
from aiogram import types
from aiogram.types import callback_query, InlineKeyboardButton, InlineKeyboardMarkup

import const.classes
from db.db_connector import Database
from const.const import *
from . import markups
import re
import time
from . import states
import random
from sqlalchemy import DateTime
from .utils import get_callback
from . import memory


class Controller:
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    async def command_start(self, message):
        name = message.from_user.first_name
        tg_id = message.from_user.id
        tg_nickname = message.from_user.username
        user_data = {
            'name': name,
            'tg_id': tg_id,
            'tg_nickname': tg_nickname
        }
        if self.db.is_user_exist(tg_id=message.from_user.id):
            markup = markups.start_markup()
            text = f'<b>Намаскар, {name}! Я таймер-бот для йогических практик!\n\n\nДА ПРИБУДЕТ С ТОБОЙ СИЛА!</b>'
            return dict(text=text, markup=markup)
        else:
            self.db.add_user(user_data=user_data)
            markup = markups.start_markup()
            text = f'<b>Намаскар, {name}! Я таймер-бот для йогических практик!\n\n\nДА ПРИБУДЕТ С ТОБОЙ СИЛА!</b>'
            return dict(text=text, markup=markup)

    async def choice_of_practice(self, message):
        markup = markups.choose_practice()
        text = 'Выбери раздел и следуй инструкциям. \nЖелаю хорошей практики...'
        return dict(text=text, markup=markup)

    async def meditation(self, message, state):
        markup = markups.step_back_markup()
        text = 'Введи количество минут для медитации и начинай практику.\n' \
               'Я прерву её звуком сообщения в назначенный срок!'
        await state.set_state(states.Meditation.time)
        return dict(text=text, markup=markup)

    async def get_time(self, message, state):
        time_pattern = r'[+]?\d+$'

        if re.fullmatch(time_pattern, message.text):
            count = int(message.text)
            sec_count = 60 * count
            cnt = 0
            edit_message = await message.answer(text='Идёт медитация\n\n'
                                                     f'Выбранное время: {count} минут')

            for countdown in range(sec_count, 0, -1):
                mins, secs = divmod(countdown, 60)
                timer = '{:02d}:{:02d}'.format(mins, secs)
                time.sleep(1)
                await edit_message.edit_text(text='Идёт медитация\n\n'
                                                  f'Выбранное время: {count} мин.\n\n'
                                                  f'Оставшееся время: {timer}',
                                             reply_markup=markups.practice_stop_process(countdown))
            text = 'Практика окончена!'
            markup = markups.step_back_markup()
        else:
            text = 'Не похоже на количество минут. Введи любое целое число.'
            markup = markups.step_back_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def prana_name(self, message, state):
        markup = markups.back_markup()
        text = 'Введи навзвание пранаямы'
        await state.set_state(states.PranaYama.name)
        return dict(text=text, markup=markup)

    async def prana_time(self, message, state):
        async with state.proxy() as data:
            data['name'] = message.text
            markup = markups.step_back_markup()
            text = f'Введи время для упражнения {data["name"]}'
            await state.set_state(states.PranaYama.time)
        return dict(text=text, markup=markup)


    async def get_prana_time(self, message, state):
        time_pattern = r'[+]?\d+$'

        if re.fullmatch(time_pattern, message.text):
            async with state.proxy() as data:
                count = int(message.text)
                sec_count = 60 * count
                cnt = 0
                edit_message = await message.answer(text=f'Дышим пранаяму {data["name"]}\n\n'
                                                         f'Выбранное время: {count} минут')

                for countdown in range(sec_count, 0, -1):
                    mins, secs = divmod(countdown, 60)
                    timer = '{:02d}:{:02d}'.format(mins, secs)
                    time.sleep(1)
                    await edit_message.edit_text(text='Дышим пранаяму {data["name"]}\n\n'
                                                      f'Выбранное время: {count} мин.\n\n'
                                                      f'Оставшееся время: {timer}',
                                                 reply_markup=markups.practice_stop_process(countdown))
                text = 'Практика окончена!'
                markup = markups.step_back_markup()
        else:
            text = 'Не похоже на количество минут. Введи любое целое число.'
            markup = markups.step_back_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    #
    # async def enter_friend_data(self, state):
    #     markup = markups.back_markup()
    #     text = 'Введите уникальный 6-ти значный код друга:'
    #     await state.set_state(states.Friend.friend_id)
    #     return dict(text=text, markup=markup)
    #
    # async def search_friend(self, message, state):
    #     ids = self.db.get_ids()
    #     ids_lst = []
    #     for i in ids:
    #         for j in i:
    #             ids_lst.append(str(j))
    #     name_pattern = r'\d{6}$'
    #     if re.fullmatch(name_pattern, message.text) and message.text in ids_lst:
    #         async with state.proxy() as data:
    #             data['friend_id'] = message.text
    #             const.const.friend_id = message.text
    #             friend_data = self.db.get_friend_data(data['friend_id'])
    #             text = f'Этот пользователь Ваш друг?\n\n' \
    #                    f'Имя: {friend_data[0][0]}\n' \
    #                    f'Дата рождения: {friend_data[0][1]}\n' \
    #                    f'Номер телефона: {friend_data[0][2]}\n'
    #             markup = markups.yes_no()
    #     elif re.fullmatch(name_pattern, message.text) and message.text not in ids:
    #         text = 'Ваш друг не найден в нашей базе, либо Вы ввели неверный номер. Поторите ввод.'
    #         markup = markups.back_markup()
    #         await state.set_state(states.Friend.friend_id)
    #     else:
    #         text = 'Не похоже на ID. Повторите ввод.\nID состоит из 6 цифр!'
    #         markup = markups.back_markup()
    #         await state.set_state(states.Friend.friend_id)
    #     await state.finish()
    #     return dict(text=text, markup=markup)
    #
    # async def get_friend_wishes(self, message):
    #     wishlist = self.db.get_friend_wishes(friend_id=const.const.friend_id)
    #     for wish in wishlist:
    #         gift_id = wish.pop('id')
    #         wish['is_reserved'] = '🔒' if wish['is_reserved'] else '🆓'
    #         wish1 = [str(row) for row in wish.values() if row]
    #         wish1 = "\n".join(wish1)
    #         text = f'{wish1}'
    #         print(type(wish['name']), type(gift_id))
    #         book_gift_markup = markups.book_gift(wish_id=gift_id)
    #         await message.reply(text=text,
    #                             reply_markup=book_gift_markup,
    #                             parse_mode='HTML',
    #                             reply=False)
    #     markup = markups.back_markup()
    #     return dict(text='Бронируй подарок кнопки.', markup=markup)
    #
    # async def enter_fullname(self, state):
    #     markup = markups.back_markup()
    #     text = 'Введи имя и фамилию:'
    #     await state.set_state(states.User.fullname)
    #     return dict(text=text, markup=markup)
    #
    # async def get_name(self, message, state):
    #     name_pattern = r'[ёЁА-Яа-я- A-za-z]+'
    #     if re.fullmatch(name_pattern, message.text):
    #         async with state.proxy() as data:
    #             data['fullname'] = message.text
    #             text = f'Привет {data["fullname"]}. <b>Пожалуйста, введите вашу дату рождения.\nФормат для ввода даты ' \
    #                    f'рождения: ДД.ММ.ГГГГ </b>.'
    #         markup = markups.back_set_name_markup()
    #         await state.set_state(states.User.birthdate)
    #     elif message.text == 'Назад к вводу имени':
    #         markup = markups.back_markup()
    #         text = 'Введи имя и фамилию:'
    #         await state.set_state(states.User.fullname)
    #     else:
    #         text = 'Не похоже на ваше имя. Введите что-то более корректное (только буквы и дефис).'
    #         markup = None
    #     return dict(text=text, markup=markup)
    #
    # async def get_birthdate(self, message, state):
    #     date_pattern = r'.*'
    #     if message.text == 'Назад к вводу даты рождения':
    #         async with state.proxy() as data:
    #             text = f"<b>{data['fullname']}, пожалуйста повтори ввод даты рождения\nФормат ввода: ДД.ММ.ГГГГ</b>."
    #         markup = markups.back_set_name_markup()
    #         await state.set_state(states.User.birthdate)
    #     elif re.fullmatch(date_pattern, message.text):
    #         async with state.proxy() as data:
    #             try:
    #                 birthdate = datetime.strptime(message.text, r'%d.%m.%Y').date()
    #                 data['birthdate'] = birthdate
    #                 text = f'День твоего рождения: {data["birthdate"]}\n ' \
    #                        f'Красивое число, тебе повезло <b> \nПожалуйста, номер своего телефона...\nФормат ввода: ' \
    #                        f'79001112233</b>.'
    #                 markup = markups.back_set_birthdate_markup()
    #             except ValueError:
    #                 text = 'Не похоже на дату. Введите дату в формате ДД.ММ.ГГГГ'
    #                 markup = markups.back_set_name_markup()
    #                 await state.set_state(states.User.birthdate)
    #     await state.set_state(states.User.phone)
    #     return dict(text=text, markup=markup)
    #
    # async def get_phone(self, message, state):
    #     phone_pattern = r'^7\d{10}$'
    #     random_id = self.db.check_id()
    #     if message.text == 'Не хочу давать свой номер!':
    #         async with state.proxy() as data:
    #             data['phone'] = None
    #             data['id'] = random_id
    #             text = f"Твои данные приняты!\n\n {data['fullname']}\n " \
    #                    f"{data['birthdate']} \n\nТвой уникальный ID: {data['id']} \n\n" \
    #                    f" Перейти к созданию списка? Или вернуться к вводу номера телефона?"
    #
    #         await state.set_state(states.User.id)
    #         markup = markups.back_set_phone()
    #     elif re.fullmatch(phone_pattern, message.text):
    #         async with state.proxy() as data:
    #             data['phone'] = message.text
    #             data['id'] = random_id
    #             text = f"Твои данные приняты!\n\n {data['fullname']},\n{data['birthdate']}\n {data['phone']} \n\n " \
    #                    f"Твой уникальный ID: {data['id']} \n\n" \
    #                    f"Перейти к созданию списка? Или вернуться к вводу номера телефона?"
    #         await state.set_state(states.User.id)
    #         markup = markups.back_set_phone()
    #     elif message.text == 'Назад к вводу номера телефона':
    #         async with state.proxy() as data:
    #             text = f' {data["fullname"]}\n ' \
    #                    f'<b>Пожалуйста, повтори ввод номера телефона...</b>.'
    #         markup = markups.back_set_birthdate_markup()
    #         await state.set_state(states.User.phone)
    #     else:
    #         text = 'Не похоже на номер. Введите что-то более корректное (79998887766 ...).'
    #         markup = markups.back_set_birthdate_markup()
    #     return dict(text=text, markup=markup)
    #
    # async def add_user_to_db(self, message, state):
    #     async with state.proxy() as data:
    #         user_data = dict(
    #             id=data['id'],
    #             fullname=data['fullname'],
    #             birthdate=data['birthdate'],
    #             phone=data['phone'],
    #             tg_id=message.from_user.id,
    #             tg_nickname=message.from_user.username,
    #         )
    #         self.db.add_user(user_data=user_data)
    #     await state.finish()
    #
    # async def get_wishes(self, message, state):
    #     wishlist = self.db.get_wishes(tg_id=message.from_user.id)
    #     random_id = self.db.check_id()
    #     for wish in wishlist:
    #         gift_id = wish.pop('id')
    #         wish['is_reserved'] = '🔒' if wish['is_reserved'] else '🆓'
    #         wish1 = [str(row) for row in wish.values() if row]
    #         wish1 = "\n".join(wish1)
    #         text = f'{wish1}'
    #         print(type(wish['name']), type(gift_id))
    #         del_gift_markup = markups.del_gift(wish_id=gift_id)
    #         await message.reply(text=text,
    #                             reply_markup=del_gift_markup,
    #                             parse_mode='HTML',
    #                             reply=False)
    #     markup = markups.wishes_menu()
    #     return dict(text=f'Твой уникальный ID: {random_id}\n'
    #                      f'Вы можете добавить новый подарок используя кнопку ниже.', markup=markup)
    #
    # async def create_wish_list(self, state):
    #     text = 'Введите желание и я добавлю его в список подарков:'
    #     markup = markups.back_to_wishes_menu()
    #     await state.set_state(states.Gift.wish_name_to_add)
    #     return dict(text=text, markup=markup)
    #
    # async def add_point_in_list(self, message, state):
    #     wish_name = message.text
    #     tg_id = message.from_user.id
    #     wishlist_data = dict(
    #         name=wish_name,
    #         user_id=self.db.get_user_id(tg_id=tg_id)
    #     )
    #     self.db.add_gift(wishlist_data=wishlist_data)
    #     wishlist = self.db.get_wishes(tg_id=message.from_user.id)
    #     text = f'This is your wishlist:\n{wishlist}'
    #     for wish in wishlist:
    #         gift_id = wish.pop('id')
    #         wish['is_reserved'] = '🔒' if wish['is_reserved'] else '🆓'
    #         del_gift_markup = markups.del_gift(wish_id=gift_id)
    #         wish = [str(row) for row in wish.values() if row]
    #         text = "\n".join(wish)
    #         await message.reply(text=text,
    #                             reply_markup=del_gift_markup,
    #                             parse_mode='HTML',
    #                             reply=False)
    #     markup = markups.wishes_menu()
    #     await state.finish()
    #     return dict(text='Вы можете добавить новый подарок используя кнопку ниже.', markup=markup)
    #
    # async def del_point_from_list(self, query, wish_id):
    #     self.db.del_gift(gift_id=wish_id)
    #     wishlist = self.db.get_wishes(tg_id=query.from_user.id)
    #     for wish in wishlist:
    #         gift_id = wish.pop('id')
    #         wish['is_reserved'] = '🔒' if wish['is_reserved'] else '🆓'
    #         del_gift_markup = markups.del_gift(wish_id=gift_id)
    #         wish = [str(row) for row in wish.values() if row]
    #         text = "\n".join(wish)
    #         await self.bot.send_message(chat_id=query.from_user.id,
    #                                     text=text,
    #                                     reply_markup=del_gift_markup)
    #     markup = markups.wishes_menu()
    #     text = 'Подарок удален'
    #     return dict(text=text, markup=markup)
    #
    # async def book_point_from_list(self, query, wish_id):
    #     self.db.book_gift(gift_id=wish_id)
    #     wishlist = self.db.get_friend_wishes(const.const.friend_id)
    #     for wish in wishlist:
    #         gift_id = wish.pop('id')
    #         wish['is_reserved'] = '🔒' if wish['is_reserved'] else '🆓'
    #         book_gift_markup = markups.book_gift(wish_id=gift_id)
    #         wish = [str(row) for row in wish.values() if row]
    #         text = "\n".join(wish)
    #         await self.bot.send_message(chat_id=query.from_user.id,
    #                                     text=text,
    #                                     reply_markup=book_gift_markup)
    #     markup = back.markups()
    #     text = 'Подарок забронирован'
    #     return dict(text=text, markup=markup)
