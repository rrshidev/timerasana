'''async def meditation(self, message, state):
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
        return dict(text=text, markup=markup)'''


'''async def get_time(self, message, state):
        time_pattern = r'[+]?\d+$'
        user_message = message.text

        if re.fullmatch(time_pattern, message.text) and user_message != "Пауза" or "Возобновить":
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
        elif user_message == "Пауза" or "Возобновить":

            edit_message = await message.answer(text='Таймер на паузе.\n\n'
                                                     f'Оставшееся время время: {count} минут')
            
    '''








