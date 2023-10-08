from asyncio import exceptions
from datetime import datetime
from db.db_connector import Database
from . import markups
import re
import time
from . import states
import random
from sqlalchemy import DateTime
from .utils import get_callback
from .messages import timer_message
from . import memory
import asyncio
import const.const as const


class Controller:
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    async def command_start(self, message):
        name = message.from_user.first_name
        tg_id = message.from_user.id
        tg_nickname = message.from_user.username
        user_data = {
            'tg_id': tg_id,
            'name': name,
            'tg_nickname': tg_nickname
        }
        if self.db.is_user_exist(tg_id=message.from_user.id):
            markup = markups.start_markup()
            text = f'<b>Намаскар, {name}! Я таймер-бот для йогических практик!\n\n Рекомендую в настройках этого чата установить другую мелодию оповещения, чтобы ты мог отличать сообщения таймера от других по звуку и не отвлекался от практики!\n\n\nДА ПРИБУДЕТ С ТОБОЙ СИЛА!</b>'
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

# meditation
    async def meditation(self, message, state):
        markup = markups.step_back_markup()
        text = 'Введи количество минут для медитации и начинай практику.\n' \
               'Я прерву её звуком сообщения в назначенный срок!'
        await state.set_state(states.Meditation.time)
        return dict(text=text, markup=markup)

#get time for meditation and start practice!
    #async def get_time(self, message, state):
    async def get_time(self, message, count: int):
        print('test1', const.timer_paused, const.timer_stopped)
        sec_count = 60 * count
        
        while sec_count > 0:
            print('test:', sec_count, const.timer_paused, const.timer_stopped)
            if const.timer_stopped:
                break

            mins, secs = divmod(sec_count, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)

            if not const.timer_paused:        
                sec_count -= 1
                const.timer_rest = timer
                try:
                    await message.edit_text(
                        text=timer_message(total=count, rest=timer, status=not const.timer_paused),
                        reply_markup=markups.practice_stop_process(),
                    )
                except exceptions.MessageNotModified:
                    pass

            await asyncio.sleep(1)
        
        if const.timer_stopped:
            text = "Таймер остановлен!"
            markup = markups.choose_practice()
        if not const.timer_stopped:    
            print('test3', const.timer_paused, const.timer_stopped)
            text = 'Практика окончена!'
            markup = markups.step_back_markup()
            
        return await message.reply(text=text, reply_markup=markup)

    

#prana+get count
    async def pranayama(self, message, state):
        markup = markups.back_markup()
        text = 'Введи количество упражнений пранаямы'
        await state.set_state(states.PranaYama.count)
        return dict(text=text, markup=markup)


#get prana time
    async def prana_time(self, message, state):
        count_pattern = r'[+]?\d+$'
        if re.fullmatch(count_pattern, message.text):
            async with state.proxy() as data:    
                data['count'] = message.text
                markup = markups.step_back_markup()
                text = 'Введи количество минут на 1 упражнение:'
                await state.set_state(states.PranaYama.prana_time) 
        else:
            markup = markups.step_back_markup()
            text = 'Повтори ввод количества минут для пранаямы. \n\nДолжно быть целое число'
            await state.set_state(states.PranaYama.count)
        return dict(text=text, markup=markup)
 
 #get reload
    async def get_reload_time(self, message, state):
        prana_time_pattern = r'[+]?\d+$'
        if re.fullmatch(prana_time_pattern, message.text):
            async with state.proxy() as data:    
                data['prana_time'] = message.text
                markup = markups.step_back_markup()
                text = 'Введи количество секунд на перевод дыхания и отдых между пранаямами:'
                await state.set_state(states.PranaYama.reload)
        else:
            markup = markups.step_back_markup()
            text = 'Повтори ввод количества минут для пранаямы. \n\nДолжно быть целое число'
            await state.set_state(states.PranaYama.prana_time)
        return dict(text=text, markup=markup)

#get meditation time
    async def get_medidation_time(self, message, state):
        reload_pattern = r'[+]?\d+$'
        if re.fullmatch(reload_pattern, message.text):
            async with state.proxy() as data:    
                data['reload'] = message.text
                markup = markups.step_back_markup()
                text = 'Введи количество минут для медитации в конце пранаямы:'
                await state.set_state(states.PranaYama.meditation_time)
        else:
            markup = markups.step_back_markup()
            text = 'Повтори ввод количества секунд для перевода дыхания и отдыха. \n\nДолжно быть целое число'
            await state.set_state(states.PranaYama.reload)
        return dict(text=text, markup=markup)
    
#start pranayama
    async def practice_time(self, message, state):
        name = message.from_user.first_name
        tg_id = message.from_user.id
        meditaion_time_pattern = r'[+]?\d+$'
        if re.fullmatch(meditaion_time_pattern, message.text):
            async with state.proxy() as data:   
                data['meditation_time'] = message.text
                prana_data = {
                    'tg_id': tg_id,
                    'name': name,
                    'count': data['count'],
                    'prana_time': data['prana_time'],
                    'reload': data['reload'],
                    'meditation_time': data['meditation_time'],
                }
                self.db.add_prana_data(prana_data=prana_data)
                count = int(data['count']) 
                prana_time = int(data['prana_time']) * 60
                reload_time = int(data['reload'])
                meditation_time = int(data['meditation_time']) *60  
                cnt = 0
                for i in range(0, count):
                    cnt += 1
                    edit_message = await message.answer(text=f'Идёт практика прнаямы: упражнение №{cnt}')

                    for countdown in range(prana_time, 0, -1):
                        mins, secs = divmod(countdown, 60)
                        timer = '{:02d}:{:02d}'.format(mins, secs)
                        time.sleep(1)
                        await edit_message.edit_text(text=f'Идёт практика прнаямы: упражнение №{cnt}\n\nОставшееся время: {timer}',
                                                    reply_markup=markups.practice_stop_process())
                    if cnt != count:
                        for countdown in range(reload_time, 0, -1):
                            mins, secs = divmod(countdown, 60)
                            timer = '{:02d}:{:02d}'.format(mins, secs)
                            time.sleep(1)
                            await edit_message.edit_text(text=f'Отдохни! Переведи дух! Сконцентрируйте в одной точке!\
                                                        Оставшееся время отдыха: {timer}',
                                                        reply_markup=markups.practice_stop_process())
                    else:
                        for countdown in range(meditation_time, 0, -1):
                            mins, secs = divmod(countdown, 60)
                            timer = '{:02d}:{:02d}'.format(mins, secs)
                            time.sleep(1)
                            await edit_message.edit_text(text=f'Медитация... иди на свет... Ом... \
                                                        Оставшееся время Шавасаны: {timer}',
                                                        reply_markup=markups.practice_stop_process())    

            text = 'Практика окончена!'
            markup = markups.step_back_markup()
        else:
            text = 'Не похоже на количество минут. Введи любое целое число.'
            markup = markups.step_back_markup()
            await state.set_state(states.PranaYama.meditation_time)
        await state.finish()
        return dict(text=text, markup=markup)

    
    
    
   #asana
   
    async def asana(self, message, state):
        markup = markups.step_back_markup()
        text = 'Введи количество асан в твоём комплексе:'
        await state.set_state(states.Asana.count)
        return dict(text=text, markup=markup)
   
   #get asana time 
    async def get_asana_time(self, message, state):
        count_pattern = r'[+]?\d+$'
        async with state.proxy() as data:
            if re.fullmatch(count_pattern, message.text):
                async with state.proxy() as data:    
                    data['count'] = message.text
                    markup = markups.step_back_markup()
                    text = 'Введи количество минут в асане:'
                    await state.set_state(states.Asana.asana_time)
                
            else:
                markup = markups.step_back_markup()
                text = 'Повтори ввод количества асан.\n\nДолжно быть целое число!'
                await state.set_state(states.Asana.count)
        return dict(text=text, markup=markup)
  
    #get relax time
    async def get_relax_time(self, message, state):
        asana_time_pattern = r'[+]?\d+$'
        async with state.proxy() as data:
            if re.fullmatch(asana_time_pattern, message.text):
                async with state.proxy() as data:    
                    data['asana_time'] = message.text
                    markup = markups.step_back_markup()
                    text = 'Введи количество минут для отдыха между асанами:'
                    await state.set_state(states.Asana.relax_time)
                    
            else:
                markup = markups.step_back_markup()
                text = 'Повтори ввод количества минут для асаны. \n\nДолжно быть целое число'
                await state.set_state(states.Asana.asana_time)
        return dict(text=text, markup=markup)
    

    #get shavasana time
    async def get_shavasana_time(self, message, state):
        relax_time_pattern = r'[+]?\d+$'
        if re.fullmatch(relax_time_pattern, message.text):
            async with state.proxy() as data:    
                data['relax_time'] = message.text
                markup = markups.step_back_markup()
                text = 'Введи количество минут для шавасаны в конце конце комплекса:'
                await state.set_state(states.Asana.shavasana_time)  
        else:
            markup = markups.step_back_markup()
            text = 'Повтори ввод количества минут для отдыха между асанами. \n\nДолжно быть целое число'
            await state.set_state(states.Asana.relax_time)
        return dict(text=text, markup=markup)
            
    async def startasana(self, message, state):
        name = message.from_user.first_name
        tg_id = message.from_user.id
        shavasana_time_pattern = r'[+]?\d+$'
        if re.fullmatch(shavasana_time_pattern, message.text):
            async with state.proxy() as data:   
                data['shavasana_time'] = message.text
                asana_data = {
                    'tg_id': tg_id,
                    'name': name,
                    'count': data['count'],
                    'asana_time': data['asana_time'],
                    'relax_time': data['relax_time'],
                    'shavasana_time': data['shavasana_time'],
                }
                self.db.add_asana_data(asana_data=asana_data)
                count = int(data['count'])
                asana_time = int(data['asana_time']) * 60
                relax_time = int(data['relax_time']) * 60
                shavasana_time = int(data['shavasana_time']) * 60
                cnt = 0
                for i in range(0, count):
                    cnt += 1
                    edit_message = await message.answer(text=f'Идёт практика асаны: позиция № {cnt}')

                    for countdown in range(asana_time, 0, -1):
                        mins, secs = divmod(countdown, 60)
                        timer = '{:02d}:{:02d}'.format(mins, secs)
                        time.sleep(1)
                        await edit_message.edit_text(text=f'Идёт практика асаны: позиция № {cnt}\n\nОставшееся время в асане: {timer}',
                                                    reply_markup=markups.practice_stop_process())
                    if cnt != count:
                        for countdown in range(relax_time, 0, -1):
                            mins, secs = divmod(countdown, 60)
                            timer = '{:02d}:{:02d}'.format(mins, secs)
                            time.sleep(1)
                            await edit_message.edit_text(text=f'Отдохни! Сделай компенацию или Шавасану\
                                                        Оставшееся время отдыха: {timer}',
                                                        reply_markup=markups.practice_stop_process())
                    else:
                        for countdown in range(shavasana_time, 0, -1):
                            mins, secs = divmod(countdown, 60)
                            timer = '{:02d}:{:02d}'.format(mins, secs)
                            time.sleep(1)
                            await edit_message.edit_text(text=f'Практика Шавасаны! \
                                                        Оставшееся время Шавасаны: {timer}',
                                                        reply_markup=markups.practice_stop_process())    

            text = 'Практика окончена! Намаскар!'
            markup = markups.step_back_markup()
        else:
            text = 'Не похоже на количество минут. Введи любое целое число.'
            markup = markups.step_back_markup()
            await state.set_state(states.Asana.shavasana_time)
        await state.finish()
        return dict(text=text, markup=markup)






'''work peace of code for meditaion

            count = int(message.text)
            sec_count = 60 * count
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
            await state.set_state(states.Meditation.time)
        await state.finish()
        return dict(text=text, markup=markup)
'''

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
